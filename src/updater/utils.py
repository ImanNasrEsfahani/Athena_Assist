from src.log_config import loggerUpdater
from src.app.notifications import run_notify_active_users
from src.updater.crud import get_last_row
from src.app.config import settings

import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Literal


async def fetch_tiingo_finance_data(symbol: str, start: str, end: str, interval: str):

    # Construct the API URL https://api.tiingo.com/tiingo/fx/eurusd/prices
    url = f"https://api.tiingo.com/tiingo/fx/{symbol}/prices"

    # Set the headers and parameters
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Token {settings.TIINGO_API_TOKEN}'
    }

    params = {
        'startDate': start,
        'resampleFreq': interval,
        "token": settings.TIINGO_API_TOKEN
    }

    # Make the API request
    response = requests.get(url, headers=headers, params=params)
    loggerUpdater.debug(response.json())

    return 0
    # Check if the request was successful
    if response.status_code == 200:
        # Convert the response to a pandas DataFrame
        data = pd.DataFrame(response.json())

        # Convert the date column to datetime
        data['date'] = pd.to_datetime(data['date'])

        # Set the date as the index
        data.set_index('date', inplace=True)

        # Display the first few rows of the data
        print(data.head())

        # You can now use this DataFrame for further analysis or visualization
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


async def fetch_yahoo_finance_data(symbol: str, start: str, end: str, interval: str):
    try:
        loggerUpdater.info(
            f"""Start of downloading from Yahoo Finance. Symbol: {symbol}, Start: {start}, End: {end}, Intervals: {interval}""")

        data = yf.download(tickers=symbol, start=start, end=end, interval=interval)
        
        if data.empty:
            loggerUpdater.error(
                f"No data found for {symbol} in the specified date range from Yahoo Finance in updater.")
            await run_notify_active_users(
                message=f"No data found for {symbol} in the specified date range from Yahoo Finance in updater.")
            return None  # Return None if no data is found

        # Check if columns have multiple levels before dropping
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
        
        # Process the data
        data["timestamp"] = data.index  # Make a copy from index to a column with name 'datetime'
        data.reset_index(drop=True, inplace=True)  # Remove index
        data.index.name = None

        columns = {
            'Datetime': 'timestamp',
            'Close': 'close',
            'High': 'high',
            'Low': 'low',
            'Open': 'open',
            'Volume': 'volume'
        }
        data.rename(columns=columns, inplace=True)  # Rename all columns to lower case
        data = data[list(columns.values())]

        loggerUpdater.info("Download completed successfully from Yahoo Finance in updater.")

        return data

    except Exception as e:
        loggerUpdater.error(f"An error occurred while downloading data from Yahoo Finance: {e}")
        await run_notify_active_users(
            message=f"An error occurred while downloading data from Yahoo Finance: {e}")
        return None


def format_position_dict_for_telegram_message(data):
    if data is None:
        return "No data available"

    emoji_map = {
        'Kind': '',
        'Score': '📈',
        'Positives': '',
        'Negatives': '',
        'Time UTC': '🗓️',
        'Time Teh': '🗓️',
        'Entry': '💰'
    }

    # Add SL and TP to emoji_map if they exist in data
    if 'sl' in data and data['sl'] is not None:
        emoji_map['sl'] = '🎯'
    if 'tp' in data and data['tp'] is not None:
        emoji_map['tp'] = '🎯'
    if 'Volume' in data and data['Volume'] is not None:
        emoji_map['Volume'] = '📊'

    formatted_text = "📊 **Prediction Results**\n\n"
    for key, value in data.items():
        emoji = emoji_map.get(key, '➖')
        formatted_text += f"{emoji} *{key.capitalize()}*: `{value}`\n"

    return formatted_text


def position_creator(data: pd.DataFrame, t: int, commission: float, position_type: str, min_size_stop_loss):
    """
    Create a position DataFrame based on the specified position type (long or short).

    Parameters:
    data (pd.DataFrame): The input DataFrame containing market data.
    t (int): The current index in the DataFrame.
    commission (float): The commission to consider for stop loss and take profit calculations.
    position_type (str): The type of position ('long' or 'short').

    Returns:
    pd.DataFrame: A DataFrame containing the position details or an empty DataFrame if conditions are not met.
    """

    open_price = data.iloc[t]['close']

    if position_type == 'long':
        min_low = data.iloc[t]['low']
        for i in range(1, 4):  # This will check t, t-1 and t-2
            min_low = min(min_low, data.iloc[t - i]['low'])

        loggerUpdater.debug(f""" final min low {min_low} {t - i}""")

        stop_loss = min_low - commission
        take_profit = open_price + abs(open_price - stop_loss) * 2 + commission
    else:
        max_high = data.iloc[t]['high']
        for i in range(1, 4):  # This will check t, t-1 and t-2
            max_high = max(max_high, data.iloc[t - i]['high'])
        stop_loss = max_high + commission
        take_profit = open_price - abs(stop_loss - open_price) * 2 - commission

    loggerUpdater.debug(f"Stop distance in Position creator function {stop_loss - open_price} min {min_size_stop_loss}")
    loggerUpdater.debug(f"stop in Position creator function {stop_loss} open price {open_price}")
    if not min_size_stop_loss < abs(stop_loss - open_price) < 5 * min_size_stop_loss:
        return pd.DataFrame()

    return pd.DataFrame({
        "kind": [position_type],
        "timestamp": [data.iloc[t]["timestamp"]],
        "open": [round(open_price, 5)],
        "sl": [round(stop_loss, 5)],
        "tp": [round(take_profit, 5)],
        "stop_distance": [round(abs(stop_loss - open_price), 5)],
    })


def calculate_position_size(entry_price: float, stop_loss: float,
                            account_balance: float, risk_percentage: float = 1.0,
                            leverage: float = 1.0) -> dict:
    """
    Calculate position size based on risk management parameters.

    Args:
        entry_price (float): Entry price of the trade
        stop_loss (float): Stop loss price
        account_balance (float): Current account balance
        risk_percentage (float): Percentage of account willing to risk (default 1%)
        leverage (float): Trading leverage (default 1.0 for spot trading)

    Returns:
        dict: Dictionary containing position details
    """
    try:
        # Calculate the risk amount in currency
        risk_amount = account_balance * (risk_percentage / 100)
        loggerUpdater.error(f"risk_amount: {risk_amount}")
        # Calculate price difference between entry and stop loss
        price_difference = abs(entry_price - stop_loss) * 10000  # Convert to pips
        loggerUpdater.error(f"price_difference: {price_difference}")
        # Calculate pip value (assuming standard forex lot size)
        pip_value = 0.0001  # For most forex pairs (0.01 for JPY pairs)

        # Calculate position size in standard lots
        # position_size = (risk_amount / price_difference) * leverage
        position_size = (risk_amount / (price_difference * pip_value)) / entry_price
        # Convert to standard lots (100,000 units)
        standard_lots = position_size / 100000
        loggerUpdater.error(f"position_size: {standard_lots}")

        # Calculate potential loss and profit
        potential_loss = price_difference * position_size

        return {
            'position_size': round(position_size, 2),
            'standard_lots': round(standard_lots, 2),
            'risk_amount': round(risk_amount, 2),
            'potential_loss': round(potential_loss, 2),
            'leverage_used': leverage,
            'risk_percentage': risk_percentage
        }

    except Exception as e:
        return {
            'error': f"Error calculating position size: {str(e)}"
        }


def convert_to_upper_time_frame(data: pd.DataFrame, timeframe: str):
    """
    Convert 1-hour time frame data to 4-hour time frame data.

    Parameters:
    data (pd.DataFrame): DataFrame with 1-hour OHLCV data and a datetime index

    Returns:
    pd.DataFrame: DataFrame with 4-hour OHLCV data
    """

    # data preparations
    df = data.copy()
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

    # resampling that convert timeframe
    ohlc_dict = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }
    df = df.resample(timeframe).agg(ohlc_dict)
    df = df.dropna()

    # post-processing
    df["timestamp"] = df.index
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df.reset_index(drop=True, inplace=True)

    return df


def is_data_update(model, pydantic_model, max_time_difference: int = 18) -> bool:
    last_row = get_last_row(model, pydantic_model)

    if not last_row:
        loggerUpdater.error(f"No data found in the {model} table.")
        return False

    date_last_row = last_row[0].timestamp
    time_difference = round((datetime.now() - date_last_row).total_seconds() / 60)

    if time_difference > max_time_difference:
        return False

    return True
