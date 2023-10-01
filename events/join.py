import json
import sys
import os
from definitions.path import root_dir

# - Check for config.json, if it doesn't find it, will exit and give an error message.
if os.path.exists("{}/config.json".format(root_dir)) == False:
    sys.exit("Unable to find 'config.json'! Please add it and try again.")
else:
    with open("{}/config.json".format(root_dir)) as file:
        config = json.load(file)

def join_server(bot):
    '''
    Sends a DM when a user joins the server.
    Also sends a message in #immigration-office.
    '''
    @bot.event
    async def on_member_join(member):
        guild = member.guild
        await member.send(f"Welcome to {guild}, {member}! \n Please make sure to read the message in #welcome-citizen.") 
        print(f"{member} has joined {guild}.") # - shows who joined in bot terminal.
        channel = bot.get_channel(config["log_private"])
        await channel.send(f"{member} has entered {guild}.")