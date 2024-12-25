import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "YOUR_TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "YOUR_TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "YOUR_TWILIO_PHONE_NUMBER")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.example.com")  # Replace with your SMTP server
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))  # Common port for TLS
    EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS", "your_email@example.com")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "your_email_password")


    # Updater
    TIINGO_API_TOKEN = os.getenv("TIINGO_API_TOKEN", "Tiingo API Token")

settings = Settings()
