from fastapi import FastAPI

from app.services.startup_service.apt_rent import startup_apt_rent
from app.services.startup_service.apt_trade import startup_apt_trade
from app.services.startup_service.city_park import startup_city_park
from app.services.startup_service.officetel_rent import startup_officetel_rent
from app.services.startup_service.officetel_trade import startup_officetel_trade
from app.services.startup_service.school import startup_school

app = FastAPI()


def save_mongodb():
    startup_apt_rent()
    startup_apt_trade()
    startup_officetel_rent()
    startup_officetel_trade()
    startup_city_park()
    startup_school()
