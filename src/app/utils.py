# # utils.py - non-business logic functions, e.g. response normalization, data enrichment, etc.
#
# # src/app/utils.py
# import telegram_webhook
# from twilio.rest import Client
# import smtplib
# from email.mime.text import MIMEText
# from src.app.config import settings
#
#
# def send_telegram_message(message: str, chat_id: int):
#     bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
#     bot.send_message(chat_id=chat_id, text=message)
#
# def send_sms(to: str, message: str):
#     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#     client.messages.create(body=message, from_=settings.TWILIO_PHONE_NUMBER, to=to)
#
# def send_email(to: str, subject: str, body: str):
#     msg = MIMEText(body)
#     msg['Subject'] = subject
#     msg['From'] = settings.EMAIL_ADDRESS
#     msg['To'] = to
#
#     with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
#         server.starttls()
#         server.login(settings.EMAIL_ADDRESS, settings.EMAIL_PASSWORD)
#         server.sendmail(settings.EMAIL_ADDRESS, to, msg.as_string())