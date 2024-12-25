from src.log_config import loggerUpdater
from src.updater.schemas import EURUSD_M15Create
from src.updater.database import get_db
from src.updater.models import EURUSD_M15
from src.updater.models import EURUSD_M15_Pydantic
from src.app.notifications import run_notify_active_users

import pandas as pd
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from sqlmodel import select
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone, timedelta

def create_EURUSD_M15(db: Session, users: list[EURUSD_M15Create]):
    created_EURUSD_M15 = []

    for row in created_EURUSD_M15:
        db_EURUSD_M15 = EURUSD_M15(**row.dict())
        db.add(db_EURUSD_M15)

    db.commit()

    # Refresh the records to get their IDs back from the database.
    for row in created_EURUSD_M15:
        created_EURUSD_M15.append(db.query(EURUSD_M15).filter(EURUSD_M15.timestamp == row.timestamp).first())

    return created_EURUSD_M15


# Function to add DataFrame to the database
def add_dataframe_to_db(df: pd.DataFrame):
    loggerUpdater.debug(df)

    db_session = next(get_db())

    for index, row in df.iterrows():
        exists = db_session.query(EURUSD_M15).filter_by(timestamp=row["timestamp"]).first()

        if exists:
            # Skip adding or updating if the record already exists
            continue

        # Attempt to add or update the record
        record = EURUSD_M15(
            # timestamp=row["timestamp"],
            timestamp = datetime.fromisoformat(row['timestamp'].replace("Z", "+00:00")),
            open=round(row["open"],5),
            high=round(row["high"],5),
            low=round(row["low"],5),
            close=round(row["close"],5),
            volume=round(row["volume"],5)
        )

        # Add new record
        db_session.add(record)

    try:
        db_session.commit()
        loggerUpdater.info("New data from csv has been saved in sqlite database")

    except IntegrityError:
        loggerUpdater.error("Insert data from csv to sqlite has error.")
        db_session.rollback()  # Rollback in case of any integrity error

# Function to add DataFrame to the database
async def add_yahoo_data_to_db(df: pd.DataFrame):
    loggerUpdater.debug(df)

    db_session = next(get_db())

    for index, row in df.iterrows():
        exists = db_session.query(EURUSD_M15).filter_by(timestamp=row.iloc[0]).first()

        if exists:
            # Skip adding or updating if the record already exists
            continue

        # Attempt to add or update the record
        record = EURUSD_M15(
            timestamp = row.iloc[0],
            open=round(row.iloc[1],6),
            high=round(row.iloc[2],6),
            low=round(row.iloc[3],6),
            close=round(row.iloc[4],6),
            volume=round(row.iloc[5],6)
        )

        # Add new record
        db_session.add(record)

    try:
        db_session.commit()
        loggerUpdater.info("Yahoo New data has been saved in sqlite database")

    except IntegrityError:
        loggerUpdater.error("Yahoo new data to sqlite has error.")
        db_session.rollback()  # Rollback in case of any integrity error
        await run_notify_active_users(
            message="Yahoo new data to sqlite has error.")


def get_last_row(model, pydantic):
    db_session = next(get_db())

    statement = select(model).order_by(model.timestamp.desc()).limit(1)
    results = db_session.execute(statement)
    return [pydantic.from_orm(row) for row in results.scalars().all()]


def get_last_month(model, pydantic, to_datetime: datetime = datetime.now()):
    db_session = next(get_db())

    # Calculate the date last month
    months_ago = to_datetime - timedelta(days=31)

    # Create the select statement
    statement = (
        select(model)
            .where(model.timestamp >= months_ago)
            .order_by(model.timestamp)
    )
    df = pd.read_sql_query(statement, db_session.bind)
    return df