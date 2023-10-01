# - import asyncio
import asyncio

# - prevents the generation of __pycache__ files
import sys
sys.dont_write_bytecode = True

# - import os for relative path.
import os
from definitions.path import root_dir
absolute_path = os.path.dirname(__file__)


# - enable logging
import logging
handler = logging.FileHandler(filename=f'{absolute_path}/domo.log', encoding='utf-8', mode='w')

# - import json for config.json
import json

# - import required dependencies
import discord
from discord.ext import commands, tasks

# - import events and commands
from cmds import *
from events  import *

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix = '$', intents = intents)

#------Load cogs------
try:
    async def load_extensions():
        for cog in os.listdir(f"{root_dir}/cogs"):
            if cog.endswith(".py"):
                # - removes the .py from filename.
                await bot.load_extension(f"cogs.{cog[:-3]}")
except FileNotFoundError:
    print("There is no such directory or file! Check and try again.")

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    await ctx.send("Loaded extension!")

# - Check for config.json, if it doesn't find it, will exit and give an error message.
if os.path.exists("{}/config.json".format(absolute_path)) == False:
    sys.exit("Unable to find 'config.json'! Please add it and try again.")
else:
    with open("{}/config.json".format(absolute_path)) as file:
        config = json.load(file)

@bot.event 
async def on_ready():
    print("{0.user} is ready.".format(bot)) # - prints that Domo is ready when this file is run.
    print("----------------------")

# --------- Commands ---------
kick.kick(bot, discord, commands)
ban.ban(bot, discord, commands)
# --------- Events ---------
join.join_server(bot)
leave.leave_server(bot)
voice_log.voice_log(bot)
react_role.role_on_react(bot, discord)

async def main():
    async with bot:
        await load_extensions() # - loads cogs on startup.
        await bot.start(config["token"]) # - set up logging in future.

asyncio.run(main())