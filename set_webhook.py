import os, subprocess
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = "https://" + os.getenv('DOMAIN') + "/webhook/"
command = f"curl -X POST 'https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}'"

# Run the curl command
subprocess.run(command, shell=True)
