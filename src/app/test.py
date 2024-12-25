import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# DATABASE_URL = "sqlite:///./db"
DATABASE_URL = "sqlite+aiosqlite:///./db"

# Create an async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session factory
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)


async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session  # This is how we yield the session for use


async def test_get_async_session():
    async for db in get_async_session():
        print("Session created:", db)


if __name__ == "__main__":
    asyncio.run(test_get_async_session())
