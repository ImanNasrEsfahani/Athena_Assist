# Main script to run the entire pipeline
from tqdm import tqdm
from datetime import datetime, timezone, timedelta
import os
import pandas as pd
import argparse
import json
from pathlib import Path
import pytz

from src.display import plot_dendrogram, plot_histograms
from src.download_data import download_data
from src.data_preparation import prepare_data
from src.features.convert_to_upper_time_frame import convert_to_upper_time_frame
from src.filter import filtering_data, filter_by_working_hours
from src.label_data import label_data, position_creator, closing_open_positions
from src.feature import feature_extraction
from src.feature_selection import feature_selection
from src.model import train_model
from src.predict import predict_model
from src.test import test_model
from src.tools.tools import list_files, select_symbol, load_data_from_sqlite, load_data, get_last_month_from_database, \
    is_working_hours
from settings import settings

from sqlalchemy import create_engine

symbol =None
start =None
end =None

def main(action):
    global symbol, start, end

    # end = "2024-02-28"
    interval = settings.interval
    n_clusters = settings.n_clusters
    buffer_size = settings.buffer_size
    commission = settings.commission
    min_size_stop_loss = settings.min_size_stop_loss
    london_timezone = settings.london_timezone
    newyork_timezone = settings.newyork_timezone
    table_name = settings.table_name
    database_path = settings.database_path
    start_date_test = settings.start_date_test
    features = settings.features

    if action == "download":
        download_data(method="yfinance", symbol=symbol, start=start, end=end, interval=interval)

    elif action == "prepare":

        database = load_data_from_sqlite(table_name=table_name, database_path=database_path)
        database_1h = convert_to_upper_time_frame(data=database, timeframe="1h")

        converted_df = database_1h[database_1h['timestamp'] <= end + " 00:00:00"]

        prepare_data(data=converted_df, symbol=symbol, start=start, end=end, interval=interval)

    elif action == "filter":

        prepared_data = load_data(path=["data", "processed"], symbol=symbol, start=start, end=end, interval=interval)

        filtering_data(data=prepared_data, symbol=symbol, start=start, end=end, interval=interval,
                       london_timezone=london_timezone, newyork_timezone=newyork_timezone, buffer_size=buffer_size)

    elif action == "label":

        prepared_data = load_data(path=["data", "processed"], symbol=symbol, start=start, end=end, interval=interval)
        filtered_data = load_data(path=["data", "filtered"], symbol=symbol, start=start, end=end, interval=interval)

        label_data(real_time=prepared_data, filtered_time=filtered_data, symbol=symbol, start=start, end=end,
                   interval=interval, commission=commission, min_size_stop_loss=min_size_stop_loss, kinds=settings.kinds)

    elif action == "feature":

        prepared_data = load_data(path=["data", "processed"], symbol=symbol, start=start, end=end, interval=interval)

        df = feature_extraction(processed_data=prepared_data, symbol=symbol, start=start, end=end, interval=interval)
        df.to_csv(os.path.join("data", "featured", f"{symbol}_{start}_{end}_{interval}.csv"), index=False)

    elif action == "feature_selection":

        featured_data = load_data(path=["data", "featured"], symbol=symbol, start=start, end=end, interval=interval)

        grouped_features = feature_selection(data=featured_data, features=features, n_clusters=n_clusters)
        with open(os.path.join("data", "featured", f"{symbol}_{start}_{end}_{interval}_feature_selection.csv"),
                  'w') as f:
            json.dump(grouped_features, f, indent=4)

    elif action == "train":

        for kind in settings.kinds:
            positions = load_data(path=["data", "labeled"], symbol=symbol, start=start, end=end, interval=interval)
            closed_positions = positions[(positions["situation"] == 1) & (positions["kind"] == kind)]

            features = load_data(path=["data", "featured"], symbol=symbol, start=start, end=end, interval=interval)

            merged_df = closed_positions.merge(
                features,
                on='timestamp',
                how='left'
            )

            merged_df.to_csv(os.path.join("data", "train", f"{symbol}_{start}_{end}_{interval}.csv"), index=False)
            merged_df.loc[merged_df['result'] == -1, 'result'] = 0
            merged_df.loc[merged_df['result'] >= 2, 'result'] = 1
            merged_df = merged_df.dropna()

            # analysis(closed_positions)
            train_model(positions=merged_df, features=features, kind=kind, symbol=symbol, start=start, end=end,
                        interval=interval)

    elif action == "predict":
        print("predict")
        filter_data = load_data(path=["data", "filter"], symbol=symbol, start=start, end=end, interval=interval)
        samples = filter_data.sample(10)
        predict_model(data=samples, path=rf"models", models="",  symbol=symbol, start=start, end=end, interval=interval)

    elif action == "test":

        database = load_data_from_sqlite(table_name=table_name, database_path=database_path)
        database_1h = convert_to_upper_time_frame(data=database, timeframe="1h")
        if 'timestamp' in database.columns:
            database.set_index('timestamp', inplace=True, drop=False)
            database.index = pd.to_datetime(database.index)
        if 'timestamp' in database_1h.columns:
            database_1h.set_index('timestamp', inplace=True, drop=False)
            database_1h.index = pd.to_datetime(database_1h.index)

        # Then filter the rows
        split_database_1h = database_1h[database_1h.index > pd.Timestamp(start_date_test, tz='UTC')]

        positions = pd.DataFrame()

        # total_iterations = len(split_database_1h)
        # # Iterate over each row in the DataFrame
        # for index, row in tqdm(split_database_1h.iterrows(), total=total_iterations, desc="Back-test",
        #                        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {percentage:3.2f}% ', leave=False):
        #     if not is_working_hours(row.name):
        #         continue
        #
        #     # print(row.name, "Now")
        #     # Calculate the date range
        #     start_date = pd.to_datetime(row.name, utc=True) - timedelta(days=31)
        #     end_date = pd.to_datetime(row.name, utc=True)
        #
        #     # Filter the database
        #     last_month_to_now_1h = database_1h.loc[start_date:end_date]
        #
        #     predictions = {}
        #
        #     for kind in ["long", "short"]:
        #         avg_cluster = 0
        #         models_list = list_files(
        #             directory=os.path.join(Path(__file__).parent.absolute(), 'models'),
        #             pattern=f'{"EURUSD=X"}_{settings.start}_{settings.end}_{settings.interval}_{kind}',
        #             extension=".joblib")
        #
        #         prediction = predict_model(data=last_month_to_now_1h,
        #                                    path=os.path.join(Path(__file__).parent.absolute(), 'models'),
        #                                    models=models_list,
        #                                    symbol="EURUSD=X",
        #                                    start=settings.start,
        #                                    end=settings.end,
        #                                    interval=settings.interval)
        #         # predictions[kind] = prediction
        #         # Extract abbreviations into lists based on cluster value
        #         cluster_0_abbrs = [item['abbr'] for item in prediction if item['cluster'] == 0]
        #         cluster_1_abbrs = [item['abbr'] for item in prediction if item['cluster'] == 1]
        #         # print(f""" result 1: {cluster_1_abbrs} result 0: {cluster_0_abbrs}""")
        #
        #         avg_cluster = round(sum(m['cluster'] for m in prediction) / len(prediction), 2)
        #         # print(f""" kind: {kind}, Average {avg_cluster}""")
        #         if avg_cluster >= 0.5:
        #             # open position for current
        #             # print(type(kind), " type kind ", kind)
        #             # print(kind == "long", " if")
        #             positions = pd.concat(
        #                 [positions, position_creator(data=last_month_to_now_1h, t=-1, commission=commission,
        #                                              position_type=kind,
        #                                              min_size_stop_loss=min_size_stop_loss)])
        #             # if kind == "long":
        #             #     # print(f""" kind {kind}""")
        #             #     positions = pd.concat(
        #             #         [positions, position_creator(data=last_month_to_now_1h, t=-1, commission=commission,
        #             #                                      position_type=kind,
        #             #                                      min_size_stop_loss=min_size_stop_loss)])
        #             # else:
        #             #     positions = pd.concat(
        #             #         [positions, position_creator(data=last_month_to_now_1h, t=-1, commission=commission,
        #             #                                      position_type="short",
        #             #                                      min_size_stop_loss=min_size_stop_loss)])
        #
        # print(positions, "positions")
        # positions.to_csv(os.path.join("models", "results", f"positions.csv"))
        positions = pd.DataFrame(pd.read_csv(os.path.join("models", "results", f"positions.csv")))
        print(positions)
        print(f""" len: {len(positions)}""")

        # closing all open positions in real time beyond of London and New york working hours in 24 hours
        # for _, current in tqdm(database_1h.iterrows(), desc="Closing the positions are in Processing",
        #               bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}  {percentage:3.2f}% '):
        # for _, current in database_1h.iterrows():
        for row in tqdm(split_database_1h.itertuples(index=False), total=len(split_database_1h), desc="Closing the positions are in Processing",
                      bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}  {percentage:3.2f}% '):
            # print(f"row: {row}")
            # tqdm.write(f"Current datetime: {current}")
            closing_open_positions(positions=positions, current=row, commission=commission)

        print(positions, "positions")
        positions.to_csv(os.path.join("models", "results", f"positions2.csv"))

        exit()

        file = list_files(os.path.join("data", "processed", f"{symbol}_{start}_{end}_{interval}"))[-1]
        print(f""" raw data file name {file}""")
        processed_data = pd.DataFrame(pd.read_csv(os.path.join("data", "processed", f"{file}")))

        test_model(raw_data=processed_data, symbol=symbol, start=start, end=end, interval=interval)

    elif action == "display":
        kind = "long"
        positions = load_data(path=["data", "labeled"], symbol=symbol, start=start, end=end, interval=interval)
        closed_positions = positions[(positions["situation"] == 1) & (positions["kind"] == kind)]

        features = load_data(path=["data", "featured"], symbol=symbol, start=start, end=end, interval=interval)

        merged_df = closed_positions.merge(
            features,
            on='timestamp',
            how='left'
        )

        merged_df.to_csv(os.path.join("data", "train", f"{symbol}_{start}_{end}_{interval}.csv"), index=False)
        merged_df.loc[merged_df['result'] == -1, 'result'] = 0
        merged_df.loc[merged_df['result'] >= 2, 'result'] = 1
        merged_df = merged_df.dropna()

        columns = ['stochastic%K_1h', 'stochastic%D_1h', "stochastic_signal_1h", "RSI_1h", "MACD_1h", 'Signal_Line_1h',
                   'MACD_Histogram_1h', 'ATR_1h', 'stochastic%K_4h', 'stochastic%D_4h', "stochastic_signal_4h",
                   'RSI_4h', 'MACD_4h', 'Signal_Line_4h', 'MACD_Histogram_4h', 'ATR_4h',
                   'EMA_10_1h', 'EMA_20_1h', 'EMA_50_1h', 'EMA_10_4h', 'EMA_20_4h', 'EMA_50_4h']
        # Usage example:
        # Without condition
        # plot_histograms(merged_df, columns)

        # With condition
        plot_histograms(merged_df, columns, condition_column='result', condition_value=1)
        exit()
        # file = list_files(os.path.join("data", "processed"), f"{symbol}_{start}_{end}_{interval}")[-1]
        # print(f""" raw data file name {file}""")
        # processed_data = pd.DataFrame(pd.read_csv(os.path.join("data", "processed" , f"{file}")))
        #
        # file = list_files(os.path.join("data", "labeled"), f"{symbol}_{start}_{end}_{interval}_positions")[-1]
        # print(f""" positions file name {file}""")
        # labeled = pd.DataFrame(pd.read_csv(os.path.join("data", "labeled", f"{file}"))

        # plot_candlestick(raw_data)
        # plot_candlestick_with_positions(data=processed_data, positions=labeled, kind="long")

        file = list_files(os.path.join("data", "featured", f"{symbol}_{start}_{end}_{interval}"))[-1]
        print(f""" positions file name {file}""")
        featured_data = pd.DataFrame(pd.read_csv(os.path.join("data", "featured", f"{file}")))

        plot_dendrogram(data=featured_data)

    elif action == "all":
        symbol = select_symbol()

        download_data(method="yfinance", symbol=symbol, start=start, end=end, interval=interval)
        prepare_data(symbol=symbol, start=start, end=end, interval=interval)
        filtering_data(symbol=symbol, start=start, end=end, interval=interval, london_timezone=london_timezone,
                       newyork_timezone=newyork_timezone, buffer_size=buffer_size)
        label_data(symbol=symbol, start=start, end=end, interval=interval, commission=commission,
                   min_size_stop_loss=min_size_stop_loss)

    else:
        print(
            "Invalid action. Please choose from: download, prepare, filter, feature_selection_algorithms, train, display, predict.")

    # save_model(model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Machine Learning Workflow Manager")
    # parser.add_argument('--task', default='ctdet', help='Specify the task to perform')

    # Adding an argument for the action to perform
    parser.add_argument(
        'action',
        choices=['download', 'prepare', 'filter', 'label', 'feature', 'feature_selection', 'train', 'display',
                 'predict', 'test', 'all'],
        help="Specify the action to perform."
    )
    parser.add_argument('--symbol', type=str, help="Specify the symbol to use")
    parser.add_argument('--start', type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
                        help="Start date in YYYY-MM-DD format")
    parser.add_argument('--end', type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
                        help="End date in YYYY-MM-DD format")

    args = parser.parse_args()

    symbol = args.symbol if args.symbol else select_symbol()
    start = args.start if args.start else settings.start
    end = args.end if args.end else settings.end

    main(args.action)
