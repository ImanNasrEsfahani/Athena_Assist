from .tools import list_files
from .utils.OANDA import fetch_oanda_data
from .utils.yfinance import fetch_yahoo_finance_data
from .utils.ALPHAVANTAGE import fetch_alpha_vantage_data

import os
import pandas as pd

def download_data(method: str, symbol: str, start: str, end: str, interval: str):
    """
    Downloads data from a specified URL and saves it to the given path.

    Parameters:
    - method (str): which method is recommended OANDA, ALPHAVANTAGE, Yahoo finance
    - symbol (str): The symbol of the data to download.
    - start (str): The start of the data to download.
    - end (str): The end of the data to download.
    - save_path (str): The local file path where the data should be saved.

    Raises:
    - Exception: If the download fails or if the response is not successful.
    """

    if method == "OANDA":
        # Import OANDA related functionality
        return fetch_oanda_data()  # Replace with actual function to fetch data from OANDA

    elif method == "ALPHAVANTAGE":
        # Import Alpha Vantage related functionality
        return fetch_alpha_vantage_data()  # Replace with actual function to fetch data from Alpha Vantage

    elif method == "yfinance":
        file = list_files(os.path.join("data", "raw") , f"{symbol}_{start}_{end}_{interval}")
        if len(file) != 0:
            print("raw file has been found")
            raw_data = pd.DataFrame(pd.read_csv(os.path.join("data", "raw", f"{file[-1]}")))
        else:
            # Import yfinance related functionality
            raw_data = fetch_yahoo_finance_data(symbol=symbol, start=start, end=end, interval=interval)

        if not isinstance(raw_data, pd.DataFrame):
            print(f"""Error in download data is : {raw_data}""")
            return 0

        raw_data.to_csv(os.path.join("data", "raw", f"{symbol}_{start}_{end}_{interval}.csv"), index=False)
        print("raw data has been saved")

        return raw_data
