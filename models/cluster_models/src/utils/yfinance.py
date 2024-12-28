import yfinance as yf
import pandas as pd
from joblib import load, dump

def fetch_yahoo_finance_data(symbol: str, start: str, end: str, interval: str):
    try:
        start = pd.to_datetime(start) - pd.Timedelta(days=51)
        print(f"""Start of downloading from Yahoo Finance. Symbol: {symbol}, Start: {start} end: {end} intervals: {interval}""")
        data = yf.download(tickers=symbol, start=start, end=end, interval=interval)

        if data.empty:
            print(f"No data found for {symbol} in the specified date range.")
            exit()

        print("Download completed successfully.")

        data.columns = data.columns.droplevel(1)  # remove the second label of columns
        data["datetime"] = data.index   # make a copy from index to a column with name data time
        data.reset_index(drop=True, inplace=True)  # remove index
        data.index.name = None
        columns = {
            'datetime': 'datetime',
            'Close': 'close',
            'High': 'high',
            'Low': 'low',
            'Open': 'open',
            'Volume': 'volume'
        }
        data.rename(columns=columns, inplace=True)  # rename all columns to lower case
        data = data[list(columns.values())]
        return data

    except Exception as e:
        print(f"An error occurred while downloading data: {e}")
        return None