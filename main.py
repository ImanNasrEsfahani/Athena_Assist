import asyncio, uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from telegram import Update
from telegram.ext import Application
from contextlib import asynccontextmanager
from src.log_config import setup_logging, loggerMain

from src.app import (
    bot_manager,
    engine,
    app_router,
    app_start_scheduler,
)
from src.updater.database import create_tables

from src.updater.scheduler import start_scheduler as updater_start_scheduler
from src.updater.router import router as updater_router
# Setup logging
setup_logging()

# from src.updater.models.base import Base as BaseUpdater

@asynccontextmanager
async def lifespan(app: FastAPI):
    loggerMain.info("test for iman")
    loggerMain.warn("test for iman")
    loggerMain.debug("test for iman")

    try:
        await bot_manager.initialize()
        await bot_manager.start_webhook()
    except Exception as e:
        # Handle the exception
        print(f"An error occurred: {e}")

    # Start the scheduler
    # db = next(get_db())  # Get the database session for scheduling
    updater_start_scheduler()
    app_start_scheduler()

    create_tables()
    # Base.metadata.create_all(bind=engine)

    yield
    loggerMain.info("Shutdown event triggered")
    await bot_manager.shutdown()

# Create an instnce of FastAPI
app = FastAPI(title="ِAthena Application", version="1.0", lifespan=lifespan)
# Configure CORS
# Define allowed origins
origins = [
    "http://localhost:8000",  # Adjust this to your frontend's URL
    "https://fastapi.imannasr.com",  # Add your production URL if needed
    "*",  # Use "*" to allow all origins (not recommended for production)
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Include the router from all modules
app.include_router(app_router)
app.include_router(updater_router)


@app.get("/account_info")
async def get_account_info():
    if not mt5.initialize():
        return {"error": "MT5 initialization failed"}

    account_info = mt5.account_info()
    if account_info is None:
        return {"error": "Failed to get account info"}

    return {
        "login": account_info.login,
        "balance": account_info.balance,
        "equity": account_info.equity,
        "margin": account_info.margin,
        "free_margin": account_info.margin_free,
    }

# app.include_router(telegram_webhook.router)

def get_application():
    return bot_manager.application


@app.post("/webhook/")
async def process_update(request: Request, application: Application = Depends(get_application)):
    loggerMain.info("Received request: %s", await request.json())
    try:
        update = Update.de_json(await request.json(), application.bot)
        await application.process_update(update)
    except Exception as e:
        loggerMain.error("Error processing update: %s", str(e))
    return {"status": "ok"}


async def main():
    global application
    config = uvicorn.Config(app, host='0.0.0.0', port=8000)
    server = uvicorn.Server(config)

    # Run application and webserver together
    async with application:
        await application.start()
        await server.serve()
        await application.stop()


if __name__ == "__main__":
    asyncio.run(main())
