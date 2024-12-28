# src/settings.py

import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Now you can access your environment variables using os.getenv()
OANDA_ACCESS_TOKEN = os.getenv('OANDA_ACCESS_TOKEN')
ALPHAVANTAGE_API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')
