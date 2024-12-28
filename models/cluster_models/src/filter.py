import os
import datetime
import pandas as pd
import pytz


def filtering_data(data: pd.DataFrame, symbol: str, start: str, end: str, interval: str, london_timezone: bool,
                   newyork_timezone: bool, buffer_size: int):
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    start_time, end_time = getting_start_end_time(london_working_hours=london_timezone,
                                                  newyork_working_hours=newyork_timezone)
    filter_by_working_hours(processed_data=data, start_time=start_time, end_time=end_time,
                            buffer_size=buffer_size).to_csv(
        os.path.join("data", "filtered", f"{symbol}_{start}_{end}_{interval}.csv"), index=False)

    print("saving file ...")
    return 0


def filter_by_working_hours(processed_data: pd.DataFrame, start_time: datetime, end_time: datetime, buffer_size: int):
    """
    Filters the DataFrame to keep only rows within specified working hours in a given timezone.

    Parameters:
    - processed_data: pd.DataFrame containing a 'timestamp' column.
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


def getting_start_end_time(london_working_hours: bool, newyork_working_hours: bool):
    """
    Filter data based on specified timezones and save to CSV.

    Args:
        london_working_hours (bool): Whether to consider London timezone.
        newyork_working_hours (bool): Whether to consider New York timezone.

    Returns:
        start_time and end_time
    """
    london_tz = pytz.timezone("Europe/London")
    new_york_tz = pytz.timezone("America/New_York")

    if london_working_hours and newyork_working_hours:
        start_time = london_tz.localize(pd.to_datetime("09:00:00"))
        end_time = new_york_tz.localize(pd.to_datetime("17:00:00")).astimezone(london_tz)
    elif london_working_hours:
        start_time = london_tz.localize(pd.to_datetime("09:00:00"))
        end_time = london_tz.localize(pd.to_datetime("17:00:00"))
    elif newyork_working_hours:
        start_time = new_york_tz.localize(pd.to_datetime("09:00:00")).astimezone(london_tz)
        end_time = new_york_tz.localize(pd.to_datetime("17:00:00")).astimezone(london_tz)
    else:
        start_time = pd.to_datetime("00:00:00")
        end_time = pd.to_datetime("23:59:00")

    return start_time, end_time
