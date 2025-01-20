import asyncio
from twikit import Client
from config import *

# Initialize Twikit client
client = Client('en-US')

async def fetch_latest_tweets(screen_name):
    try:
        # Log in to Twikit
        await client.login(
            auth_info_1=TWITTER_USERNAME,
            auth_info_2=TWITTER_EMAIL,
            password=TWITTER_PASSWORD
        )

        # Get user details by screen name
        user = await client.get_user_by_screen_name(screen_name)
        user_id = user.id
        print(f"Fetching tweets for @{screen_name} (User ID: {user_id})")

        # Fetch latest tweets (up to 20 by default)
        tweets = await client.get_user_tweets(user_id, 'Tweets', count=20)

        # Print tweets
        for tweet in tweets:
            print(f"Tweet ID: {tweet.id}")
            print(f"Content: {tweet.text}")
            print(f"Created At: {tweet.created_at}")
            print("-" * 40)

    except Exception as e:
        print(f"Error fetching tweets for @{screen_name}: {e}")

# Run the fetch_latest_tweets function
screen_name_to_fetch = 'elonmusk'  # Replace with the Twitter screen name to track
asyncio.run(fetch_latest_tweets(screen_name_to_fetch))
