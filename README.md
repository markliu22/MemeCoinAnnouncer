# Celebrity Memecoin Alert 🚀

# Subscribe Here: 
https://memecoinannouncer.com

## Introduction
It seems I'm always late to hear about these celebrity meme coins. By the time I hear about them, it's already too late.
It would be nice to know about them right when they're announced without constantly checking online. This way, I can buy and sell a little bit before any potential rug pull.

This app monitors tweets from the most popular X (Twitter) users and notifies subscribers via email/text if the tweet contains an announcement of a new cryptocurrency (looking for $TOKEN patterns).

## Example
![Text Message Notification Example](assets/text_demo.png)

# To Run Locally:

## Features
- Monitors tweets from top Twitter/X users in real-time
- Detects cryptocurrency token mentions ($TOKEN pattern)
- Supports both email and SMS notifications
- Rate limit handling with exponential backoff
- Easy to subscribe to notifications

### Prerequisites
- Python 3.8+
- Node.js 18+
- Twitter/X account credentials
- Twilio account (for SMS notifications)
- Gmail account (for email notifications)
- Cohere API key (for AI-powered tweet analysis)

### Backend Setup

1. Clone the repository
```
git clone https://github.com/markliu22/MemeCoinAnnouncer.git
```
```
cd MemeCoinAnnouncer
```

2. Create and activate a virtual environment
```
python -m venv venv
```
```
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies
```
pip install -r requirements.txt
```

4. Set up your credentials
- Fill in your credentials in `app.py`:
  - Twitter/X account details
  - Twilio credentials (for SMS)
  - Gmail credentials (for email). Note, do not put your Gmail password in the file. Instead, generate an app password for your Gmail account and put that for the password.
  - Cohere API key

5. Review users to track
- Check `users_to_track.txt` for the list of X (Twitter) users to monitor
- Add or remove usernames as needed

6. Start the Flask backend
```
python app.py
```

The backend will run on http://localhost:5001

### Frontend Setup

1. Navigate to the frontend directory
```
cd memecoin-announcer
```

2. Install Node dependencies
```
npm install
```

3. Start the development server
```
npm run dev
```

The frontend will run on http://localhost:5173

### Usage

1. Open http://localhost:5173 in your browser
2. Subscribe with your email and/or phone number
3. You'll receive notifications when tracked celebrities/influencers mention new tokens in their tweets