import os
import motor
from dotenv import load_dotenv
from fastapi import FastAPI
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


def start_save_apt_rent(parsing_data: list):
    aptRents_collection.insert_many(parsing_data)


def start_save_apt_trade(parsing_data: list):
     aptTrades_collection.insert_many(parsing_data)


def start_save_city_park(parsing_data: list):
     cityParks_collection.insert_many(parsing_data)


def start_save_officetel_rent(parsing_data: list):
     officetelRents_collection.insert_many(parsing_data)


def start_save_officetel_trade(parsing_data: list):
     officetelTrades_collection.insert_many(parsing_data)


def start_save_school(parsing_data: list):
     schools_collection.insert_many(parsing_data)
