import os
import asyncio
from flask import Flask, jsonify
from twikit import Client
from twilio.rest import Client as TwilioClient
import smtplib
from email.mime.text import MIMEText
import threading
from config import *
import time


app = Flask(__name__)

# Twikit twitter client
twitter_client = Client("en-US")

# Format: {"email": ..., "phone": ..., "notification_type": ...}
subscribers = []

# Twitter users to track
users_to_track = []

# Load users to track from local file
def load_users_to_track():
    global users_to_track
    try:
        with open("users_to_track.txt", "r") as f:
            users_to_track = [line.strip() for line in f if line.strip()]
        print(f"[INFO] Tracking {len(users_to_track)} users.")
    except FileNotFoundError:
        print("[WARNING] No users_to_track.txt file found. Starting with an empty list.")

# Send SMS notification
def send_sms(to, message):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=message, from_=TWILIO_PHONE_NUMBER, to=to)
        print(f"[INFO] SMS sent to {to}: {message}")
    except Exception as e:
        print(f"[ERROR] Failed to send SMS to {to}: {e}")

# Send email notification
def send_email(to, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls() # TLS encryption
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to, msg.as_string())
        print(f"[INFO] Email sent to {to}: Subject={subject}")
    except Exception as e:
        print(f"[ERROR] Failed to send email to {to}: {e}")

# Notify subscribers
def notify_subscribers(message):
    global subscribers
    if not subscribers:
        print("[WARNING] No subscribers to notify.")
        return

    for subscriber in subscribers:
        if subscriber.get("notification_type") == "sms" and subscriber.get("phone"):
            send_sms(subscriber["phone"], message)
        elif subscriber.get("notification_type") == "email" and subscriber.get("email"):
            send_email(subscriber["email"], "New Tweet Alert", message)

# Monitor tweets from specified users
async def monitor_users():
    global users_to_track
    
    # Rate limit calculations
    RATE_LIMIT_REQUESTS = 50  # Requests allowed per 15-min window https://github.com/d60/twikit/blob/main/ratelimits.md
    RATE_LIMIT_WINDOW = 15 * 60  # 15 minutes in seconds
    USERS_COUNT = len(users_to_track)
    
    # Calculate optimal delay between users
    # Adding 10% buffer for safety
    DELAY_BETWEEN_USERS = (RATE_LIMIT_WINDOW / RATE_LIMIT_REQUESTS) * 1.1  # ~19.8 seconds
    
    base_delay = RATE_LIMIT_WINDOW / RATE_LIMIT_REQUESTS  # ~18 seconds
    max_delay = 3600  # Max delay 1 hour
    current_delay = base_delay
    
    print(f"[INFO] Monitoring {USERS_COUNT} users")
    print(f"[INFO] Delay between users: {DELAY_BETWEEN_USERS:.2f}s")
    print(f"[INFO] Complete cycle time: {(DELAY_BETWEEN_USERS * USERS_COUNT)/60:.2f} minutes")
    
    try:
        await twitter_client.login(
            auth_info_1=TWITTER_USERNAME,
            auth_info_2=TWITTER_EMAIL,
            password=TWITTER_PASSWORD,
        )
        print("[INFO] Successfully logged into Twikit.")
        
        while True:
            cycle_start_time = time.time()
            
            for username in users_to_track:
                try:
                    print(f"[INFO] Fetching tweets for @{username}...")
                    user = await twitter_client.get_user_by_screen_name(username)
                    user_id = user.id
                    tweets = await twitter_client.get_user_tweets(user_id, "Tweets", count=20)
                    
                    # Reset delay on successful request
                    current_delay = base_delay
                    
                    for tweet in tweets:
                        # Look for token symbols ($XXX pattern)
                        words = tweet.text.split()
                        tokens = [word for word in words if word.startswith('$') and len(word) > 1 and word[1:].isupper()]
                        if tokens:
                            message = f"🚀 @{username} mentioned tokens {', '.join(tokens)}: {tweet.text}"
                            print(f"[INFO] Found token mention: {tweet.text}")
                            notify_subscribers(message)
                    
                    await asyncio.sleep(DELAY_BETWEEN_USERS)
                    
                except Exception as e:
                    if "Rate limit exceeded" in str(e):
                        print(f"[WARNING] Rate limit hit, backing off for {current_delay} seconds...")
                        await asyncio.sleep(current_delay)
                        current_delay = min(current_delay * 2, max_delay)
                    else:
                        print(f"[ERROR] Failed to fetch tweets for @{username}: {e}")
                        await asyncio.sleep(5)
            
            cycle_end_time = time.time()
            cycle_duration = cycle_end_time - cycle_start_time
            print(f"[INFO] Completed cycle in {cycle_duration/60:.2f} minutes")
            
    except Exception as e:
        print(f"[ERROR] Failed to monitor users: {e}")
        await asyncio.sleep(current_delay)
        await monitor_users()

@app.route('/')
def home():
    return "Twitter Tracker is running!"

if __name__ == "__main__":
    # Load tracked users and start monitoring in a thread
    print("[INFO] Loading users to track...")
    load_users_to_track()

    # Run Twikit in an asyncio thread
    def start_monitoring():
        asyncio.run(monitor_users())

    print("[INFO] Starting monitoring thread...")
    threading.Thread(target=start_monitoring).start()

    # Start Flask server
    print("[INFO] Starting Flask server on port 5001...")
    app.run(host="0.0.0.0", port=5001)