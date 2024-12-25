from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from src.app import crud, models, schemas
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# DATABASE_URL = "sqlite:///./db"
DATABASE_URL = "sqlite+aiosqlite:///./db"

# Create an async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session factory
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)

# Dependency to get the async session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# # Define the SQLite database URL
# DATABASE_URL = "sqlite:///./db"  # This will create a file named users.db in the current directory
#
# # Create the SQLAlchemy engine
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
#
# # Create a session local class
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
Base = declarative_base()

# Base.metadata.create_all(bind=engine)
# Function to initialize the database and create tables
# async def init_db():
#     async with engine.begin() as conn:
#         # This will create all tables defined in Base's metadata
#         await conn.run_sync(Base.metadata.create_all)

# # Dependency to get the database session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
