# noinspection PyUnresolvedReferences
# from models.cluster_models.src.tools.tools import load_data


import os
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from pandas import Timestamp


def label_data(real_time: pd.DataFrame, filtered_time: pd.DataFrame, symbol: str, start: str, end: str, interval: str,
               commission: float, min_size_stop_loss: float, kinds: list):
    data = filtered_time[filtered_time['timestamp'] >= start]

    columns = {"kind": "string",
               "timestamp": "datetime64[ns, UTC]",
               "open": "float64",
               "sl": "float64",
               "tp": "float64",
               "exit_datetime": "datetime64[ns, UTC]",
               "exit_price": "float64",
               "result": "byte",
               "hold_position": "int64",
               "profit/loss": "float64",
               "stop_distance": "float64",
               "situation": "byte"
               }
    positions = pd.DataFrame([], columns=list(columns.keys()))
    positions = positions.astype(columns)

    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # Make all open positions in the filtered date time for example London and New york working hours
    for row in tqdm(data.itertuples(index=True), total=len(data), desc="Creating positions are in Processing",
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {percentage:3.2f}% '):
        if row.Index >= 3:  # Ensure there are at least two previous candles
            new_positions = []
            for kind in kinds:
                new_position = position_creator(data=data, t=row.Index, commission=commission, position_type=kind, min_size_stop_loss=min_size_stop_loss)
                new_positions.append(new_position)
            positions = pd.concat([positions] + new_positions, ignore_index=True)

    positions.to_csv(os.path.join("data", "labeled", f"{symbol}_{start}_{end}_{interval}.csv"), index=False)
    # positions = load_data(path=["data", "labeled"], symbol=symbol, start=start, end=end, interval=interval)

    # closing all open positions in real time beyond of London and New york working hours in 24 hours
    for row in tqdm(real_time.itertuples(index=False), total=len(real_time), desc="Closing the positions are in Processing",
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}  {percentage:3.2f}% ', leave=True):
        closing_open_positions(positions=positions, current=row, commission=commission)

    positions = positions[positions['result'] != 0]
    positions = positions.reset_index(drop=True)
    print(positions, "positions")
    positions.to_csv(os.path.join("data", "labeled", f"{symbol}_{start}_{end}_{interval}.csv"), index=False)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return 0


def update_position(positions: pd.DataFrame, position: tuple, current: tuple, commission: float):

    duration_minute = (Timestamp(current.timestamp) - Timestamp(position.timestamp)).total_seconds() / 60

    # # Main loop to process both long and short positions
    # for kind in ['long', 'short']:
    #     mask = (positions['kind'] == kind) & (positions['situation'] == 0)
    #     for idx in positions[mask].index:
    #         # position = positions.loc[idx]
    #         handle_position(positions=positions, position=position, current=current, duration_minute=duration_minute, commission=commission)

    # Handle long positions
    if position.kind == 'long' and position.situation == 0:
        if current.low <= position.sl:
            positions.loc[position.Index, ["situation", "hold_position", "exit_datetime", "exit_price", "profit/loss"]] = [
                1,
                duration_minute,
                current.timestamp,
                position.sl,
                round(position.sl - position.open, 5)
            ]
            if positions.at[position.Index, "result"] == 0:
                positions.at[position.Index, "result"] = -1

        elif current.close >= position.tp:
            multiplier = 2
            while True:
                positions.at[position.Index, "sl"] = position.open + multiplier * position.stop_distance + commission
                positions.at[position.Index, "result"] = multiplier
                multiplier += 1
                if (multiplier * position.stop_distance + position.open) > current.close:
                    break

    # Handle short positions
    elif position.kind == 'short' and position.situation == 0:
        if current.high >= position.sl:
            positions.loc[position.Index, ["situation", "hold_position", "exit_datetime", "exit_price", "profit/loss"]] = [
                1,
                duration_minute,
                current.timestamp,
                position.sl,
                round(position.open - position.sl, 5)
            ]
            if positions.at[position.Index, "result"] == 0:
                positions.at[position.Index, "result"] = -1

        elif current.low <= position.tp:
            multiplier = 2
            while True:
                positions.at[position.Index, "sl"] = position.open - multiplier * position.stop_distance - commission
                positions.at[position.Index, "result"] = multiplier
                multiplier += 1
                if (multiplier * position.stop_distance - position.open) < current.close:
                    break

    return 0


def closing_open_positions(positions: pd.DataFrame, current: tuple, commission: float):
    positions["timestamp"] = pd.to_datetime(positions["timestamp"])

    filtered_positions = positions[
        (positions["situation"] == 0) & (positions["timestamp"] < current.timestamp)]

    for row in tqdm(filtered_positions.itertuples(index=True), total=len(filtered_positions), desc="Closing open positions in each real time",
                      bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}  {percentage:3.2f}% ', leave=False):

        update_position(positions=positions, position=row, current=current, commission=commission)

    return 0


def position_creator(data: pd.DataFrame, t: int, commission: float, position_type: str, min_size_stop_loss):
    assert position_type in ('long', 'short'), f"Invalid position type: {position_type}"
    """
    Create a position DataFrame based on the specified position type (long or short).

    Parameters:
    data (pd.DataFrame): The input DataFrame containing market data.
    t (int): The current index in the DataFrame.
    commission (float): The commission to consider for stop loss and take profit calculations.
    position_type (str): The type of position ('long' or 'short').

    Returns:
    pd.DataFrame: A DataFrame containing the position details or an empty DataFrame if conditions are not met.
    """

    open_price = data.iloc[t]['close']

    if position_type == 'long':
        min_low = data.iloc[t]['low']
        for i in range(1, 3):  # This will check t, t-1 and t-2
            min_low = min(min_low, data.iloc[t - i]['low'])
        stop_loss = min_low - commission
        take_profit = open_price + abs(open_price - stop_loss) * 2 + commission
    else:
        max_high = data.iloc[t]['high']
        for i in range(1, 3):  # This will check t, t-1 and t-2
            max_high = max(max_high, data.iloc[t - i]['high'])
        stop_loss = max_high + commission
        take_profit = open_price - abs(stop_loss - open_price) * 2 - commission

    if not min_size_stop_loss < abs(stop_loss - open_price) < 5 * min_size_stop_loss:
        return pd.DataFrame()

    return pd.DataFrame({
        "kind":             [position_type],
        "timestamp":        [data.iloc[t].get("timestamp", data.index[t])],
        "open":             [round(open_price, 5)],
        "sl":               [round(stop_loss, 5)],
        "tp":               [round(take_profit, 5)],
        "result":           [0],
        "hold_position":    [0],
        "profit/loss":      [0],
        "stop_distance":    [round(abs(stop_loss - open_price),5)],
        "situation":        [0],
    })


def handle_position(positions: pd.DataFrame, position: tuple, current: tuple, duration_minute: int, commission: float):
    if position.situation != 0:
        return

    is_long = position.kind == 'long'
    closing_condition = current.low <= position.sl if is_long else current.high >= position.sl
    trailing_condition = current.close >= position.tp if is_long else current.low <= position.tp

    profit_calc = (round(position.sl - position.open, 5)) if is_long else (round(position.open - position.sl, 5))

    if closing_condition:
        positions.loc[position.Index, ["situation", "hold_position", "exit_datetime", "exit_price", "profit/loss"]] = [
            1, duration_minute, current.timestamp, position.sl, profit_calc
        ]
        if positions.at[position.Index, "result"] == 0:
            positions.at[position.Index, "result"] = -1

    if trailing_condition:
        multiplier = 2
        while True:
            new_sl = position.open + (multiplier * position.stop_distance * (1 if is_long else -1)) + (commission * (1 if is_long else -1))
            positions.at[position.Index, "sl"] = new_sl
            positions.at[position.Index, "result"] = multiplier
            multiplier += 1
            if (multiplier * position.stop_distance + position.open > current.close) if is_long else (multiplier * position.stop_distance - position.open < current.close):
                break



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
