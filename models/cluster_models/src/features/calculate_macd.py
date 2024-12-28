import pandas as pd


def calculate_macd(data: pd.DataFrame, timeframe, fast_period=12, slow_period=26, signal_period=9):
    # Calculate the fast and slow EMAs
    ema_fast = data['close'].ewm(span=fast_period, adjust=False).mean()
    ema_slow = data['close'].ewm(span=slow_period, adjust=False).mean()

    # Calculate MACD line
    macd_line = ema_fast - ema_slow

    # Calculate signal line
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

    # Calculate MACD histogram
    macd_histogram = macd_line - signal_line

    # Add MACD indicators to the dataframe
    df = pd.DataFrame()
    df[f"""MACD_{timeframe}"""] = macd_line
    df[f"""Signal_Line_{timeframe}"""] = signal_line
    df[f"""MACD_Histogram_{timeframe}"""] = macd_histogram

    return df[[f"""MACD_{timeframe}""", f"""Signal_Line_{timeframe}""", f"""MACD_Histogram_{timeframe}"""]]