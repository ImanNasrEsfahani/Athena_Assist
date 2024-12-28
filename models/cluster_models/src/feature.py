import pandas as pd
import pandas_ta as ta
import numpy as np

from .features.calculate_atr import calculate_atr
from .features.calculate_macd import calculate_macd
from .features.calculate_rsi import calculate_rsi
from .features.calculate_sma_ema_wma import calculate_sma, calculate_ema, calculate_wma
from .features.calculate_stochastic import calculate_stochastic
from .features.convert_to_upper_time_frame import convert_to_upper_time_frame
# from .features.cnadle_stick_pattern import check_candlestick_patterns

def pivotid(df1, l, n1, n2):  # n1 n2 before and after candle l
    if l - n1 < 0 or l + n2 >= len(df1):
        return 0

    pividlow = 1
    pividhigh = 1
    for i in range(l - n1, l + n2 + 1):
        if (df1.low[l] > df1.low[i]):
            pividlow = 0
        if (df1.high[l] < df1.high[i]):
            pividhigh = 0
    if pividlow and pividhigh:
        return 3
    elif pividlow:
        return 1
    elif pividhigh:
        return 2
    else:
        return 0


def RSIpivotid(df1, l, n1, n2):  # n1 n2 before and after candle l
    if l - n1 < 0 or l + n2 >= len(df1):
        return 0

    pividlow = 1
    pividhigh = 1
    for i in range(l - n1, l + n2 + 1):
        if (df1.RSI[l] > df1.RSI[i]):
            pividlow = 0
        if (df1.RSI[l] < df1.RSI[i]):
            pividhigh = 0
    if pividlow and pividhigh:
        return 3
    elif pividlow:
        return 1
    elif pividhigh:
        return 2
    else:
        return 0


def divsignal2(df, x, nbackcandles):
    backcandles = nbackcandles
    candleid = int(x.name)

    closp = np.array([])
    xxclos = np.array([])

    maxim = np.array([])
    minim = np.array([])
    xxmin = np.array([])
    xxmax = np.array([])

    maximRSI = np.array([])
    minimRSI = np.array([])
    xxminRSI = np.array([])
    xxmaxRSI = np.array([])

    for i in range(candleid - backcandles, candleid + 1):
        closp = np.append(closp, df.iloc[i].close)
        xxclos = np.append(xxclos, i)
        if df.iloc[i].pivot == 1:
            minim = np.append(minim, df.iloc[i].low)
            xxmin = np.append(xxmin, i)  # could be i instead df.iloc[i].name
        if df.iloc[i].pivot == 2:
            maxim = np.append(maxim, df.iloc[i].high)
            xxmax = np.append(xxmax, i)  # df.iloc[i].name
        if df.iloc[i].RSIpivot == 1:
            minimRSI = np.append(minimRSI, df.iloc[i].RSI)
            xxminRSI = np.append(xxminRSI, df.iloc[i].name)
        if df.iloc[i].RSIpivot == 2:
            maximRSI = np.append(maximRSI, df.iloc[i].RSI)
            xxmaxRSI = np.append(xxmaxRSI, df.iloc[i].name)

    slclos, interclos = np.polyfit(xxclos, closp, 1)

    if slclos > 1e-4 and (maximRSI.size < 2 or maxim.size < 2):
        return 0
    if slclos < -1e-4 and (minimRSI.size < 2 or minim.size < 2):
        return 0
    # signal decisions here !!!
    if slclos > 1e-4:
        if maximRSI[-1] < maximRSI[-2] and maxim[-1] > maxim[-2]:
            return 1
    elif slclos < -1e-4:
        if minimRSI[-1] > minimRSI[-2] and minim[-1] < minim[-2]:
            return 2
    else:
        return 0

import plotly.graph_objects as go
from plotly.subplots import make_subplots

def divsignal(df, x, nbackcandles):
    backcandles = nbackcandles
    candleid = int(x.name)

    maxim = np.array([])
    minim = np.array([])
    xxmin = np.array([])
    xxmax = np.array([])

    maximRSI = np.array([])
    minimRSI = np.array([])
    xxminRSI = np.array([])
    xxmaxRSI = np.array([])

    for i in range(candleid - backcandles, candleid + 1):
        if df.iloc[i].pivot == 1:
            minim = np.append(minim, df.iloc[i].low)
            xxmin = np.append(xxmin, i)  # could be i instead df.iloc[i].name
        if df.iloc[i].pivot == 2:
            maxim = np.append(maxim, df.iloc[i].high)
            xxmax = np.append(xxmax, i)  # df.iloc[i].name
        if df.iloc[i].RSIpivot == 1:
            minimRSI = np.append(minimRSI, df.iloc[i].RSI)
            xxminRSI = np.append(xxminRSI, df.iloc[i].name)
        if df.iloc[i].RSIpivot == 2:
            maximRSI = np.append(maximRSI, df.iloc[i].RSI)
            xxmaxRSI = np.append(xxmaxRSI, df.iloc[i].name)

    if maxim.size < 2 or minim.size < 2 or maximRSI.size < 2 or minimRSI.size < 2:
        return 0

    slmin, intercmin = np.polyfit(xxmin, minim, 1)
    slmax, intercmax = np.polyfit(xxmax, maxim, 1)
    slminRSI, intercminRSI = np.polyfit(xxminRSI, minimRSI, 1)
    slmaxRSI, intercmaxRSI = np.polyfit(xxmaxRSI, maximRSI, 1)

    dfpl = df

    if slmin > 1e-4 and slmax > 1e-4 and slmaxRSI < -0.1:
        fig = make_subplots(rows=2, cols=1)
        fig.append_trace(go.Candlestick(x=dfpl.index,
                                        open=dfpl['open'],
                                        high=dfpl['high'],
                                        low=dfpl['low'],
                                        close=dfpl['close']), row=1, col=1)
        fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                        marker=dict(size=4, color="MediumPurple"),
                        name="pivot", row=1, col=1)
        fig.add_trace(go.Scatter(x=xxmin, y=slmin * xxmin + intercmin, mode='lines', name='min slope'), row=1, col=1)
        fig.add_trace(go.Scatter(x=xxmax, y=slmax * xxmax + intercmax, mode='lines', name='max slope'), row=1, col=1)

        fig.append_trace(go.Scatter(x=dfpl.index, y=dfpl['RSI']), row=2, col=1)
        fig.add_scatter(x=dfpl.index, y=dfpl['RSIpointpos'], mode="markers",
                        marker=dict(size=2, color="MediumPurple"),
                        name="pivot", row=2, col=1)
        fig.add_trace(go.Scatter(x=xxminRSI, y=slminRSI * xxminRSI + intercminRSI, mode='lines', name='min slope'),
                      row=2,
                      col=1)
        fig.add_trace(go.Scatter(x=xxmaxRSI, y=slmaxRSI * xxmaxRSI + intercmaxRSI, mode='lines', name='max slope'),
                      row=2,
                      col=1)

        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.show()
        return 1
    elif slmin < -1e-4 and slmax < -1e-4 and slminRSI > 0.1:
        return 2
    else:
        return 0

def pointpos(x):
    if x['pivot'] == 1:
        return x['low'] - 1e-3
    elif x['pivot'] == 2:
        return x['high'] + 1e-3
    else:
        return np.nan

def RSIpointpos(x):
    if x['RSIpivot'] == 1:
        return x['RSI'] - 1
    elif x['RSIpivot'] == 2:
        return x['RSI'] + 1
    else:
        return np.nan

def feature_extraction(processed_data: pd.DataFrame, symbol: str, start: str, end: str, interval: str):
    print("feature_extraction")
    data = processed_data[42130:].copy()
    print(f"""len processed_data {len(data)}""")
    data.reset_index(drop=True, inplace=True)

    # Calculate RSI
    data.ta = ta
    data['RSI'] = data.ta.rsi(close=data['close'], length=14)

    # Finding Pivot points
    data['pivot'] = data.apply(lambda x: pivotid(data, x.name, 5, 5), axis=1)
    data['RSIpivot'] = data.apply(lambda x: RSIpivotid(data, x.name, 5, 5), axis=1)
    print(f""" RSI Pivot count {(data["RSIpivot"]==1).sum()} Pivot count {(data["RSIpivot"]==1).sum()}""")

    data['pointpos'] = data.apply(lambda row: pointpos(row), axis=1)
    data['RSIpointpos'] = data.apply(lambda row: RSIpointpos(row), axis=1)
    print(f""" RSI Pivot count {data[data.RSIpointpos==1].count()} Pivot count {data[data.pointpos==1].count()}""")
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    dfpl = data.tail(500)
    print(f""" len processed data {len(data)} len dfpl {len(dfpl)}""")

    fig = make_subplots(rows=2, cols=1)
    fig.append_trace(go.Candlestick(x=dfpl.index,
                                    open=dfpl['open'],
                                    high=dfpl['high'],
                                    low=dfpl['low'],
                                    close=dfpl['close']), row=1, col=1)

    fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers",
                    marker=dict(size=4, color="MediumPurple"),
                    name="pivot", row=1, col=1)

    fig.append_trace(go.Scatter(x=dfpl.index, y=dfpl['RSI']), row=2, col=1)
    fig.add_scatter(x=dfpl.index, y=dfpl['RSIpointpos'], mode="markers",
                    marker=dict(size=4, color="MediumPurple"),
                    name="pivot", row=2, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False)
    fig.show()

    print(data)

    splited_df = data.tail(500)
    splited_df.reset_index(drop=True, inplace=True)

    splited_df['divSignal'] = splited_df.apply(lambda row: divsignal(splited_df, row, 30), axis=1)
    splited_df['divSignal2'] = splited_df.apply(lambda row: divsignal2(splited_df, row, 30), axis=1)


    print(splited_df.iloc[-1], " splited_df.iloc[-1]")
    test = divsignal2(splited_df, splited_df.iloc[-1], 30)
    print(test)
    # divsignal2(processed_data[:500], 85, 5)
    print(splited_df)
    splited_df.to_csv(rf"test-iman.csv")

    exit("iman")
    return 0
    # Feature extraction
    features = feature_extraction_by_interval(data=processed_data, interval=interval)
    features_data = pd.concat([processed_data, features], axis=1)
    # print(features_data, " 1h")

    # Upper time frame feature extraction
    upper_timeframe = "4h"
    upper_timeframe_data = convert_to_upper_time_frame(data=processed_data, timeframe=upper_timeframe)
    features_upper_timeframe = feature_extraction_by_interval(data=upper_timeframe_data, interval=upper_timeframe)
    features_upper_timeframe_data = pd.concat([upper_timeframe_data, features_upper_timeframe], axis=1)
    # print(features_upper_timeframe_data, " 4h")

    # Merge
    if 'timestamp' in features_data.columns:
        features_data['timestamp'] = pd.to_datetime(features_data['timestamp'], utc=True)
        features_data.set_index('timestamp', inplace=True)

    if 'timestamp' in features_upper_timeframe_data.columns:
        features_upper_timeframe_data['timestamp'] = pd.to_datetime(features_upper_timeframe_data['timestamp'], utc=True)
        features_upper_timeframe_data.set_index('timestamp', inplace=True)

    merged_df = pd.merge(
        features_data,
        features_upper_timeframe_data,
        on='timestamp',
        how='left',
        suffixes=('', '_4h')
    ).ffill()
    merged_df["timestamp"] = merged_df.index
    merged_df["timestamp"] = pd.to_datetime(merged_df['timestamp'], utc=True)
    merged_df.reset_index(drop=True, inplace=True)
    merged_df = merged_df[merged_df['timestamp'] >= pd.to_datetime(start).tz_localize('UTC').normalize()]
    cols = ['timestamp'] + [col for col in merged_df.columns if col != 'timestamp']
    merged_df = merged_df.reindex(columns=cols)
    # print(merged_df, " merged 1h and 4h")

    return merged_df

def feature_extraction_by_interval(data: pd.DataFrame, interval: str):

    return pd.concat([
        # check_candlestick_patterns(data=data),
        calculate_stochastic(data=data, timeframe=interval, k_period=14, d_period=3),
        calculate_rsi(data=data, timeframe=interval, period=14),
        calculate_macd(data=data, timeframe=interval, fast_period=12, slow_period=26, signal_period=9),
        calculate_atr(data=data, timeframe=interval, period=14),
        # calculate_sma(data=data, timeframe=interval, column='close', periods=[10, 20, 50]),
        calculate_ema(data=data, timeframe=interval, column='close', periods=[10, 20, 50]),
        # calculate_wma(data=data, timeframe=interval, column='close', periods=[10, 20, 50]),
    ], axis=1)