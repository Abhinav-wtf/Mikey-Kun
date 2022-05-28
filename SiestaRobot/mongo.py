import asyncio
import sys
from motor import motor_asyncio
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from SiestaRobot.confing import get_int_key, get_str_key
from SiestaRobot import LOGGER

client = MongoClient("mongodb+srv://mike:mike123@cluster0.gl7x8.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient("mongodb+srv://mike:mike123@cluster0.gl7x8.mongodb.net/?retryWrites=true&w=majority", 27017)["SiestaRobot"]
motor = motor_asyncio.AsyncIOMotorClient("mongodb+srv://mike:mike123@cluster0.gl7x8.mongodb.net/?retryWrites=true&w=majority", 27017)
db = motor["SiestaRobot"]
db = client["SiestaRobot"]
try:
    asyncio.get_event_loop().run_until_complete(motor.server_info())
except ServerSelectionTimeoutError:
    sys.exit(LOGGER.critical("ERROR"))
