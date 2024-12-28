import pandas as pd


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
