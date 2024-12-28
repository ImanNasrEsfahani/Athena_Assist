import pandas as pd
import pandas_ta as ta
import numpy as np
import talib

# Register the pandas-ta extension
pd.DataFrame.ta = ta
pattern_codes = {
    'CDL_2CROWS': 1,
    'CDL_3BLACKCROWS': 2,
    'CDL_3INSIDE': 3,
    'CDL_3LINESTRIKE': 4,
    'CDL_3OUTSIDE': 5,
    'CDL_3STARSINSOUTH': 6,
    'CDL_3WHITESOLDIERS': 7,
    'CDL_ABANDONEDBABY': 8,
    'CDL_ADVANCEBLOCK': 9,
    'CDL_BELTHOLD': 10,
    'CDL_BREAKAWAY': 11,
    'CDL_CLOSINGMARUBOZU': 12,
    'CDL_CONCEALBABYSWALL': 13,
    'CDL_COUNTERATTACK': 14,
    'CDL_DARKCLOUDCOVER': 15,
    'CDL_DOJI_10_0.1': 16,
    'CDL_DOJISTAR': 17,
    'CDL_DRAGONFLYDOJI': 18,
    'CDL_ENGULFING': 19,
    'CDL_EVENINGDOJISTAR': 20,
    'CDL_EVENINGSTAR': 21,
    'CDL_GAPSIDESIDEWHITE': 22,
    'CDL_GRAVESTONEDOJI': 23,
    'CDL_HAMMER': 24,
    'CDL_HANGINGMAN': 25,
    'CDL_HARAMI': 26,
    'CDL_HARAMICROSS': 27,
    'CDL_HIGHWAVE': 28,
    'CDL_HIKKAKE': 29,
    'CDL_HIKKAKEMOD': 30,
    'CDL_HOMINGPIGEON': 31,
    'CDL_IDENTICAL3CROWS': 32,
    'CDL_INNECK': 33,
    'CDL_INVERTEDHAMMER': 34,
    'CDL_KICKING': 35,
    'CDL_KICKINGBYLENGTH': 36,
    'CDL_LADDERBOTTOM': 37,
    'CDL_LONGLEGGEDDOJI': 38,
    'CDL_LONGLINE': 39,
    'CDL_MARUBOZU': 40,
    'CDL_MATCHINGLOW': 41,
    'CDL_MATHOLD': 42,
    'CDL_MORNINGDOJISTAR': 43,
    'CDL_MORNINGSTAR': 44,
    'CDL_ONNECK': 45,
    'CDL_PIERCING': 46,
    'CDL_RICKSHAWMAN': 47,
    'CDL_RISEFALL3METHODS': 48,
    'CDL_SEPARATINGLINES': 49,
    'CDL_SHOOTINGSTAR': 50,
    'CDL_SHORTLINE': 51,
    'CDL_SPINNINGTOP': 52,
    'CDL_STALLEDPATTERN': 53,
    'CDL_STICKSANDWICH': 54,
    'CDL_TAKURI': 55,
    'CDL_TASUKIGAP': 56,
    'CDL_THRUSTING': 57,
    'CDL_TRISTAR': 58,
    'CDL_UNIQUE3RIVER': 59,
    'CDL_UPSIDEGAP2CROWS': 60,
    'CDL_XSIDEGAP3METHODS': 61
}

def check_candlestick_patterns(data: pd.DataFrame):

    # Ensure the DataFrame has the required columns
    required_columns = ['open', 'high', 'low', 'close']

    if not all(col in data.columns for col in required_columns):
        raise ValueError("DataFrame must have 'Open', 'High', 'Low', and 'Close' columns")

    # Get help about pandas-ta
    # help(df.ta)

    # List all available indicators
    # df.ta.indicators()

    # Use pandas-ta to check for candlestick patterns
    patterns = data.ta.cdl_pattern(open_=data['open'], high=data['high'], low=data['low'], close=data['close'], name="all")
    df = pd.DataFrame()
    df["candle_stick_pattern"] = patterns.apply(assign_pattern_code, axis=1)

    return df

def assign_pattern_code(row):
    for pattern, code in pattern_codes.items():
        if row[pattern] != 0:
            return code
    return 0  # No pattern detected

# import talib
# import pandas as pd
# from typing import Tuple, List
#
# def identify_candlestick_patterns(df: pd.DataFrame) -> List[Tuple[int, str]]:
#     # Ensure the DataFrame has the required columns
#     required_columns = ['Open', 'High', 'Low', 'Close']
#     if not all(col in df.columns for col in required_columns):
#         raise ValueError("DataFrame must have 'Open', 'High', 'Low', and 'Close' columns")
#
#     # Dictionary to store pattern functions, their codes, and labels
#     patterns = {
#         talib.CDLDOJI: (1, 'DOJI'),
#         talib.CDLENGULFING: (2, 'ENGULFING'),
#         talib.CDLHAMMER: (3, 'HAMMER'),
#         talib.CDLHARAMI: (4, 'HARAMI'),
#         talib.CDLMORNINGSTAR: (5, 'MORNING_STAR'),
#         talib.CDLEVENINGSTAR: (6, 'EVENING_STAR'),
#         talib.CDLSHOOTINGSTAR: (7, 'SHOOTING_STAR'),
#         talib.CDLHANGINGMAN: (8, 'HANGING_MAN'),
#         talib.CDLINVERTEDHAMMER: (9, 'INVERTED_HAMMER'),
#         talib.CDLPIERCING: (10, 'PIERCING_LINE'),
#         talib.CDL3WHITESOLDIERS: (11, 'THREE_WHITE_SOLDIERS'),
#         talib.CDLDRAGONFLYDOJI: (12, 'DRAGONFLY_DOJI'),
#         talib.CDLGRAVESTONEDOJI: (13, 'GRAVESTONE_DOJI'),
#         talib.CDLDARKCLOUDCOVER: (14, 'DARK_CLOUD_COVER'),
#         talib.CDL3BLACKCROWS: (15, 'THREE_BLACK_CROWS')
#     }
#
#     identified_patterns = []
#
#     # Check for each pattern
#     for pattern_func, (code, label) in patterns.items():
#         result = pattern_func(df['Open'], df['High'], df['Low'], df['Close'])
#         if any(result != 0):
#             identified_patterns.append((code, label))
#
#     return identified_patterns if identified_patterns else [(0, 'NO_PATTERN')]