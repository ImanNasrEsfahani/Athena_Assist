import pandas as pd
import numpy as np


def calculate_sma_ema(data, column='close', periods=[10, 20, 50]):
    """
    Calculate Simple Moving Average (SMA) and Exponential Moving Average (EMA)

    Parameters:
    data (pd.DataFrame): DataFrame with price data
    column (str): Column name to use for calculations (default: 'close')
    periods (list): List of periods for moving averages (default: [10, 20, 50])

    Returns:
    pd.DataFrame: Original DataFrame with additional SMA and EMA columns
    """
    for period in periods:
        data[f'SMA_{period}'] = data[column].rolling(window=period).mean()
        data[f'EMA_{period}'] = data[column].ewm(span=period, adjust=False).mean()

    return data


def calculate_sma(data, timeframe, column='close', periods=[10, 20, 50]):
    """
    Calculate Simple Moving Average (SMA)

    Parameters:
    data (pd.DataFrame): DataFrame with price data
    column (str): Column name to use for calculations (default: 'close')
    periods (list): List of periods for moving averages (default: [10, 20, 50])

    Returns:
    pd.DataFrame: Original DataFrame with additional SMA columns
    """
    df = pd.DataFrame()
    for period in periods:
        df[f'SMA_{period}_{timeframe}'] = data[column].rolling(window=period).mean()

        # Calculate distance
        df[f'SMA_{period}_{timeframe}'] = data["close"] - df[f'SMA_{period}_{timeframe}']

        # 1 if close is above 0, -1 if below
        # df[f'SMA_{period}_{timeframe}'] = np.where(df[f'SMA_{period}_{timeframe}'] >= 0, 1, -1)

    return df


def calculate_ema(data, timeframe, column='close', periods=[10, 20, 50]):
    """
    Calculate Exponential Moving Average (EMA)

    Parameters:
    data (pd.DataFrame): DataFrame with price data
    column (str): Column name to use for calculations (default: 'close')
    periods (list): List of periods for moving averages (default: [10, 20, 50])

    Returns:
    pd.DataFrame: Original DataFrame with additional EMA columns
    """
    df = pd.DataFrame()
    for period in periods:
        df[f'EMA_{period}_{timeframe}'] = data[column].ewm(span=period, adjust=False).mean()

        # Calculate distance
        df[f'EMA_{period}_{timeframe}'] = data["close"] - df[f'EMA_{period}_{timeframe}']

        # 1 if close is above 0, -1 if below
        # df[f'EMA_{period}_{timeframe}'] = np.where(df[f'EMA_{period}_{timeframe}'] >= 0, 1, -1)

    return df


# Example usage:
# df = pd.DataFrame({'close': [...]})
# df = calculate_sma(df)
# df = calculate_ema(df)

def calculate_wma(data, timeframe, column='close', periods=[10, 20, 50]):
    """
    Calculate Weighted Moving Average (WMA)

    Parameters:
    data (pd.DataFrame): DataFrame with price data
    column (str): Column name to use for calculations (default: 'close')
    periods (list): List of periods for moving averages (default: [10, 20, 50])

    Returns:
    pd.DataFrame: Original DataFrame with additional WMA columns
    """
    df = pd.DataFrame()
    for period in periods:
        weights = np.arange(1, period + 1)
        df[f'WMA_{period}_{timeframe}'] = data[column].rolling(window=period).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True
        )

        # Calculate distance
        df[f'WMA_{period}_{timeframe}'] = data["close"] - df[f'WMA_{period}_{timeframe}']

        # 1 if close is above 0, -1 if below
        # df[f'WMA_{period}_{timeframe}'] = np.where(df[f'WMA_{period}_{timeframe}'] >= 0, 1, -1)

    return df

# Example usage:
# df = pd.DataFrame({'close': [...]})
# df = calculate_sma_ema(df)
# df = calculate_wma(df)