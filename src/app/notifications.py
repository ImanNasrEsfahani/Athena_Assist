# from src.app.database import get_db, SessionLocal
from src.app.models import User

import os, httpx
from src.log_config import loggerApp
from src.app.config import settings
from random import random

from .database import get_async_session
from .service import get_all_active_users
from sqlalchemy import select


async def run_notify_active_users(message: str = f"This is test notification! {round(random() * 100)}"):
    """Wrapper function to call notify_active_users with proper async context."""
    users = await get_all_active_users()
    for user in users:
        await send_telegram_message(user.telegram_chat_id, message)


async def send_telegram_message(chat_id: str, message: str):
    """Send a message to a Telegram user."""
    tg_msg = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        async with httpx.AsyncClient() as client:
            await client.post(API_URL, json=tg_msg)
    except Exception as e:
        loggerApp.error(f"Failed to send message to {chat_id}: {e}")
