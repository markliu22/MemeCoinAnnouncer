import os
from flask import Flask, request, jsonify
import tweepy
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
import threading
from config import *


app = Flask(__name__)

# Twitter API
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
twitter_api = tweepy.API(auth)

# Format: {"email": ..., "phone": ..., "notification_type": ...}
subscribers = []

# X users to track
users_to_track = []

# Load users to track from a file
def load_users_to_track():
    global users_to_track
    try:
        with open("users_to_track.txt", "r") as f:
            users_to_track = [line.strip() for line in f if line.strip()]
        print(f"Tracking {len(users_to_track)} users.")
    except FileNotFoundError:
        print("No users_to_track.txt file found. Starting with an empty list.")

# Send SMS notifications
def send_sms(to, message):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=message, from_=TWILIO_PHONE_NUMBER, to=to)
        print(f"SMS sent to {to}")
    except Exception as e:
        print(f"Failed to send SMS to {to}: {e}")

# Send email notifications
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
        print(f"Email sent to {to}")
    except Exception as e:
        print(f"Failed to send email to {to}: {e}")

# Notify subscribers
def notify_subscribers(message):
    global subscribers
    for subscriber in subscribers:
        if subscriber.get("notification_type") == "sms" and subscriber.get("phone"):
            send_sms(subscriber["phone"], message)
        elif subscriber.get("notification_type") == "email" and subscriber.get("email"):
            send_email(subscriber["email"], "New Tweet Alert", message)

# Monitor tweets from specific users
def monitor_users():
    # TODO

@app.route('/')
def home():
    return "Twitter Tracker is running!"

if __name__ == '__main__':
    # Load tracked users and start monitoring in a thread
    load_users_to_track()
    threading.Thread(target=monitor_users).start()

    # Start Flask server
    app.run(host="0.0.0.0", port=5000)
