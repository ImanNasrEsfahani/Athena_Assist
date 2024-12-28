import os
import datetime
from joblib import load, dump
from src.tools.tools import list_files
import pandas as pd
import numpy as np
import pytz

def filtering_data(data: pd.DataFrame, symbol: str, start: str, end: str, interval: str, london_timezone: bool, newyork_timezone: bool, buffer_size: int):

    # processed_data = load(rf"data\processed\{file}")
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # Define the New York and London time zones
    new_york_tz = pytz.timezone("America/New_York")
    london_tz = pytz.timezone("Europe/London")

    # Check if both timezones are active
    if london_timezone and newyork_timezone:
        # dump(value=filter_by_working_hours(processed_data=processed_data, start_time=london_tz.localize(pd.to_datetime("09:00:00")), end_time=new_york_tz.localize(pd.to_datetime("17:00:00")), buffer_size=buffer_size), filename=rf"data\filtered\{symbol}_{start}_{end}_{interval}_filtered.joblib", compress=False)
        filter_by_working_hours(processed_data=data, start_time=london_tz.localize(pd.to_datetime("09:00:00")), end_time=new_york_tz.localize(pd.to_datetime("17:00:00")).astimezone(pytz.timezone("Europe/London")), buffer_size=buffer_size).to_csv(
            os.path.join("data", "filtered", f"{symbol}_{start}_{end}_{interval}_filtered.csv"), index=False)
        return True
    # Check if only London timezone is active
    elif london_timezone:
        # dump(value=filter_by_working_hours(processed_data=processed_data, start_time=london_tz.localize(pd.to_datetime("09:00:00")), end_time=london_tz.localize(pd.to_datetime("17:00:00")), buffer_size=buffer_size), filename=rf"data\filtered\{symbol}_{start}_{end}_{interval}_filtered.joblib", compress=False)
        filter_by_working_hours(processed_data=data, start_time=london_tz.localize(pd.to_datetime("09:00:00")), end_time=london_tz.localize(pd.to_datetime("17:00:00")), buffer_size=buffer_size).to_csv(
            os.path.join("data", "filtered", f"{symbol}_{start}_{end}_{interval}_filtered.csv"), index=False)
        return True
    # Check if only New York timezone is active
    elif newyork_timezone:
        # dump(value=filter_by_working_hours(processed_data=processed_data, start_time=new_york_tz.localize(pd.to_datetime("09:00:00")), end_time=new_york_tz.localize(pd.to_datetime("17:00:00")), buffer_size=buffer_size), filename=rf"data\filtered\{symbol}_{start}_{end}_{interval}_filtered.joblib", compress=False)
        filter_by_working_hours(processed_data=data, start_time=new_york_tz.localize(pd.to_datetime("09:00:00")).astimezone(pytz.timezone("Europe/London")), end_time=new_york_tz.localize(pd.to_datetime("17:00:00")).astimezone(pytz.timezone("Europe/London")), buffer_size=buffer_size).to_csv(
            os.path.join("data", "filtered", f"{symbol}_{start}_{end}_{interval}_filtered.csv"), index=False)
        return True

    print("saving file ...")
    # return dump(value=processed_data, filename=rf"data\filtered\{symbol}_{start}_{end}_{interval}_filtered.joblib", compress=False)
    return data.to_csv(os.path.join("data", "filtered", f"{symbol}_{start}_{end}_{interval}_filtered.csv"), index=False)

def filter_by_working_hours(processed_data: pd.DataFrame, start_time: datetime, end_time: datetime, buffer_size: int):
    """
    Filters the DataFrame to keep only rows within specified working hours in a given timezone.

    Parameters:
    - processed_data: pd.DataFrame containing a 'datetime' column.
    - start_time: time object representing the start of working hours (e.g., "09:00:00").
    - end_time: time object representing the end of working hours (e.g., "17:00:00").
    - timezone: pytz representing the timezone (e.g., "America/New_York" or "London").

    Returns:
    - pd.DataFrame containing only the rows within the specified working hours.
    """
    start_time = (start_time - pd.Timedelta(hours=buffer_size)).time()
    end_time = (end_time + pd.Timedelta(hours=buffer_size)).time()

    # Filter the DataFrame
    return processed_data[
        (processed_data['timestamp'].dt.time >= start_time) &
        (processed_data['timestamp'].dt.time <= end_time)
        ]