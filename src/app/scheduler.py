from src.log_config import loggerApp
from src.app.notifications import run_notify_active_users

from apscheduler.schedulers.asyncio import AsyncIOScheduler


# Create an instance of AsyncIOScheduler
scheduler = AsyncIOScheduler()

def start_scheduler():
    loggerApp.info("Start Scheduler app")

    # Schedule job to notify active users every minute (customize as needed)
    # scheduler.add_job(func=run_notify_active_users,
    #                   trigger='cron',
    #                   minute='0',
    #                   # day_of_week = 'mon-fri',
    #                   timezone = 'Europe/London')

    # start scheduler
    scheduler.start()
