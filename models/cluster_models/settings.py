
class Settings:
    start = "2016-12-02"
    end = "2024-01-01"
    # end = "2024-02-28"
    interval = "1h"
    n_clusters = 7
    buffer_size = 0
    commission = 0.00005
    min_size_stop_loss = 0.0005
    london_timezone = True
    newyork_timezone = True
    table_name = 'EURUSD_M15'
    database_path = "market.db"
    start_date_test = '2024-01-01'
    features = ['candle_stick_pattern', 'stochastic%K_1h', 'stochastic%D_1h', "stochastic_signal_1h", "RSI_1h", "MACD_1h", 'Signal_Line_1h',
                'MACD_Histogram_1h', 'ATR_1h', 'stochastic%K_4h', 'stochastic%D_4h', "stochastic_signal_4h",
                'RSI_4h', 'MACD_4h', 'Signal_Line_4h', 'MACD_Histogram_4h', 'ATR_4h',
                'EMA_10_1h', 'EMA_20_1h', 'EMA_50_1h', 'EMA_10_4h', 'EMA_20_4h', 'EMA_50_4h']

    kinds = ["long", "short"]

    bullish_reversal_patterns = {
        'CDL3WHITESOLDIERS': 7,
        'CDLMORNINGSTAR': 44,
        'CDLMORNINGDOJISTAR': 43,
        'CDLPIERCING': 46,
        'CDLABANDONEDBABY': 8,
        'CDLHAMMER': 24,
        'CDLINVERTEDHAMMER': 34,
        'CDLHARAMI': 26,
        'CDLHARAMICROSS': 27,
        'CDLHOMINGPIGEON': 31,
        'CDLLADDERBOTTOM': 37,
        'CDLMATCHINGLOW': 41,
        'CDLMATHOLD': 42,
        'CDLTHRUSTING': 57,
        'CDLUNIQUE3RIVER': 59,
        'CDLBELTHOLD': 10,
        'CDLBREAKAWAY': 11
    }

    bearish_reversal_patterns = {
        'CDL3BLACKCROWS': 2,
        'CDL2CROWS': 1,
        'CDLEVENINGSTAR': 21,
        'CDLEVENINGDOJISTAR': 20,
        'CDLDARKCLOUDCOVER': 15,
        'CDLSHOOTINGSTAR': 50,
        'CDLHANGINGMAN': 25,
        'CDLHARAMI': 26,
        'CDLHARAMICROSS': 27,
        'CDLIDENTICAL3CROWS': 32,
        'CDLUPSIDEGAP2CROWS': 60,
        'CDLBELTHOLD': 10,
        'CDLBREAKAWAY': 11
    }

    continuation_patterns = {
        'CDL3LINESTRIKE': 4,
        'CDL3OUTSIDE': 5,
        'CDLSEPARATINGLINES': 49,
        'CDLXSIDEGAP3METHODS': 61,
        'CDLRISEFALL3METHODS': 48
    }

    indecision_patterns = {
        'CDLDOJI': 16,
        'CDLSPINNINGTOP': 52,
        'CDLHIGHWAVE': 28,
        'CDLLONGLEGGEDDOJI': 38,
        'CDLRICKSHAWMAN': 47,
        'CDLGRAVESTONEDOJI': 23,
        'CDLDRAGONFLYDOJI': 18,
        'CDLDOJISTAR': 17
    }

    other_patterns = {
        'CDL3INSIDE': 3,
        'CDLADVANCEBLOCK': 9,
        'CDLCLOSINGMARUBOZU': 12,
        'CDLCONCEALBABYSWALL': 13,
        'CDLCOUNTERATTACK': 14,
        'CDLENGULFING': 19,
        'CDLGAPSIDESIDEWHITE': 22,
        'CDLHIKKAKE': 29,
        'CDLHIKKAKEMOD': 30,
        'CDLINNECK': 33,
        'CDLKICKING': 35,
        'CDLKICKINGBYLENGTH': 36,
        'CDLLONGLINE': 39,
        'CDLMARUBOZU': 40,
        'CDLONNECK': 45,
        'CDLSHORTLINE': 51,
        'CDLSTALLEDPATTERN': 53,
        'CDLSTICKSANDWICH': 54
    }

    missed_patterns = {
        "CDL3STARSINSOUTH": 6,
        "CDLTAKURI": 55,
        "CDLTASUKIGAP": 56,
        "CDLTRISTAR": 58
    }

    pattern_codes = bullish_reversal_patterns | bearish_reversal_patterns | continuation_patterns | indecision_patterns | other_patterns | missed_patterns

settings = Settings()

# pattern_codes = {
#     'CDL2CROWS': 1,
#     'CDL3BLACKCROWS': 2,
#     'CDL3INSIDE': 3,
#     'CDL3LINESTRIKE': 4,
#     'CDL3OUTSIDE': 5,
#     'CDL3STARSINSOUTH': 6,
#     'CDL3WHITESOLDIERS': 7,
#     'CDLABANDONEDBABY': 8,
#     'CDLADVANCEBLOCK': 9,
#     'CDLBELTHOLD': 10,
#     'CDLBREAKAWAY': 11,
#     'CDLCLOSINGMARUBOZU': 12,
#     'CDLCONCEALBABYSWALL': 13,
#     'CDLCOUNTERATTACK': 14,
#     'CDLDARKCLOUDCOVER': 15,
#     'CDLDOJI': 16,
#     'CDLDOJISTAR': 17,
#     'CDLDRAGONFLYDOJI': 18,
#     'CDLENGULFING': 19,
#     'CDLEVENINGDOJISTAR': 20,
#     'CDLEVENINGSTAR': 21,
#     'CDLGAPSIDESIDEWHITE': 22,
#     'CDLGRAVESTONEDOJI': 23,
#     'CDLHAMMER': 24,
#     'CDLHANGINGMAN': 25,
#     'CDLHARAMI': 26,
#     'CDLHARAMICROSS': 27,
#     'CDLHIGHWAVE': 28,
#     'CDLHIKKAKE': 29,
#     'CDLHIKKAKEMOD': 30,
#     'CDLHOMINGPIGEON': 31,
#     'CDLIDENTICAL3CROWS': 32,
#     'CDLINNECK': 33,
#     'CDLINVERTEDHAMMER': 34,
#     'CDLKICKING': 35,
#     'CDLKICKINGBYLENGTH': 36,
#     'CDLLADDERBOTTOM': 37,
#     'CDLLONGLEGGEDDOJI': 38,
#     'CDLLONGLINE': 39,
#     'CDLMARUBOZU': 40,
#     'CDLMATCHINGLOW': 41,
#     'CDLMATHOLD': 42,
#     'CDLMORNINGDOJISTAR': 43,
#     'CDLMORNINGSTAR': 44,
#     'CDLONNECK': 45,
#     'CDLPIERCING': 46,
#     'CDLRICKSHAWMAN': 47,
#     'CDLRISEFALL3METHODS': 48,
#     'CDLSEPARATINGLINES': 49,
#     'CDLSHOOTINGSTAR': 50,
#     'CDLSHORTLINE': 51,
#     'CDLSPINNINGTOP': 52,
#     'CDLSTALLEDPATTERN': 53,
#     'CDLSTICKSANDWICH': 54,
#     'CDLTAKURI': 55,
#     'CDLTASUKIGAP': 56,
#     'CDLTHRUSTING': 57,
#     'CDLTRISTAR': 58,
#     'CDLUNIQUE3RIVER': 59,
#     'CDLUPSIDEGAP2CROWS': 60,
#     'CDLXSIDEGAP3METHODS': 61
# }
