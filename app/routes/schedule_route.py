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
    scheduler.add_job(schedule_apt_rent, 'cron', hour=1, minute=0)
    scheduler.add_job(schedule_apt_trade, 'cron', hour=1, minute=5)  # 매일 새벽 1시 5분에 실행
    scheduler.add_job(schedule_officetel_rent, 'cron', hour=1, minute=10)
    scheduler.add_job(schedule_officetel_trade, 'cron', hour=1, minute=15)
    scheduler.start()
    print("스케줄러 시작")


def shutdown_scheduler():
    scheduler.shutdown()
    print("스케줄러 종료")
