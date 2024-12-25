import pandas as pd
import pytz

from src.log_config import loggerUpdater
from src.updater.models import EURUSD_M15
from src.updater.crud import get_last_row, add_yahoo_data_to_db, get_last_month
from src.updater.utils import fetch_yahoo_finance_data, format_position_dict_for_telegram_message, \
    fetch_tiingo_finance_data, position_creator, calculate_position_size, convert_to_upper_time_frame, is_data_update
from src.updater.models.eurusd_m15 import EURUSD_M15_Pydantic
from models.cluster_models.prediction import prediction as classifier_prediction
from src.app.notifications import run_notify_active_users

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from datetime import datetime, timedelta


def start_scheduler():
    scheduler = AsyncIOScheduler()

    # yahoo_updater
    scheduler.add_job(func=yahoo_updater,
                      trigger='cron',
                      name="updater price from yahoo",
                      minute='2,16,31,46',
                      day_of_week='mon-fri',
                      timezone='Europe/London'
                      )

    # prediction
    scheduler.add_job(func=prediction_hourly,
                      trigger='cron',
                      name="prediction_hourly",
                      day_of_week='mon-fri',
                      hour='7-21',
                      minute='3',
                      # minute='*',
                      timezone='Europe/London'
                      )

    # Notifications
    scheduler.add_job(func=notifications_hourly,
                      trigger='cron',
                      name="prediction_hourly",
                      day_of_week='mon-fri',
                      hour='7-21',
                      minute='4,18,34,48',
                      # minute='*',
                      timezone='Europe/London'
                      )

    # account manager updater
    scheduler.add_job(func=daily_report,
                      trigger='cron',
                      name="prediction_hourly",
                      day_of_week='mon-fri',
                      hour='21',
                      minute='0',
                      # minute='*',
                      timezone='Europe/London'
                      )

    scheduler.add_job(func=weekly_report,
                      trigger='cron',
                      name="prediction_hourly",
                      day_of_week='fri',
                      hour='21',
                      minute='0',
                      # minute='*',
                      timezone='Europe/London'
                      )

    # start all cron jobs
    scheduler.start()
    return scheduler


async def notifications_hourly():
    loggerUpdater.debug("notifications_hourly")

    pass


# Daily report
async def daily_report():
    loggerUpdater.debug("Daily report")

    message = f"""
    *Daily Report*
    
    """
    await run_notify_active_users(message=message)


async def weekly_report():
    loggerUpdater.debug("Weekly report")

    message = f"""
    *Weekly Report*

    """
    await run_notify_active_users(message=message)


# prediction function
async def prediction_hourly():
    loggerUpdater.debug("prediction hourly")

    if not is_data_update(model=EURUSD_M15, pydantic_model=EURUSD_M15_Pydantic, max_time_difference=18):
        time_difference = round(
            (datetime.now() - get_last_row(EURUSD_M15, EURUSD_M15_Pydantic)[0].timestamp).total_seconds() / 60)
        loggerUpdater.error("last date time in database in EuroUSD has more than %s minute difference from now: %s",
                            time_difference, datetime.now())
        await run_notify_active_users(
            message=f"last date time in database in EuroUSD has more than {time_difference} minute difference from now: {datetime.now()}")
        return 0

    rows = pd.DataFrame(get_last_month(EURUSD_M15, EURUSD_M15_Pydantic))
    rows_1h = convert_to_upper_time_frame(data=rows, timeframe="1h")
    loggerUpdater.debug(rows_1h)
    predictions = await classifier_prediction(data=rows_1h)

    # predictions = {}
    for position_type in ["long", "short"]:
        prediction = predictions[position_type]

        # Calculate average score
        avg_cluster = round(sum(m['cluster'] for m in prediction) / len(prediction), 2)
        # Extract abbreviations into lists based on cluster value
        cluster_0_abbrs = [item['abbr'] for item in prediction if item['cluster'] == 0]
        cluster_1_abbrs = [item['abbr'] for item in prediction if item['cluster'] == 1]

        # Convert lists to comma-separated strings
        cluster_0_string = ', '.join(cluster_0_abbrs)
        cluster_1_string = ', '.join(cluster_1_abbrs)

        # create position
        position_created = position_creator(data=rows_1h, t=-1, commission=0.0003, position_type=position_type,
                                            min_size_stop_loss=0.0004)

        # Add Tehran time
        tehran_tz = pytz.timezone('Asia/Tehran')

        if (len(position_created) > 0) and (avg_cluster > 0.5):
            response = {
                "Kind": position_type,
                "Score": avg_cluster,
                "Positives": cluster_1_string,
                "Negatives": cluster_0_string,
                "Time UTC": rows_1h.iloc[-1]["timestamp"].strftime('%b-%d %H:%M'),
                "Time Teh": rows_1h.iloc[-1]["timestamp"].replace(tzinfo=pytz.utc).astimezone(tehran_tz).strftime(
                    '%b-%d %H:%M'),
                "sl": position_created.iloc[-1]["sl"],
                "tp": position_created.iloc[-1]["tp"],
                "Entry": rows_1h.iloc[-1]["close"],
                "Volume":
                    calculate_position_size(entry_price=rows_1h.iloc[-1]["close"],
                                            stop_loss=position_created.iloc[-1]["sl"],
                                            account_balance=10000, risk_percentage=1, leverage=100)[
                        "standard_lots"],
            }
            await run_notify_active_users(message=format_position_dict_for_telegram_message(response))

        message = f"""
        This is for information:
        Kind: {position_type}
        Score: {avg_cluster}
        Entry: {rows_1h.iloc[-1]["close"]}
        Positives: {cluster_1_string}
        Negatives: {cluster_0_string}
        UTC:    {rows_1h.iloc[-1]["timestamp"].strftime('%b-%d %H:%M')}
        Teh:    {rows_1h.iloc[-1]["timestamp"].replace(tzinfo=pytz.utc).astimezone(tehran_tz).strftime('%b-%d %H:%M')}
        """
        await run_notify_active_users(message=message)

    return 0


# Function to send a request to the target URL
async def yahoo_updater():
    loggerUpdater.info("UPDATER HAS BEEN STARTED")

    last_row = get_last_row(EURUSD_M15, EURUSD_M15_Pydantic)
    if not last_row:
        loggerUpdater.error("No data found in the EURUSD_M15 table.")

    date_last_row = last_row[0].timestamp.date()

    tiingo_data = await fetch_tiingo_finance_data(symbol="EURUSD=X", start=date_last_row,
                                                  end=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                                                  interval="15min")
    loggerUpdater.debug(tiingo_data)
    loggerUpdater.debug("tiingo_data")

    new_data = await fetch_yahoo_finance_data(symbol="EURUSD=X", start=date_last_row,
                                              end=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                                              interval="15m")
    if new_data is None:
        loggerUpdater.error("No data received from yahoo finance")
        await run_notify_active_users(message="No data received from yahoo finance")
        return 0

    await add_yahoo_data_to_db(new_data)
    loggerUpdater.debug("data in table EuroUSD has been updated.")

    loggerUpdater.debug("start of fetch_tiingo_finance_data")
