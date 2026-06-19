import os
from bale import Bot

BOT_TOKEN = "1214289316:IOxAQjveWKEG-vGTi-uWBJSZf_6utZtRPxQ"
ADMIN_ID = 692466131

TOKEN = os.getenv("BOT_TOKEN", BOT_TOKEN)
ADMIN = int(os.getenv("ADMIN_ID", ADMIN_ID))

bot = Bot(token=TOKEN)
