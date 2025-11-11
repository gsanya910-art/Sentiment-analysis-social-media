from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime
import json

from twitter_client import TwitterClient
from sentiment_model import analyzer
from config import MODEL_CONFIG

app = Flask(__name__)
CORS(app)

# Initialize clients
twitter_client = TwitterClient()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/analyze/sentiment', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment of provided text"""
    data = request.get_json()
    text = data.get('text', '')
    method = data.get('method', 'bert')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    sentiment = analyzer.predict_sentiment(text, method)
    
    return jsonify({
        'text': text,
        'sentiment': sentiment,
        'method': method
    })

@app.route('/api/twitter/sentiment', methods=['GET'])
def analyze_twitter_sentiment():
    """Analyze sentiment of tweets for a given keyword"""
    keyword = request.args.get('keyword', '')
    count = int(request.args.get('count', MODEL_CONFIG['max_tweets']))
    method = request.args.get('method', 'bert')
    
    if not keyword:
        return jsonify({'error': 'No keyword provided'}), 400
    
    # Fetch tweets
    tweets_df = twitter_client.search_tweets(keyword, count)
    
    if tweets_df.empty:
        return jsonify({'error': 'No tweets found or API error'}), 404
    
    # Analyze sentiment for each tweet
    sentiments = []
    for text in tweets_df['text']:
        sentiment = analyzer.predict_sentiment(text, method)
        sentiments.append(sentiment)
    
    tweets_df['sentiment'] = sentiments
    
    # Calculate statistics
    sentiment_counts = tweets_df['sentiment'].value_counts().to_dict()
    total_tweets = len(tweets_df)
    
    sentiment_stats = {
        'positive_percentage': (sentiment_counts.get('positive', 0) / total_tweets) * 100,
        'negative_percentage': (sentiment_counts.get('negative', 0) / total_tweets) * 100,
        'neutral_percentage': (sentiment_counts.get('neutral', 0) / total_tweets) * 100,
        'total_tweets': total_tweets
    }
    
    # Prepare response
    response = {
        'keyword': keyword,
        'statistics': sentiment_stats,
        'tweets': tweets_df.to_dict('records'),
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(response)

@app.route('/api/twitter/trends', methods=['GET'])
def get_sentiment_trends():
    """Get sentiment trends over time for dashboard"""
    keyword = request.args.get('keyword', '')
    
    if not keyword:
        return jsonify({'error': 'No keyword provided'}), 400
    
    tweets_df = twitter_client.search_tweets(keyword, 50)
    
    if tweets_df.empty:
        return jsonify({'error': 'No tweets found'}), 404
    
    # Analyze sentiment
    sentiments = []
    for text in tweets_df['text']:
        sentiment = analyzer.predict_sentiment(text)
        sentiments.append(sentiment)
    
    tweets_df['sentiment'] = sentiments
    
    # Group by time and sentiment (simplified)
    trends_data = {
        'hourly_sentiment': [
            {'hour': '00:00', 'positive': 5, 'negative': 2, 'neutral': 3},
            {'hour': '01:00', 'positive': 4, 'negative': 1, 'neutral': 5},
            {'hour': '02:00', 'positive': 6, 'negative': 3, 'neutral': 1},
        ],
        'current_sentiment': tweets_df['sentiment'].value_counts().to_dict(),
        'sample_tweets': tweets_df.head(10).to_dict('records')
    }
    
    return jsonify(trends_data)

if __name__ == '__main__':
    print("Starting Sentiment Analysis Backend...")
    print("Available endpoints:")
    print("  GET  /api/health")
    print("  POST /api/analyze/sentiment")
    print("  GET  /api/twitter/sentiment?keyword=<keyword>")
    print("  GET  /api/twitter/trends?keyword=<keyword>")
    
    app.run(debug=True, host='0.0.0.0', port=5001)