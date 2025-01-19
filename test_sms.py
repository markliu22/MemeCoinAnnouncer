from twilio.rest import Client

from config import * 

TO_PHONE_NUMBER = "+16479990000"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms(message):
    try:
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=TO_PHONE_NUMBER
        )
        print(f"Message sent: SID {message.sid}")
    except Exception as e:
        print(f"Failed to send message: {e}")

# Test
send_sms("Hello buddy!")
# "Sent from your Twilio trial account - Hello buddy!"