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


from src.updater.utils import run_notify_active_users


@router.get("/send-test", responses=None)
async def send_test():
    await run_notify_active_users(message="No data received from yahoo finance")
    return None


import httpx
from mt5linux import MetaTrader5
import socket

@router.get("/call-external-service")
async def call_external_service():
    # async with httpx.AsyncClient() as client:
    #     response = await client.get("http://host.docker.internal:18812")
    #     return {"status_code": response.status_code, "data": response.json()}
    # try:
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     sock.connect(("host.docker.internal", 18800))  # Use appropriate host address
    #     response = sock.recv(1024).decode()
    #     sock.close()
    #     return {"message": response}
    # except Exception as e:
    #     return {"error": str(e)}

    # mt5 = MetaTrader5(host="127.0.0.1", port=18812)
    mt5 = MetaTrader5(host="host.docker.internal", port=18812)
    if not mt5.initialize():
        print("MT5 initialization failed")
        mt5.shutdown()

    account_info = mt5.account_info()
    # mt5.account_info().balance
    return {
        "balance": account_info.balance,
        "equity": account_info.equity,
        "profit": account_info.profit
    }

    return True
