# - prevents the generation of __pycache__ files
import sys
sys.dont_write_bytecode = True

# - import json for config.json
import json
import sys

# - import required dependencies
import discord
from discord.ext import commands

# - import events and commands
from cmds import *
from events  import *

# - import os for relative path.
import os
absolute_path = os.path.dirname(__file__)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# - change YOUR_PREFIX_HERE to the prefix that you want.
bot = commands.Bot(command_prefix = 'YOUR_PREFIX_HERE', intents = intents)

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

# - load commands and events from cmds and events folders.
join.join_server(bot)
leave.leave_server(bot)
kick.kick(bot, discord, commands)
ban.ban(bot, discord, commands)
react_role.role_on_react(bot, discord)

bot.run(config["token"])