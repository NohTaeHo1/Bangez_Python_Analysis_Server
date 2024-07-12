import asyncio

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.services.scheduler_service.apt_rent import schedule_apt_rent
from app.services.scheduler_service.apt_trade import schedule_apt_trade
from app.services.scheduler_service.officetel_rent import schedule_officetel_rent
from app.services.scheduler_service.officetel_trade import schedule_officetel_trade

# scheduler = BackgroundScheduler()
scheduler = AsyncIOScheduler(timezone=pytz.utc)
app = FastAPI()


def start_scheduler():
    scheduler.add_job(schedule_apt_rent, 'cron', hour=2, minute=46)
    scheduler.add_job(schedule_apt_trade, 'cron', hour=2, minute=47)
    scheduler.add_job(schedule_officetel_rent, 'cron', hour=10, minute=48)
    scheduler.add_job(schedule_officetel_trade, 'cron', hour=10, minute=49)
    scheduler.start()
    print("스케줄러 시작")

def shutdown_scheduler():
    scheduler.shutdown()
    print("스케줄러 종료")
