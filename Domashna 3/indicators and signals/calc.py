from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)


# Utility Functions for Market Analysis

def compute_rsi(data, window=14):
    delta = data['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def compute_moving_avg(data, window=10):
    return data['close'].rolling(window=window).mean()


def generate_market_signal(data):
    rsi = compute_rsi(data).iloc[-1]
    if rsi < 30:
        return "BUY"
    elif rsi > 70:
        return "SELL"
    else:
        return "HOLD"


# Sentiment Analysis Utilities

def fetch_latest_news(stock_symbol):
    url = f"https://example.com/news/{stock_symbol}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = soup.find_all("p")
        return " ".join([headline.text for headline in headlines if stock_symbol in headline.text])
    return "No relevant news found."


def analyze_article_sentiment(content):
    analyzer = SentimentIntensityAnalyzer()
    return analyzer.polarity_scores(content)['compound']


@app.route("/market_signal", methods=["POST"])
def market_signal():
    data = pd.DataFrame(request.json)
    signal = generate_market_signal(data)
    return jsonify({"signal": signal})


@app.route("/news_sentiment", methods=["GET"])
def news_sentiment():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"error": "Stock symbol is required"}), 400

    news = fetch_latest_news(symbol)
    sentiment_score = analyze_article_sentiment(news)
    recommendation = "BUY" if sentiment_score > 0.05 else "SELL" if sentiment_score < -0.05 else "HOLD"

    return jsonify({
        "symbol": symbol,
        "news": news,
        "sentiment_score": sentiment_score,
        "recommendation": recommendation
    })


if __name__ == "__main__":
    app.run(debug=True)
