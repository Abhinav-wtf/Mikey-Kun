import os
import re
from platform import python_version as kontol
from telethon import events, Button
from telegram import __version__ as telever
from telethon import __version__ as tlhver
from pyrogram import __version__ as pyrover
from SiestaRobot.events import register
from SiestaRobot import telethn as tbot


PHOTO = "https://telegra.ph/file/92487bd1cc9fdba41c32e.jpg"

@register(pattern=("/alive"))
async def awake(event):
  TEXT = f"**Hi [{event.sender.first_name}](tg://user?id={event.sender.id}), I'm Siesta Robot.** \n\n"
  TEXT += "🔹 **I'm Working Properly** \n\n"
  TEXT += f"🔹 **My Master : [Mikey-kun](https://t.me/mikey_kun90)** \n\n"
  TEXT += f"🔹 **Library Version :** `{telever}` \n\n"
  TEXT += f"🔹 **Telethon Version :** `{tlhver}` \n\n"
  TEXT += f"🔹 **Pyrogram Version :** `{pyrover}` \n\n"
  TEXT += "**Thanks For Adding Me Here ❤️**"
  BUTTON = [[Button.url("Help", "https://t.me/mikeyxrobot?start=help"), Button.url("Support", "https://t.me/MikeyXSupport")]]
  await tbot.send_file(event.chat_id, PHOTO, caption=TEXT,  buttons=BUTTON)
