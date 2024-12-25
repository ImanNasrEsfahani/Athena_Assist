from src.log_config import loggerUpdater
from src.updater.scheduler import yahoo_updater
from src.updater.crud import add_dataframe_to_db
from src.updater.scheduler import prediction_hourly
from fastapi import APIRouter

router = APIRouter()

import pandas as pd


@router.get("/updater/yahoo-finance", response_model=None)
async def yahoo_finance():
    await yahoo_updater()
    return None


@router.get("/updater/csv-to-sqlite", response_model=None)
def csv_to_sqlite():
    # Open the CSV file and read its contents
    new_data = pd.read_csv(rf'./models/EURUSD_M15.csv', header=0)

    new_data["timestamp"] = new_data["datetime"]
    new_data.drop("datetime", axis=1, inplace=True)
    new_data.reset_index(drop=True, inplace=True)

    add_dataframe_to_db(new_data)
    loggerUpdater.debug("data in table EuroUSD has been updated.")

    return None


@router.get("/predict", responses=None)
async def predict():
    await prediction_hourly()

    return None
