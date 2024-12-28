import pandas as pd
# from alpha_vantage.timeseries import TimeSeries


def fetch_alpha_vantage_data(symbol):
    """
    Fetch daily stock data for a given symbol from Alpha Vantage.

    Parameters:
    - symbol (str): The stock symbol (e.g., 'AAPL' for Apple).

    Returns:
    - pd.DataFrame: A DataFrame containing daily stock prices.
    """

    # Initialize TimeSeries object with your API key
    # ts = TimeSeries(key="", output_format='pandas')

    # try:
        # Fetch daily adjusted time series data
        # data, meta_data = ts.get_daily_adjusted(symbol=symbol, outputsize='full')
        # return data
    # except Exception as e:
    #     print(f"Error fetching data: {e}")
    #     return None
