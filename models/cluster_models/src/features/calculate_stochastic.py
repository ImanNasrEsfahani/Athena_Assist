import pandas as pd

def calculate_stochastic(data: pd.DataFrame, timeframe, k_period=14, d_period=3):
    """
    Calculate Stochastic Oscillator for given price data.

    Parameters:
    data (pd.DataFrame): DataFrame with 'high', 'low', and 'close' columns
    k_period (int): Look-back period for %K calculation
    d_period (int): Smoothing period for %D calculation

    Returns:
    pd.DataFrame: DataFrame with '%K' and '%D' columns added
    """
    df = pd.DataFrame()
    # Calculate %K
    lowest_low = data['low'].rolling(window=k_period).min()
    highest_high = data['high'].rolling(window=k_period).max()
    df[f"""stochastic%K_{timeframe}"""] = 100 * (data['close'] - lowest_low) / (highest_high - lowest_low)

    # Calculate %D
    df[f"""stochastic%D_{timeframe}"""] = df[f"""stochastic%K_{timeframe}"""].rolling(window=d_period).mean()

    # Signal
    df[f"""stochastic_signal_{timeframe}"""] = df[f"""stochastic%K_{timeframe}"""] - df[f"""stochastic%D_{timeframe}"""]

    return df
