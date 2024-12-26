import pandas as pd
import numpy as np
import ta

# Load the uploaded file to analyze its structure and content
data = pd.read_csv(r'C:\Users\Ane\Downloads\DAS-Homeworks-main\Домашна 1\stock_market.csv')
data = data[data['Issuer'] == 'ADIN']   #                                                       ---RABOTIMO SS 1 ISSUER TREBA DA SE TRGNE

data.rename(columns={'Last trade price': 'last_transaction_price'}, inplace=True)

unique_issuers = data['Issuer'].unique()

# Create a dictionary to store DataFrames for each issuer
issuer_dfs = {}

# Split the data for each issuer
for issuer in unique_issuers:
    issuer_dfs[issuer] = data[data['Issuer'] == issuer].copy()

# Data preprocessing
# Convert 'Date' column to datetime
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

# Remove rows with invalid dates
data = data.dropna(subset=['Date'])

# Sort by date in ascending order for time-series analysis
data = data.sort_values(by='Date')

# Remove commas from 'Last trade price' and convert to numeric
data['last_transaction_price'] = pd.to_numeric(data['last_transaction_price'].str.replace(',', ''), errors='coerce')

# Select necessary columns for technical analysis
technical_data = data[['Date', 'last_transaction_price']].dropna()

# Rename columns for easier handling
technical_data.rename(columns={'last_transaction_price': 'Price'}, inplace=True)


def calculate_daily_indicators(data):
    """Calculate technical indicators for daily timeframe (14 periods)"""
    df = data.copy()
    window = 14
    suffix = '1D'

    # Calculate RSI
    df[f'RSI_{suffix}'] = ta.momentum.RSIIndicator(
        close=df['last_transaction_price'],
        window=window
    ).rsi()

    # Calculate Stochastic RSI
    df[f'Stoch_{suffix}'] = ta.momentum.StochRSIIndicator(
        close=df['last_transaction_price'],
        window=window
    ).stochrsi()

    # Calculate MACD
    macd = ta.trend.MACD(
        close=df['last_transaction_price'],
        window_slow=window,
        window_fast=int(window / 2),
        window_sign=int(window / 3)
    )
    df[f'MACD_{suffix}'] = macd.macd_diff()

    # Calculate Williams %R
    df[f'Williams_%R_{suffix}'] = ta.momentum.WilliamsRIndicator(
        high=df['last_transaction_price'],
        low=df['last_transaction_price'],
        close=df['last_transaction_price'],
        lbp=window
    ).williams_r()

    # Calculate CCI
    df[f'CCI_{suffix}'] = ta.trend.CCIIndicator(
        high=df['last_transaction_price'],
        low=df['last_transaction_price'],
        close=df['last_transaction_price'],
        window=window
    ).cci()

    # Calculate weights for WMA
    weights = np.array(range(1, window + 1))
    weights = weights / weights.sum()

    # Calculate Moving Averages
    df[f'SMA_{suffix}'] = df['last_transaction_price'].rolling(window=window).mean()
    df[f'EMA_{suffix}'] = df['last_transaction_price'].ewm(span=window, adjust=False).mean()
    df[f'WMA_{suffix}'] = df['last_transaction_price'].rolling(window=window).apply(
        lambda x: np.dot(x, weights), raw=True
    )

    # Calculate Hull Moving Average
    df[f'HMA_{suffix}'] = (
            2 * df[f'EMA_{suffix}'] -
            df[f'SMA_{suffix}']
    ).rolling(window).mean()

    # Calculate Triple EMA
    df[f'TEMA_{suffix}'] = (
            3 * df[f'EMA_{suffix}'] -
            3 * df[f'EMA_{suffix}'].ewm(span=window).mean() +
            df[f'EMA_{suffix}'].ewm(span=window).mean()
    )

    return df


def calculate_weekly_indicators(data):
    """Calculate technical indicators for weekly timeframe (70 periods ≈ 14 weeks)"""
    df = data.copy()
    window = 70
    suffix = '1W'

    # Same calculations as daily but with weekly window
    # Calculate RSI
    df[f'RSI_{suffix}'] = ta.momentum.RSIIndicator(
        close=df['last_transaction_price'],
        window=window
    ).rsi()

    # Calculate Stochastic RSI
    df[f'Stoch_{suffix}'] = ta.momentum.StochRSIIndicator(
        close=df['last_transaction_price'],
        window=window
    ).stochrsi()

    # Calculate MACD
    macd = ta.trend.MACD(
        close=df['last_transaction_price'],
        window_slow=window,
        window_fast=int(window / 2),
        window_sign=int(window / 3)
    )
    df[f'MACD_{suffix}'] = macd.macd_diff()

    # Calculate Williams %R
    df[f'Williams_%R_{suffix}'] = ta.momentum.WilliamsRIndicator(
        high=df['last_transaction_price'],
        low=df['last_transaction_price'],
        close=df['last_transaction_price'],
        lbp=window
    ).williams_r()

    # Calculate CCI
    df[f'CCI_{suffix}'] = ta.trend.CCIIndicator(
        high=df['last_transaction_price'],
        low=df['last_transaction_price'],
        close=df['last_transaction_price'],
        window=window
    ).cci()

    # Calculate weights for WMA
    weights = np.array(range(1, window + 1))
    weights = weights / weights.sum()

    # Calculate Moving Averages
    df[f'SMA_{suffix}'] = df['last_transaction_price'].rolling(window=window).mean()
    df[f'EMA_{suffix}'] = df['last_transaction_price'].ewm(span=window, adjust=False).mean()
    df[f'WMA_{suffix}'] = df['last_transaction_price'].rolling(window=window).apply(
        lambda x: np.dot(x, weights), raw=True
    )

    # Calculate Hull Moving Average
    df[f'HMA_{suffix}'] = (
            2 * df[f'EMA_{suffix}'] -
            df[f'SMA_{suffix}']
    ).rolling(window).mean()

    # Calculate Triple EMA
    df[f'TEMA_{suffix}'] = (
            3 * df[f'EMA_{suffix}'] -
            3 * df[f'EMA_{suffix}'].ewm(span=window).mean() +
            df[f'EMA_{suffix}'].ewm(span=window).mean()
    )

    return df


def calculate_monthly_indicators(data):
    """Calculate technical indicators for monthly timeframe (300 periods ≈ 14 months)"""
    df = data.copy()
    window = 300
    suffix = '1M'

    # Same calculations as daily but with monthly window
    # Calculate RSI
    df[f'RSI_{suffix}'] = ta.momentum.RSIIndicator(
        close=df['last_transaction_price'],
        window=window
    ).rsi()

    # Calculate Stochastic RSI
    df[f'Stoch_{suffix}'] = ta.momentum.StochRSIIndicator(
        close=df['last_transaction_price'],
        window=window
    ).stochrsi()

    # Calculate MACD
    macd = ta.trend.MACD(
        close=df['last_transaction_price'],
        window_slow=window,
        window_fast=int(window / 2),
        window_sign=int(window / 3)
    )
    df[f'MACD_{suffix}'] = macd.macd_diff()

    # Calculate Williams %R
    df[f'Williams_%R_{suffix}'] = ta.momentum.WilliamsRIndicator(
        high=df['last_transaction_price'],
        low=df['last_transaction_price'],
        close=df['last_transaction_price'],
        lbp=window
    ).williams_r()

    # Calculate CCI
    df[f'CCI_{suffix}'] = ta.trend.CCIIndicator(
        high=df['last_transaction_price'],
        low=df['last_transaction_price'],
        close=df['last_transaction_price'],
        window=window
    ).cci()

    # Calculate weights for WMA
    weights = np.array(range(1, window + 1))
    weights = weights / weights.sum()

    # Calculate Moving Averages
    df[f'SMA_{suffix}'] = df['last_transaction_price'].rolling(window=window).mean()
    df[f'EMA_{suffix}'] = df['last_transaction_price'].ewm(span=window, adjust=False).mean()
    df[f'WMA_{suffix}'] = df['last_transaction_price'].rolling(window=window).apply(
        lambda x: np.dot(x, weights), raw=True
    )

    # Calculate Hull Moving Average
    df[f'HMA_{suffix}'] = (
            2 * df[f'EMA_{suffix}'] -
            df[f'SMA_{suffix}']
    ).rolling(window).mean()

    # Calculate Triple EMA
    df[f'TEMA_{suffix}'] = (
            3 * df[f'EMA_{suffix}'] -
            3 * df[f'EMA_{suffix}'].ewm(span=window).mean() +
            df[f'EMA_{suffix}'].ewm(span=window).mean()
    )

    return df


# Indicator Retrieval Functions
def get_daily_indicators(df):
    """Returns all technical indicators for daily timeframe"""
    daily_columns = ['Date', 'last_transaction_price']
    indicator_columns = [
        'RSI_1D', 'Stoch_1D', 'MACD_1D', 'Williams_%R_1D', 'CCI_1D',
        'SMA_1D', 'EMA_1D', 'WMA_1D', 'HMA_1D', 'TEMA_1D'
    ]

    # Add all columns that exist in the DataFrame
    daily_columns.extend([col for col in indicator_columns if col in df.columns])

    daily_indicators = df[daily_columns].copy()
    return daily_indicators


def get_weekly_indicators(df):
    """Returns all technical indicators for weekly timeframe"""
    weekly_columns = ['Date', 'last_transaction_price']
    indicator_columns = [
        'RSI_1W', 'Stoch_1W', 'MACD_1W', 'Williams_%R_1W', 'CCI_1W',
        'SMA_1W', 'EMA_1W', 'WMA_1W', 'HMA_1W', 'TEMA_1W'
    ]

    # Add all columns that exist in the DataFrame
    weekly_columns.extend([col for col in indicator_columns if col in df.columns])

    weekly_indicators = df[weekly_columns].copy()
    return weekly_indicators


def get_monthly_indicators(df):
    """Returns all technical indicators for monthly timeframe"""
    monthly_columns = ['Date', 'last_transaction_price']
    indicator_columns = [
        'RSI_1M', 'Stoch_1M', 'MACD_1M', 'Williams_%R_1M', 'CCI_1M',
        'SMA_1M', 'EMA_1M', 'WMA_1M', 'HMA_1M', 'TEMA_1M'
    ]

    # Add all columns that exist in the DataFrame
    monthly_columns.extend([col for col in indicator_columns if col in df.columns])

    monthly_indicators = df[monthly_columns].copy()
    return monthly_indicators


# Main calculation function
def calculate_all_timeframes(data):
    """Calculate all technical indicators for all timeframes"""
    df = data.copy()

    # Calculate indicators for each timeframe
    df = calculate_daily_indicators(df)
    df = calculate_weekly_indicators(df)
    df = calculate_monthly_indicators(df)

    return df


# Example usage
#def main():                                                   ---PRINTOVI
    # Load and prepare your data
 #   data = pd.read_csv('stock_market.csv')
 #   data = data[data['Issuer'] == 'ADIN']
 #   data['Date'] = pd.to_datetime(data['Date'])
 #   data['last_transaction_price'] = pd.to_numeric(data['last_transaction_price'].str.replace(',', ''), errors='coerce')

    # Calculate all indicators
  #  technical_data = calculate_all_timeframes(data)

    # Get specific timeframe indicators
   # daily_data = get_daily_indicators(technical_data)
   # weekly_data = get_weekly_indicators(technical_data)
   # monthly_data = get_monthly_indicators(technical_data)


def generate_signals(df):                                                                   #SIGNALS
    """Generate buy/sell signals for all technical indicators"""
    # Buy/Sell signals for SMA (1 day, 1 week, 1 month)
    df['SMA_Signal_1D'] = np.where(df['SMA_1D'] > df['last_transaction_price'], 'Buy',
                                   np.where(df['SMA_1D'] < df['last_transaction_price'], 'Sell', 'Hold'))
    df['SMA_Signal_1W'] = np.where(df['SMA_1W'] > df['last_transaction_price'], 'Buy',
                                   np.where(df['SMA_1W'] < df['last_transaction_price'], 'Sell', 'Hold'))
    df['SMA_Signal_1M'] = np.where(df['SMA_1M'] > df['last_transaction_price'], 'Buy',
                                   np.where(df['SMA_1M'] < df['last_transaction_price'], 'Sell', 'Hold'))

    # Buy/Sell signals for EMA
    df['EMA_Signal_1D'] = np.where(df['EMA_1D'] > df['last_transaction_price'], 'Buy',
                                   np.where(df['EMA_1D'] < df['last_transaction_price'], 'Sell', 'Hold'))
    df['EMA_Signal_1W'] = np.where(df['EMA_1W'] > df['last_transaction_price'], 'Buy',
                                   np.where(df['EMA_1W'] < df['last_transaction_price'], 'Sell', 'Hold'))
    df['EMA_Signal_1M'] = np.where(df['EMA_1M'] > df['last_transaction_price'], 'Buy',
                                   np.where(df['EMA_1M'] < df['last_transaction_price'], 'Sell', 'Hold'))

    # Buy/Sell signals for RSI
    df['RSI_Signal_1D'] = np.where(df['RSI_1D'] < 30, 'Buy',
                                   np.where(df['RSI_1D'] > 70, 'Sell', 'Hold'))
    df['RSI_Signal_1W'] = np.where(df['RSI_1W'] < 30, 'Buy',
                                   np.where(df['RSI_1W'] > 70, 'Sell', 'Hold'))
    df['RSI_Signal_1M'] = np.where(df['RSI_1M'] < 30, 'Buy',
                                   np.where(df['RSI_1M'] > 70, 'Sell', 'Hold'))

    # Buy/Sell signals for MACD
    df['MACD_Signal_1D'] = np.where(df['MACD_1D'] > 0, 'Buy',
                                    np.where(df['MACD_1D'] < 0, 'Sell', 'Hold'))
    df['MACD_Signal_1W'] = np.where(df['MACD_1W'] > 0, 'Buy',
                                    np.where(df['MACD_1W'] < 0, 'Sell', 'Hold'))
    df['MACD_Signal_1M'] = np.where(df['MACD_1M'] > 0, 'Buy',
                                    np.where(df['MACD_1M'] < 0, 'Sell', 'Hold'))

    # Williams %R signals
    df['Williams_Signal_1D'] = np.where(df['Williams_%R_1D'] < -80, 'Buy',
                                        np.where(df['Williams_%R_1D'] > -20, 'Sell', 'Hold'))
    df['Williams_Signal_1W'] = np.where(df['Williams_%R_1W'] < -80, 'Buy',
                                        np.where(df['Williams_%R_1W'] > -20, 'Sell', 'Hold'))
    df['Williams_Signal_1M'] = np.where(df['Williams_%R_1M'] < -80, 'Buy',
                                        np.where(df['Williams_%R_1M'] > -20, 'Sell', 'Hold'))

    # CCI signals
    df['CCI_Signal_1D'] = np.where(df['CCI_1D'] < -100, 'Buy',
                                   np.where(df['CCI_1D'] > 100, 'Sell', 'Hold'))
    df['CCI_Signal_1W'] = np.where(df['CCI_1W'] < -100, 'Buy',
                                   np.where(df['CCI_1W'] > 100, 'Sell', 'Hold'))
    df['CCI_Signal_1M'] = np.where(df['CCI_1M'] < -100, 'Buy',
                                   np.where(df['CCI_1M'] > 100, 'Sell', 'Hold'))

    return df


def get_daily_signals(df):
    """Returns all technical indicators and signals for daily timeframe"""
    daily_columns = ['Date', 'last_transaction_price']
    daily_columns.extend([col for col in df.columns if '1D' in col])

    daily_signals = df[daily_columns].copy()

    signal_columns = ['SMA_Signal_1D', 'EMA_Signal_1D', 'RSI_Signal_1D',
                      'MACD_Signal_1D', 'Williams_Signal_1D', 'CCI_Signal_1D']

    daily_signals['Buy_Count'] = (daily_signals[signal_columns] == 'Buy').sum(axis=1)
    daily_signals['Sell_Count'] = (daily_signals[signal_columns] == 'Sell').sum(axis=1)

    daily_signals['Daily_Composite_Signal'] = np.where(
        daily_signals['Buy_Count'] > daily_signals['Sell_Count'], 'Buy',
        np.where(daily_signals['Sell_Count'] > daily_signals['Buy_Count'], 'Sell', 'Hold')
    )

    daily_signals = daily_signals.drop(['Buy_Count', 'Sell_Count'], axis=1)

    return daily_signals


def get_weekly_signals(df):
    """Returns all technical indicators and signals for weekly timeframe"""
    weekly_columns = ['Date', 'last_transaction_price']
    weekly_columns.extend([col for col in df.columns if '1W' in col])

    weekly_signals = df[weekly_columns].copy()

    signal_columns = ['SMA_Signal_1W', 'EMA_Signal_1W', 'RSI_Signal_1W',
                      'MACD_Signal_1W', 'Williams_Signal_1W', 'CCI_Signal_1W']

    weekly_signals['Buy_Count'] = (weekly_signals[signal_columns] == 'Buy').sum(axis=1)
    weekly_signals['Sell_Count'] = (weekly_signals[signal_columns] == 'Sell').sum(axis=1)

    weekly_signals['Weekly_Composite_Signal'] = np.where(
        weekly_signals['Buy_Count'] > weekly_signals['Sell_Count'], 'Buy',
        np.where(weekly_signals['Sell_Count'] > weekly_signals['Buy_Count'], 'Sell', 'Hold')
    )

    weekly_signals = weekly_signals.drop(['Buy_Count', 'Sell_Count'], axis=1)

    return weekly_signals


def get_monthly_signals(df):
    """Returns all technical indicators and signals for monthly timeframe"""
    monthly_columns = ['Date', 'last_transaction_price']
    monthly_columns.extend([col for col in df.columns if '1M' in col])

    monthly_signals = df[monthly_columns].copy()

    signal_columns = ['SMA_Signal_1M', 'EMA_Signal_1M', 'RSI_Signal_1M',
                      'MACD_Signal_1M', 'Williams_Signal_1M', 'CCI_Signal_1M']

    monthly_signals['Buy_Count'] = (monthly_signals[signal_columns] == 'Buy').sum(axis=1)
    monthly_signals['Sell_Count'] = (monthly_signals[signal_columns] == 'Sell').sum(axis=1)

    monthly_signals['Monthly_Composite_Signal'] = np.where(
        monthly_signals['Buy_Count'] > monthly_signals['Sell_Count'], 'Buy',
        np.where(monthly_signals['Sell_Count'] > monthly_signals['Buy_Count'], 'Sell', 'Hold')
    )

    monthly_signals = monthly_signals.drop(['Buy_Count', 'Sell_Count'], axis=1)

    return monthly_signals


# Usage example:
# First calculate all technical indicators using your existing calculate_all_timeframes function
technical_data = calculate_all_timeframes(data)

# Then generate all signals
technical_data_with_signals = generate_signals(technical_data)

# Finally, get separate timeframe signals
daily_signals = get_daily_signals(technical_data_with_signals)
weekly_signals = get_weekly_signals(technical_data_with_signals)
monthly_signals = get_monthly_signals(technical_data_with_signals)

def calculate_all_timeframes(data):
    """Calculate all technical indicators for daily, weekly, and monthly timeframes and return as a dictionary."""
    df = data.copy()

    # Calculate indicators for each timeframe
    df_daily = calculate_daily_indicators(df)
    df_weekly = calculate_weekly_indicators(df)
    df_monthly = calculate_monthly_indicators(df)

    # Store DataFrames in a dictionary
    indicator_data = {
        'daily': df_daily,
        'weekly': df_weekly,
        'monthly': df_monthly
    }

    return indicator_data

# Print results                                                                                           -----PRINTOVI
#print("\nDaily signals and indicators:")
#print(daily_signals.tail())

#print("\nWeekly signals and indicators:")
#print(weekly_signals.tail())

#print("\nMonthly signals and indicators:")
#print(monthly_signals.tail())

# Combine all composite signals into one DataFrame
#composite_signals = pd.DataFrame({
 #   'Date': daily_signals['Date'],
 #   'Price': daily_signals['last_transaction_price'],
 #   'Daily_Signal': daily_signals['Daily_Composite_Signal'],
 #   'Weekly_Signal': weekly_signals['Weekly_Composite_Signal'],
 #   'Monthly_Signal': monthly_signals['Monthly_Composite_Signal']
#})

#print("\nAll composite signals:")
#print(composite_signals.tail())