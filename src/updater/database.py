from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Annotated
from fastapi import FastAPI, Depends
from src.updater.models import Base

# Define the SQLite database URL
DATABASE_URL = "sqlite:///./models/market.db"  # This will create a file named users.db in the current directory

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create a session local class
SessionLocal = sessionmaker(bind=engine)

# Dependency to get the database session
def get_db() -> Session:
    db = SessionLocal()  # Create a new session
    try:
        yield db  # Yield the session to be used in the route
    finally:
        db.close()  # Close the session after use


SessionDep = Annotated[Session, Depends(get_db)]

# Function to create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)