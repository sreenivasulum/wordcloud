from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from wordcloud import WordCloud
import os
import uuid
import logging

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def generate_wordcloud(tweets):
    logging.debug("Generating wordcloud for tweets: %s", tweets)
    text = ' '.join(tweets)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    filename = f"{uuid.uuid4()}.png"
    filepath = os.path.join('static', filename)
    wordcloud.to_file(filepath)
    logging.debug("Wordcloud saved to %s", filepath)
    return filename

@app.route('/home')
def hello_twitter():
    return 'Hello Twitter'

@app.route('/extract', methods=['POST'])
def extract_tweets():
    try:
        data = request.json
        logging.debug("Received data: %s", data)
        tweets = data.get('tweets', [])
        if not tweets:
            return jsonify({"error": "No tweets provided"}), 400

        # Extract text from tweet objects
        tweet_texts = [tweet if isinstance(tweet, str) else tweet.get('text', '') for tweet in tweets]
        if not all(isinstance(text, str) for text in tweet_texts):
            return jsonify({"error": "Invalid tweet data"}), 400

        filename = generate_wordcloud(tweet_texts)
        wordcloud_url = f"/static/{filename}"
        return jsonify({"wordcloud_url": wordcloud_url, "tweets": tweet_texts})
    except Exception as e:
        logging.exception("An error occurred while processing the request")
        return jsonify({"error": str(e)}), 500

# Serve static files (word cloud images)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)
