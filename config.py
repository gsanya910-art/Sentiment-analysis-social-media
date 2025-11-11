import os
from dotenv import load_dotenv

load_dotenv()

# Twitter API Configuration
TWITTER_CONFIG = {
    'consumer_key': os.getenv('TWITTER_CONSUMER_KEY'),
    'consumer_secret': os.getenv('TWITTER_CONSUMER_SECRET'),
    'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
    'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
}

# Model Configuration
MODEL_CONFIG = {
    'max_tweets': 100,
    'sentiment_threshold': 0.1
}