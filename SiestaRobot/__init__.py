import asyncio
import logging
import os
import sys
import json
import asyncio
import time
import spamwatch
import telegram.ext as tg
from redis import StrictRedis
from inspect import getfullargspec
from aiohttp import ClientSession
from Python_ARQ import ARQ
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.sessions import MemorySession
from pyrogram.types import Message
from pyrogram import Client, errors
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid, ChannelInvalid
from pyrogram.types import Chat, User
from ptbcontrib.postgres_persistence import PostgresPersistence

StartTime = time.time()

def get_user_list(__init__, key):
    with open("{}/SiestaRobot/{}".format(os.getcwd(), __init__), "r") as json_file:
        return json.load(json_file)[key]

# enable logging
FORMAT = "[SiestaRobot] %(message)s"
logging.basicConfig(
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
)
logging.getLogger("pyrogram").setLevel(logging.INFO)
logging.getLogger('ptbcontrib.postgres_persistence.postgrespersistence').setLevel(logging.WARNING)

LOGGER = logging.getLogger('[SiestaRobot]')
LOGGER.info("Mikey is starting. | A Project by Toamn. | Licensed under GPLv3.")
LOGGER.info("Not affiliated to other anime or Villain in any way whatsoever.")
LOGGER.info("Project maintained by: github.com/Yash-Sharma-1807 (t.me/mikey_kun90)")

# if version < 3.9, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 9:
    LOGGER.error(
        "You MUST have a python version of at least 3.9! Multiple features depend on this. Bot quitting."
    )
    sys.exit(1)

ENV = bool(os.environ.get("ENV", False))

from SiestaRobot.config import Development as Config

TOKEN = Config.TOKEN

try:
    OWNER_ID = int(Config.OWNER_ID)
except ValueError:
    raise Exception("Your OWNER_ID variable is not a valid integer.")

JOIN_LOGGER = Config.JOIN_LOGGER
OWNER_USERNAME = Config.OWNER_USERNAME
ALLOW_CHATS = Config.ALLOW_CHATS
try:
    DRAGONS = {int(x) for x in Config.DRAGONS or []}
    DEV_USERS = {int(x) for x in Config.DEV_USERS or []}
except ValueError:
    raise Exception("Your sudo or dev users list does not contain valid integers.")

try:
    DEMONS = {int(x) for x in Config.DEMONS or []}
except ValueError:
    raise Exception("Your support users list does not contain valid integers.")

try:
    WOLVES = {int(x) for x in Config.WOLVES or []}
except ValueError:
    raise Exception("Your whitelisted users list does not contain valid integers.")

try:
    TIGERS = {int(x) for x in Config.TIGERS or []}
except ValueError:
    raise Exception("Your tiger users list does not contain valid integers.")

EVENT_LOGS = Config.EVENT_LOGS
WEBHOOK = Config.WEBHOOK
URL = Config.URL
PORT = Config.PORT
CERT_PATH = Config.CERT_PATH
API_ID = Config.API_ID
API_HASH = Config.API_HASH
ERROR_LOGS = Config.ERROR_LOGS
DB_URL = Config.SQLALCHEMY_DATABASE_URI
MONGO_DB_URI = Config.MONGO_DB_URI
ARQ_API = Config.ARQ_API_KEY
ARQ_API_URL = Config.ARQ_API_URL
DONATION_LINK = Config.DONATION_LINK
LOAD = Config.LOAD
TEMP_DOWNLOAD_DIRECTORY = Config.TEMP_DOWNLOAD_DIRECTORY
OPENWEATHERMAP_ID = Config.OPENWEATHERMAP_ID
NO_LOAD = Config.NO_LOAD
HEROKU_API_KEY = Config.HEROKU_API_KEY
HEROKU_APP_NAME = Config.HEROKU_APP_NAME
DEL_CMDS = Config.DEL_CMDS
STRICT_GBAN = Config.STRICT_GBAN
WORKERS = Config.WORKERS
REM_BG_API_KEY = Config.REM_BG_API_KEY
BAN_STICKER = Config.BAN_STICKER
ALLOW_EXCL = Config.ALLOW_EXCL
CASH_API_KEY = Config.CASH_API_KEY
TIME_API_KEY = Config.TIME_API_KEY
WALL_API = Config.WALL_API
SUPPORT_CHAT = Config.SUPPORT_CHAT
SPAMWATCH_SUPPORT_CHAT = Config.SPAMWATCH_SUPPORT_CHAT
SPAMWATCH_API = Config.SPAMWATCH_API
INFOPIC = Config.INFOPIC
BOT_USERNAME = Config.BOT_USERNAME
    
    
try:
    BL_CHATS = {int(x) for x in Config.BL_CHATS or []}
except ValueError:
    raise Exception("Your blacklisted chats list does not contain valid integers.")

DRAGONS.add(OWNER_ID)
DEV_USERS.add(OWNER_ID)

REDIS = StrictRedis.from_url(REDIS_URL,decode_responses=True)

try:

    REDIS.ping()

    LOGGER.info("Your redis server is now alive!")

except BaseException:

    raise Exception("Your redis server is not alive, please check again.")

finally:

   REDIS.ping()

   LOGGER.info("Your redis server is now alive!")
    
    
if not SPAMWATCH_API:
    sw = None
    LOGGER.warning("SpamWatch API key missing! recheck your config")
else:
    try:
        sw = spamwatch.Client(SPAMWATCH_API)
    except:
        sw = None
        LOGGER.warning("Can't connect to SpamWatch!")

from SiestaRobot.modules.sql import SESSION

defaults = tg.Defaults(run_async=True)
updater = tg.Updater(TOKEN, workers=WORKERS, use_context=True)
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)
dispatcher = updater.dispatcher
print("[INFO]: INITIALIZING AIOHTTP SESSION")
aiohttpsession = ClientSession()
# ARQ Client
print("[INFO]: INITIALIZING ARQ CLIENT")
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)

pbot = Client(
    ":memory:",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    workers=min(32, os.cpu_count() + 4),
)
apps = []
apps.append(pbot)
loop = asyncio.get_event_loop()

async def get_entity(client, entity):
    entity_client = client
    if not isinstance(entity, Chat):
        try:
            entity = int(entity)
        except ValueError:
            pass
        except TypeError:
            entity = entity.id
        try:
            entity = await client.get_chat(entity)
        except (PeerIdInvalid, ChannelInvalid):
            for kp in apps:
                if kp != client:
                    try:
                        entity = await kp.get_chat(entity)
                    except (PeerIdInvalid, ChannelInvalid):
                        pass
                    else:
                        entity_client = kp
                        break
            else:
                entity = await kp.get_chat(entity)
                entity_client = kp
    return entity, entity_client


async def eor(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})


DRAGONS = list(DRAGONS) + list(DEV_USERS)
DEV_USERS = list(DEV_USERS)
WOLVES = list(WOLVES)
DEMONS = list(DEMONS)
TIGERS = list(TIGERS)

# Load at end to ensure all prev variables have been set
from SiestaRobot.modules.helper_funcs.handlers import (
    CustomCommandHandler,
    CustomMessageHandler,
    CustomRegexHandler,
)

# make sure the regex handler can take extra kwargs
tg.RegexHandler = CustomRegexHandler
tg.CommandHandler = CustomCommandHandler
tg.MessageHandler = CustomMessageHandler
