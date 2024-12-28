import pandas as pd
import numpy as np
from tqdm import tqdm

from .feature import feature_extraction


def test_model(raw_data: pd.DataFrame, symbol: str, start: str, end: str, interval: str):
    print("test model")
    # raw_data.set_index('datetime', inplace=True)

    from_start_data = raw_data[raw_data['datetime'] >= start]

    # print(start, " start")
    # print(from_start_data)
    #
    # exit()

    columns = {"kind": "string",
               "datetime": "datetime64[ns]",
               "open": "float64",
               "sl": "float64",
               "tp": "float64",
               "exit_datetime": "datetime64[ns]",
               "exit_price": "float64",
               "result": "byte",
               "hold_position": "int64",
               "profit/loss": "float64",
               "stop_distance": "float64",
               "situation": "byte"
               }
    positions = pd.DataFrame([], columns=list(columns.keys()))
    positions = positions.astype(columns)

    # closing all open positions in real time beyond of London and New york working hours in 24 hours
    for t in tqdm(range(1, len(from_start_data)), desc="Closing the positions are in Processing"):
        print(len(from_start_data[from_start_data['datetime'] <= from_start_data.iloc[t]["datetime"]]), " len to start")
        features = feature_extraction(processed_data=from_start_data[from_start_data['datetime'] <= from_start_data.iloc[t]["datetime"]], symbol=symbol, start=start, end=end, interval=interval)
        print(features)
        exit()
        # tqdm.write(f"Current datetime: {current_datetime}")
        # closing_open_positions(positions=positions, current=raw_data.iloc[t], commission=commission)


    return 0