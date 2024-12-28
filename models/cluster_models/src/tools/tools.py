import os
import fnmatch
from datetime import datetime, timezone, timedelta
import pandas as pd
from sqlalchemy import create_engine
from sqlmodel import select


def list_files(directory: str, pattern="*", extension: str = ""):
    """
        List all files in the given directory that start with the specified pattern.

        Args:
        directory (str): The path to the directory to search.
        pattern (str): The pattern to match at the start of file names. Default is "*" (all files).

        Returns:
        list: A list of file names that match the pattern.
        """
    try:
        full_pattern = pattern

        # Ensure the pattern matches from the start of the filename
        if not pattern.endswith('*'):
            full_pattern += '*'

        if extension is not None:
            full_pattern += extension

        # List all files in the directory that match the pattern
        matching_files = [
            f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and fnmatch.fnmatch(f, full_pattern)
        ]

        if len(matching_files) == 0:
            print("No files founded")
            return []

        return matching_files
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def select_symbol():
    symbols = ["EURUSD=X", "USDJPY=X", "GBPUSD=X", "USDCHF=X", "AUDUSD=X",
               "USDCAD=X", "NZDUSD=X", "EURJPY=X", "GBPJPY=X", "EURGBP=X"]

    print("Please select a forex symbol:")
    for i, symbol in enumerate(symbols, 1):
        print(f"{i}. {symbol}")

    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(symbols):
                return symbols[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


def load_data_from_sqlite(table_name: str, database_path: str) -> pd.DataFrame | None:
    try:
        # Create a database engine
        database_url = f'sqlite:///./../{database_path}'
        engine = create_engine(database_url)

        # Read data from the specified table into a DataFrame
        df = pd.read_sql_table(table_name=table_name, con=engine)

        return df
    except Exception as e:
        print(f"An error occurred: {type(e).__name__} - {str(e)}")
        return None


def load_data(path: list, symbol: str, start: str, end: str, interval: str) -> pd.DataFrame:
    relative_path = ""
    for item in path:
        relative_path = os.path.join(relative_path, item)

    prefix = f"{symbol}_{start}_{end}_{interval}"
    files = list_files(relative_path, prefix)

    if not files:
        raise FileNotFoundError(f"No files found with prefix {prefix} in {relative_path}")

    latest_file = max(files)
    print(f"file name is found: {latest_file} in {relative_path}")

    if not latest_file.lower().endswith('.csv'):
        raise FileNotFoundError(f"No CSV file found in {relative_path} for {prefix}")

    file_path = os.path.join(relative_path, latest_file)
    return pd.read_csv(file_path)


def get_last_month_from_database(table_name: str, database_path: str, to_datetime: datetime = datetime.now()):

    # get data from Database
    database = load_data_from_sqlite(table_name=table_name, database_path=database_path)

    # Calculate the date last month
    months_ago = pd.to_datetime(to_datetime, utc=True) - timedelta(days=31)

    database['timestamp'] = pd.to_datetime(database['timestamp'])

    df = database[(pd.to_datetime(database['timestamp'], utc=True) >= months_ago) & (
                pd.to_datetime(database['timestamp'], utc=True) <= to_datetime)]

    return df


def is_working_hours(given_datetime: datetime) -> bool:
    """
    Check if timestamp is within working hours (9:00-17:00) for both London and NY
    London is UTC+0
    New York is UTC-5
    """
    # Convert timestamp to datetime if it's not already
    timestamp = pd.to_datetime(given_datetime)

    # Get London time (UTC+0)
    london_time = timestamp.tz_convert('Europe/London')
    london_hour = london_time.hour

    # Get New York time (UTC-5)
    ny_time = timestamp.tz_convert('America/New_York')
    ny_hour = ny_time.hour

    # Check if within working hours (9:00-17:00) for both cities
    london_working = 9 <= london_hour < 17
    ny_working = 9 <= ny_hour < 17

    return london_working and ny_working
