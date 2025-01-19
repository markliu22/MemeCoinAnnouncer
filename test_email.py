import smtplib
from email.mime.text import MIMEText
from config import * 

def send_email(to, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # TLS encryption
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to, msg.as_string())
        print(f"Email sent to {to}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Test
send_email("memecoinannouncer@gmail.com", "Test Email", "This is a test email from Memecoin Notifier.")
