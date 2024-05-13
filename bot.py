# - import asyncio
import asyncio

# - prevents the generation of __pycache__ files
import sys
sys.dont_write_bytecode = True

import sqlite3

# - import os for relative path.
import os
absolute_path = os.path.dirname(__file__)
root_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

# - enable logging
import logging
import logging.handlers

logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
logging.getLogger('discord.http').setLevel(logging.INFO)
logging.getLogger('discord.gateway').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename = f"{absolute_path}/domo.log",
    encoding = "utf-8",
    maxBytes = 32 * 1024 * 1024, # - 32 MiB
    backupCount = 5, # - Rotates through 5 files.
)     
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}',
                              dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

# - import json for config.json
import json 
import sys

# - import required dependencies
import discord
from discord.ext import commands

# - import events.
from events import *

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix = '$', intents = intents)

#------Load cogs------
try:
    async def load_extensions():
        for cog in os.listdir(f"{absolute_path}/cogs"):
            if cog.endswith(".py"):
                # - removes the .py from filename.
                await bot.load_extension(f"cogs.{cog[:-3]}")
except FileNotFoundError:
    print("There is no such directory or file! Check and try again.")

async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    await ctx.send("Loaded extension!")

# - Check for config.json, if it doesn't find it,
# - will exit and give an error message.
if os.path.exists("{}/config.json".format(absolute_path)) == False:
    sys.exit("Unable to find 'config.json'! Please add it and try again.")
else:
    with open("{}/config.json".format(absolute_path)) as file:
        config = json.load(file)

server_join.server_join(bot)
server_leave.server_leave(bot)

@bot.event 
async def on_ready():
    print("{0.user} is ready.".format(bot))
    print("----------------------")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(config["token"])

asyncio.run(main())