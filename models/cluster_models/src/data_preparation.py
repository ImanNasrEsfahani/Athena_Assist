from .tools import list_files

import os
import pandas as pd
import numpy as np
from joblib import load, dump


def prepare_data(data: pd.DataFrame, symbol: str, start: str, end: str, interval: str):

    len_before_preparation = len(data)

    # Step 1: Remove rows with NaN values
    data.dropna(inplace=True)

    # Step 2: Remove rows with zero values
    # raw_data = raw_data[(raw_data != 0).all(axis=1)]

    # Step 3: round all the numbers
    raw_data = data.round(5)

    print(
        f"""Data has been save after preparation for removing NaN and zero values. length Before {len_before_preparation} after {len(raw_data)}""")

    raw_data.to_csv(os.path.join("data", "processed", f"{symbol}_{start}_{end}_{interval}.csv"), index=False)

    return 0
