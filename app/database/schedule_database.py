import os

import motor
from dotenv import load_dotenv
from fastapi import FastAPI
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()
load_dotenv()

client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGODB_URL'))
aptRents_collection = client.mongo_db.aptRents
aptTrades_collection = client.mongo_db.aptTrades
cityParks_collection = client.mongo_db.cityParks
officetelRents_collection = client.mongo_db.officetelRents
officetelTrades_collection = client.mongo_db.officetelTrades
schools_collection = client.mongo_db.schools


async def schedule_save_apt_rent(parsing_data: list):
    for i in list:
        existing_data = await aptRents_collection.find_one(i)
        if not existing_data:
            await aptRents_collection.insert_one(parsing_data)


async def schedule_save_apt_trade(parsing_data: list):
    for i in list:
        existing_data = await aptTrades_collection.find_one(i)
        if not existing_data:
            await aptTrades_collection.insert_one(parsing_data)


async def schedule_save_city_park(parsing_data: list):
    for i in list:
        existing_data = await cityParks_collection.find_one(i)
        if not existing_data:
            await cityParks_collection.insert_one(parsing_data)


async def schedule_save_officetel_rent(parsing_data: list):
    for i in list:
        existing_data = await officetelRents_collection.find_one(i)
        if not existing_data:
            await officetelRents_collection.insert_one(parsing_data)


async def schedule_save_officetel_trade(parsing_data: list):
    for i in list:
        existing_data = await officetelTrades_collection.find_one(i)
        if not existing_data:
            await officetelTrades_collection.insert_one(parsing_data)


async def schedule_save_school(parsing_data: list):
    for i in list:
        existing_data = await schools_collection.find_one(i)
        if not existing_data:
            await schools_collection.insert_one(parsing_data)


if __name__ == '__main__':
    # asyncio.get_event_loop().run_until_complete(test2()) #비동기실행
    #
    # asyncio.run(test2()) #동기실행

    print('test')
