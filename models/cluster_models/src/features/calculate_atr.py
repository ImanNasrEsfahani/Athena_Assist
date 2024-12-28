import pandas as pd
import numpy as np

def calculate_atr(data: pd.DataFrame, timeframe, period=14):
    """
    Calculate the Average True Range (ATR) for a given dataset.

    Parameters:
    data (pd.DataFrame): DataFrame with 'high', 'low', and 'close' columns.
    period (int): The number of periods for ATR calculation (default: 14).

    Returns:
    pd.DataFrame: Original DataFrame with an additional 'ATR' column.
    """
    # # Calculate True Range (TR)
    # data['TR'] = data[['high', 'low', 'close']].apply(
    #     lambda row: max(row['high'] - row['low'],
    #                     abs(row['high'] - row['close'].shift(1)),
    #                     abs(row['low'] - row['close'].shift(1))), axis=1)
    df = pd.DataFrame()
    df[f"""TR_{timeframe}"""] = np.maximum(
        data['high'] - data['low'],
        np.abs(data['high'] - data['close'].shift(1)),
        np.abs(data['low'] - data['close'].shift(1))
    )

    # Calculate ATR using Wilder's Moving Average
    df[f"""ATR_{timeframe}"""] = df[f"""TR_{timeframe}"""].ewm(alpha=1/period, adjust=False).mean()

    return df[[f"""ATR_{timeframe}"""]]

# Example usage:
# df = pd.DataFrame({'high': [...], 'low': [...], 'close': [...]})
# df_with_atr = calculate_atr(df)