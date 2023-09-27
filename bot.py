# - prevents the generation of __pycache__ files
import sys
sys.dont_write_bytecode = True

# - import sqlite3
import sqlite3

# - import os for relative path.
import os
absolute_path = os.path.dirname(__file__)

# - enable logging
import logging
handler = logging.FileHandler(filename=f'{absolute_path}/domo.log', encoding='utf-8', mode='w')

# - import json for config.json
import json
import sys

# - import required dependencies
import discord
from discord.ext import commands, tasks

# - import events and commands
from cmds import *
from events  import *
from events.experience import *

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix = '$', intents = intents)

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
voice_exp.member_voice_exp(bot)
join.join_server(bot)
leave.leave_server(bot)
voice_log.voice_log(bot)
level_roles.level_up_role(bot, discord)
text_exp.member_text_exp(bot, discord)
react_role.role_on_react(bot, discord)

bot.run(config["token"], log_handler=handler, log_level=logging.DEBUG)