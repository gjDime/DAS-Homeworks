from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(df, fastperiod=12, slowperiod=26, signalperiod=9):
    ema_fast = df['close'].ewm(span=fastperiod, min_periods=fastperiod).mean()
    ema_slow = df['close'].ewm(span=slowperiod, min_periods=slowperiod).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signalperiod, min_periods=signalperiod).mean()
    macd_hist = macd - macd_signal
    return macd, macd_signal, macd_hist


def calculate_stochastic(df, period=14):
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()
    stochastic = 100 * ((df['close'] - low_min) / (high_max - low_min))
    return stochastic


def calculate_cci(df, period=20):
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    moving_avg = typical_price.rolling(window=period).mean()
    mad = (typical_price - moving_avg).abs().rolling(window=period).mean()
    cci = (typical_price - moving_avg) / (0.015 * mad)
    return cci


def calculate_atr(df, period=14):
    df['H-L'] = df['high'] - df['low']
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    atr = df['TR'].rolling(window=period).mean()
    return atr


def calculate_sma(df, period):
    return df['close'].rolling(window=period).mean()

def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

def calculate_wma(df, period):
    weights = np.arange(1, period+1)
    return df['close'].rolling(window=period).apply(lambda x: np.dot(x, weights)/weights.sum(), raw=True)

def calculate_hma(df, period):
    wma_half = calculate_wma(df, period//2)
    wma_full = calculate_wma(df, period)
    return calculate_wma(df.assign(close=wma_half - wma_full), period=int(np.sqrt(period)))



def calculate_vwap(df):
    vwap = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    return vwap

def generate_signal(df, period=14):
    last_row = df.iloc[-1]

    try:
        rsi = last_row[f'RSI_{period}']
    except KeyError:
        raise KeyError(f"RSI_{period} column is missing.")

    if rsi < 30:
        rsi_signal = 'Buy'
    elif rsi > 70:
        rsi_signal = 'Sell'
    else:
        rsi_signal = 'Hold'

    try:
        macd_hist = last_row[f'MACD_hist_{period}']
    except KeyError:
        raise KeyError(f"MACD_hist_{period} column is missing.")

    if macd_hist > 0:
        macd_signal = 'Buy'
    elif macd_hist < 0:
        macd_signal = 'Sell'
    else:
        macd_signal = 'Hold'

    try:
        stochastic = last_row[f'Stochastic_{period}']
    except KeyError:
        raise KeyError(f"Stochastic_{period} column is missing.")

    if stochastic < 20:
        stochastic_signal = 'Buy'
    elif stochastic > 80:
        stochastic_signal = 'Sell'
    else:
        stochastic_signal = 'Hold'

    # cci = last_row[f'CCI_{period}']
    # if cci > 100:
    #     cci_signal = 'Sell'
    # elif cci < -100:
    #     cci_signal = 'Buy'
    # else:
    #     cci_signal = 'Hold'
    #
    # atr = last_row[f'ATR_{period}']
    # if atr > 1.5:
    #     atr_signal = 'Sell'
    # else:
    #     atr_signal = 'Buy'

    try:
        sma_10 = last_row[f'SMA_{period}']
        sma_50 = last_row['SMA_50']
        ema_10 = last_row[f'EMA_{period}']
        wma_10 = last_row[f'WMA_{period}']
        hma_14 = last_row[f'HMA_{period}']
        vwap = last_row[f'VWAP_{period}']
    except KeyError as e:
        raise KeyError(f"Column {e} is missing.")

    if sma_10 > sma_50 and ema_10 > sma_50 and wma_10 > sma_50 and hma_14 > sma_50 and vwap > sma_50:
        ma_signal = 'Buy'
    else:
        ma_signal = 'Sell'

    if rsi_signal == 'Buy' and macd_signal == 'Buy' and ma_signal == 'Buy':
        final_signal = 'Buy'
    elif rsi_signal == 'Sell' and macd_signal == 'Sell' and ma_signal == 'Sell':
        final_signal = 'Sell'
    else:
        final_signal = 'Hold'

    return final_signal


# @app.route('/market_signal', methods=['POST'])
# def generate_signal_api():
#     data = request.get_json()
#     df = pd.DataFrame(data)
#     periods = [5, 10, 14, 20, 50]
#
#     for period in periods:
#         df[f'RSI_{period}'] = calculate_rsi(df, period=period)
#         df[f'MACD_{period}'], df[f'MACD_signal_{period}'], df[f'MACD_hist_{period}'] = calculate_macd(df)
#         df[f'Stochastic_{period}'] = calculate_stochastic(df, period=period)
#         df[f'CCI_{period}'] = calculate_cci(df, period=period)
#         df[f'ATR_{period}'] = calculate_atr(df, period=period)
#         df[f'SMA_{period}'] = calculate_sma(df, window=period)
#         df[f'EMA_{period}'] = calculate_ema(df, span=period)
#         df[f'WMA_{period}'] = calculate_wma(df, window=period)
#         df[f'HMA_{period}'] = calculate_hma(df, period=period)
#         df[f'VWAP_{period}'] = calculate_vwap(df)
#
#     final_signal = generate_signal(df)
#
#     return {"final_signal": final_signal}

#TEST TODO
@app.route('/market_signal', methods=['POST'])
def generate_signal_api():
    data = request.get_json()
    df = pd.DataFrame(data)

    # Convert the 'date' column to datetime if necessary
    df['date'] = pd.to_datetime(df['date'])

    df.set_index('date', inplace=True)

    # Resample data for daily, weekly, and monthly
    df_daily = df.resample('D').last()
    df_weekly = df.resample('W').last()
    df_monthly = df.resample('M').last()

    periods = [5, 10, 14, 20, 50]

    # Calculate indicators for daily, weekly, and monthly
    for period in periods:
        # For daily data
        df_daily[f'RSI_{period}'] = calculate_rsi(df_daily, period=period)
        df_daily[f'MACD_{period}'], df_daily[f'MACD_signal_{period}'], df_daily[f'MACD_hist_{period}'] = calculate_macd(
            df_daily)
        df_daily[f'Stochastic_{period}'] = calculate_stochastic(df_daily, period=period)
        # Calculate missing indicators (SMA, EMA, WMA, HMA, VWAP) for daily data
        df_daily[f'SMA_{period}'] = calculate_sma(df_daily, period)
        df_daily[f'EMA_{period}'] = calculate_ema(df_daily, period)
        df_daily[f'WMA_{period}'] = calculate_wma(df_daily, period)
        df_daily[f'HMA_{period}'] = calculate_hma(df_daily, period)
        df_daily[f'VWAP_{period}'] = calculate_vwap(df_daily)

        # For weekly data
        df_weekly[f'RSI_{period}'] = calculate_rsi(df_weekly, period=period)
        df_weekly[f'MACD_{period}'], df_weekly[f'MACD_signal_{period}'], df_weekly[
            f'MACD_hist_{period}'] = calculate_macd(df_weekly)
        df_weekly[f'Stochastic_{period}'] = calculate_stochastic(df_weekly, period=period)
        # Calculate missing indicators (SMA, EMA, WMA, HMA, VWAP) for weekly data
        df_weekly[f'SMA_{period}'] = calculate_sma(df_weekly, period)
        df_weekly[f'EMA_{period}'] = calculate_ema(df_weekly, period)
        df_weekly[f'WMA_{period}'] = calculate_wma(df_weekly, period)
        df_weekly[f'HMA_{period}'] = calculate_hma(df_weekly, period)
        df_weekly[f'VWAP_{period}'] = calculate_vwap(df_weekly)

        # For monthly data
        df_monthly[f'RSI_{period}'] = calculate_rsi(df_monthly, period=period)
        df_monthly[f'MACD_{period}'], df_monthly[f'MACD_signal_{period}'], df_monthly[
            f'MACD_hist_{period}'] = calculate_macd(df_monthly)
        df_monthly[f'Stochastic_{period}'] = calculate_stochastic(df_monthly, period=period)
        # Calculate missing indicators (SMA, EMA, WMA, HMA, VWAP) for monthly data
        df_monthly[f'SMA_{period}'] = calculate_sma(df_monthly, period)
        df_monthly[f'EMA_{period}'] = calculate_ema(df_monthly, period)
        df_monthly[f'WMA_{period}'] = calculate_wma(df_monthly, period)
        df_monthly[f'HMA_{period}'] = calculate_hma(df_monthly, period)
        df_monthly[f'VWAP_{period}'] = calculate_vwap(df_monthly)

    # Generate signals for each timeframe
    daily_signal = generate_signal(df_daily)
    weekly_signal = generate_signal(df_weekly)
    monthly_signal = generate_signal(df_monthly)
    print(jsonify({
        "daily_signal": daily_signal,
        "weekly_signal": weekly_signal,
        "monthly_signal": monthly_signal
    }).get_json())

    # Return the signals
    return jsonify({
        "daily_signal": daily_signal,
        "weekly_signal": weekly_signal,
        "monthly_signal": monthly_signal
    })


#========================================
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
