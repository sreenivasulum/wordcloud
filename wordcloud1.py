from flask import Flask, request, jsonify
from flask_cors import CORS
#import matplotlib.pyplot as plt
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
    static_folder = os.path.join(app.root_path, 'static')
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)
    filepath = os.path.join(static_folder, filename)
    wordcloud.to_file(filepath)
    logging.debug("Wordcloud saved to %s", filepath)
    return filepath

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

        wordcloud_filepath = generate_wordcloud(tweet_texts)
        wordcloud_url = f"/static/{os.path.basename(wordcloud_filepath)}"
        return jsonify({"wordcloud_url": wordcloud_url, "tweets": tweet_texts})
    except Exception as e:
        logging.exception("An error occurred while processing the request")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
