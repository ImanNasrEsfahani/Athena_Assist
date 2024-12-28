import pandas as pd
import csv

# # Read the CSV file with inconsistent space delimiters
# df = pd.read_csv(r'data/EURUSD_M15-raw.csv', sep=r'\s+', engine='python', skiprows=[0])
# df.columns = ["date", "time", "open", "high", "low", "close", "volume", "extra"]
# df['date'] = df['date'].str.replace(r'^\"?(.*?)$', r'\1', regex=True)
# df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
# df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S').dt.tz_localize('UTC')
# df.drop(['extra', "date", "time"], axis=1, inplace=True)
#
# # Save the DataFrame to a standard CSV file
# df.to_csv(rf"data/EURUSD_M15.csv", index=False)
#
# # Display the first few rows of the DataFrame
# print(df.head())


from src.features.convert_to_upper_time_frame import convert_to_upper_time_frame

# Define start and end dates for filtering
start = "2017-01-01 00:00:00+00:00"
end = "2024-12-01 00:00:00+00:00"

df = pd.read_csv(rf"data/EURUSD_M15.csv")
print(df)

filtered_df = df[(df['datetime'] >= start) & (df['datetime'] <= end)]

print(filtered_df, "filtered_df")
# h1 = convert_to_upper_time_frame(data=filtered_df, timeframe="15min")
print(filtered_df)

filtered_df.to_csv(rf"data/EURUSD_M15-edited.csv", index=False)