import os
import asyncio
from flask import Flask, jsonify, request
from twikit import Client
from twilio.rest import Client as TwilioClient
import smtplib
from email.mime.text import MIMEText
import threading
# from config import *
import time
from database import Database, Subscriber
from flask_cors import CORS
import cohere
from typing import Optional

# Add environment variable access
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_EMAIL = os.getenv('TWITTER_EMAIL')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))  # Default to 587 if not set
COHERE_API_KEY = os.getenv('COHERE_API_KEY')

users_file = "users_to_track.txt"

app = Flask(__name__)
CORS(app)

# Twikit twitter client
twitter_client = Client("en-US")

# Initialize database
db = Database()

# Format: {"email": ..., "phone": ..., "notification_type": ...}
subscribers = []
# subscribers = [
#     {
#         "email": "example@gmail.com",
#         "phone": "+16479990000",
#         "notification_type": "sms"
#     }
# ]

# Twitter users to track
users_to_track = []

# Load users to track from local file
def load_users_to_track():
    global users_to_track
    try:
        with open(users_file, "r") as f:
            users_to_track = [line.strip() for line in f if line.strip()]
        print(f"[INFO] Tracking {len(users_to_track)} users.")
    except FileNotFoundError:
        print("[WARNING] No users_to_track.txt file found. Starting with an empty list.")

# Send SMS notification
def send_sms(to, message):
    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
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
async def notify_subscribers(message: str):
    subscribers = db.get_all_active_subscribers()
    
    for subscriber in subscribers:
        if subscriber.email:
            try:
                send_email(subscriber.email, "New Memecoin Alert! 🚀", message)
            except Exception as e:
                print(f"Failed to send email to {subscriber.email}: {e}")
                
        if subscriber.phone:
            try:
                send_sms(subscriber.phone, message)
            except Exception as e:
                print(f"Failed to send SMS to {subscriber.phone}: {e}")

async def check_crypto_announcement(tweet_text: str) -> Optional[bool]:
    """
    Use Cohere LLM to check if a tweet is announcing a cryptocurrency.
    Returns True if it's a crypto announcement, False if not, None if error.
    """
    try:
        co = cohere.ClientV2(COHERE_API_KEY)
        
        prompt = f"""Analyze this tweet and determine if it's announcing a new cryptocurrency or token.
        Only respond with 'yes' if it's clearly announcing a new cryptocurrency/token, otherwise respond with 'no'.
        
        Tweet: {tweet_text}
        
        Answer with only 'yes' or 'no':"""
        
        response = co.chat(
            model="command-r-plus",
            messages=[{"role": "user", "content": prompt}]
        )
        
        answer = response.message.text.strip().lower()
        return answer == "yes"
        
    except Exception as e:
        print(f"[WARNING] Cohere API error: {e}")
        return None

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
                        # print(f"\n[DEBUG] Processing tweet: {tweet.text}")
                        
                        # Look for token symbols ($XXX pattern)
                        words = tweet.text.split()
                        tokens = [word for word in words if word.startswith('$') and len(word) > 1]
                        
                        if tokens:
                            # print(f"[DEBUG] Found ${tokens} pattern in tweet!")
                            print(f"[INFO] Making request to Cohere to analyze: {tweet.text}")
                            
                            # Try to verify if it's a crypto announcement using Cohere
                            is_crypto = await check_crypto_announcement(tweet.text)
                            # print(f"[DEBUG] Cohere analysis result: {is_crypto}")
                            
                            # If Cohere fails or confirms it's a crypto announcement, proceed with notification
                            if is_crypto is None or is_crypto:
                                message = f"🚀 @{username} mentioned tokens {', '.join(tokens)}: {tweet.text}"
                                print(f"[INFO] Found token mention: {tweet.text}")
                                if is_crypto is True:
                                    print("[INFO] Cohere confirmed this is likely a crypto announcement!")
                                    message = "🚨 LIKELY CRYPTO ANNOUNCEMENT 🚨\n" + message
                                await notify_subscribers(message)
                        # else:
                        #     print("[DEBUG] No $TOKEN patterns found in this tweet")
                    
                    await asyncio.sleep(DELAY_BETWEEN_USERS) # avoid rate limiting
                    
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

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    email = data.get('email')
    phone = data.get('phone')
    
    if not email and not phone:
        return jsonify({'error': 'Email or phone required'}), 400
        
    success = db.add_subscriber(email=email, phone=phone)
    if success:
        return jsonify({'message': 'Subscription successful'}), 200
    else:
        return jsonify({'error': 'Subscription failed'}), 400

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.json
    email = data.get('email')
    phone = data.get('phone')
    
    if not email and not phone:
        return jsonify({'error': 'Email or phone required'}), 400
        
    success = db.deactivate_subscriber(email=email, phone=phone)
    if success:
        return jsonify({'message': 'Unsubscription successful'}), 200
    else:
        return jsonify({'error': 'Unsubscription failed'}), 400

@app.route('/subscribers', methods=['GET'])
def get_subscribers():
    subscribers = db.get_all_active_subscribers()
    return jsonify({
        'subscribers': [
            {
                'id': sub.id,
                'email': sub.email,
                'phone': sub.phone,
                'is_active': sub.is_active
            } for sub in subscribers
        ]
    })

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