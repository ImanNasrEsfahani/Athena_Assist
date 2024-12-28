import pandas as pd
import numpy as np

def calculate_rsi(data: pd.DataFrame, timeframe, period=14):
    """
    Calculate the Relative Strength Index (RSI) for a given dataset.

    Parameters:
    data (pd.DataFrame): DataFrame with a 'close' price column
    period (int): The number of periods for RSI calculation (default: 14)

    Returns:
    pd.DataFrame: Original DataFrame with an additional 'RSI' column
    """
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    df = pd.DataFrame()
    df[f"""RSI_{timeframe}"""] = rsi
    return df[[f"""RSI_{timeframe}"""]]

# Example usage:
# df = pd.DataFrame({'close': [...]})
# df_with_rsi = calculate_rsi(df)