# create_tables.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app.models import Base  # Adjust based on your project structure

DATABASE_URL = "sqlite:///./db"  # Match this with your actual database URL

engine = create_engine(DATABASE_URL)

try:
    Base.metadata.create_all(bind=engine)  # This should create all tables defined by your models.
except Exception as e:
    print(f"Error creating tables: {e}")
