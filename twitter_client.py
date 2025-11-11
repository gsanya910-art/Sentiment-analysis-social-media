
import requests
import pandas as pd
import base64
import json
from config import TWITTER_CONFIG

class TwitterClient:
    def __init__(self):
        self.consumer_key = TWITTER_CONFIG['consumer_key']
        self.consumer_secret = TWITTER_CONFIG['consumer_secret']
        self.access_token = TWITTER_CONFIG['access_token']
        self.access_token_secret = TWITTER_CONFIG['access_token_secret']
        self.bearer_token = self.get_bearer_token()
    
    def get_bearer_token(self):
        """Get bearer token using app credentials"""
        try:
            # Encode credentials
            credentials = f"{self.consumer_key}:{self.consumer_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            # Get bearer token
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            }
            data = {'grant_type': 'client_credentials'}
            
            response = requests.post(
                'https://api.twitter.com/oauth2/token',
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                return response.json()['access_token']
            else:
                print(f"Error getting bearer token: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error in get_bearer_token: {e}")
            return None
    
    def search_tweets(self, keyword, count=100):
        """Search for tweets using Twitter API v2"""
        if not self.bearer_token:
            print("No bearer token available. Using mock data.")
            return self.get_mock_tweets(keyword, count)
        
        try:
            headers = {
                'Authorization': f'Bearer {self.bearer_token}'
            }
            
            params = {
                'query': f'{keyword} -is:retweet lang:en',
                'max_results': min(count, 100),
                'tweet.fields': 'created_at,public_metrics,author_id',
                'user.fields': 'username',
                'expansions': 'author_id'
            }
            
            response = requests.get(
                'https://api.twitter.com/2/tweets/search/recent',
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                tweets = []
                
                if 'data' in data:
                    users = {user['id']: user['username'] for user in data.get('includes', {}).get('users', [])}
                    
                    for tweet in data['data']:
                        tweets.append({
                            'id': tweet['id'],
                            'text': tweet['text'],
                            'created_at': tweet['created_at'],
                            'user': users.get(tweet['author_id'], 'unknown'),
                            'retweets': tweet['public_metrics']['retweet_count'],
                            'favorites': tweet['public_metrics']['like_count']
                        })
                
                return pd.DataFrame(tweets)
            else:
                print(f"Error fetching tweets: {response.status_code} - {response.text}")
                print("Using mock data instead.")
                return self.get_mock_tweets(keyword, count)
        
        except Exception as e:
            print(f"Error in search_tweets: {e}")
            print("Using mock data instead.")
            return self.get_mock_tweets(keyword, count)

    def get_mock_tweets(self, keyword, count=10):
        """Generate mock tweet data for testing"""
        import datetime
        mock_tweets = [
            {
                'id': f'mock_{i}',
                'text': f'This is a mock tweet about {keyword}. It is great! #{keyword}',
                'created_at': datetime.datetime.now().isoformat(),
                'user': f'user_{i}',
                'retweets': i * 2,
                'favorites': i * 3
            }
            for i in range(count)
        ]
        # Add some variety to sentiments
        mock_tweets[1]['text'] = f'Not happy with {keyword}. Poor quality!'
        mock_tweets[2]['text'] = f'{keyword} is okay, nothing special.'
        mock_tweets[3]['text'] = f'Loving the new {keyword} features! Amazing work!'
        mock_tweets[4]['text'] = f'Disappointed with {keyword} service. Very bad experience.'
        
        return pd.DataFrame(mock_tweets)