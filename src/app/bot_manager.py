from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from src.app.config import settings
from src.app.router import start, handle_message, button_handler


class BotManager:
    def __init__(self):
        self.application = None

    async def initialize(self):
        if not self.application:
            self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
            self.application.add_handler(CommandHandler("start", start))
            self.application.add_handler(CallbackQueryHandler(button_handler))
            # self.application.add_handler(MessageHandler(filters.Text & ~filters.COMMAND, handle_message))
            # self.application.add_handler(MessageHandler(filters.TEXT, handle_message))  # Handle all text messages
            # self.application.add_handler(MessageHandler(~filters.COMMAND, handle_message))  # Handle non-command messages

            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            await self.application.initialize()

    async def start_webhook(self):
        webhook_url = f"https://{settings.DOMAIN}/webhook"
        await self.application.bot.set_webhook(url=webhook_url)

    async def shutdown(self):
        if self.application:
            await self.application.shutdown()

bot_manager = BotManager()
