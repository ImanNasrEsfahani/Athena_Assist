# from fastapi import APIRouter, Request, Depends
# from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext
# from src.app.bot_manager import bot_manager
# from telegram import Update
# from src.log_config import loggerApp
#
# router = APIRouter()
#
# def get_application():
#     return bot_manager.application
#
# @router.post("/webhook")
# async def process_update(request: Request, application: Application = Depends(get_application)):
#     print("message has been recieved ", request)
#     loggerApp.info("Received request: %s", await request.json())
#     try:
#         update = Update.de_json(await request.json(), application.bot)
#         loggerApp.info("Processed update successfully")
#         await application.process_update(update)
#     except Exception as e:
#         loggerApp.error("Error processing update: %s", str(e))
#     return {"status": "ok"}