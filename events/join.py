# - import required modules for relative path and config.
import os
import json
from path.definitions import root_dir

config_path = os.path.join(root_dir, 'config.json')

with open(config_path) as file:
    config = json.load(file)

def join_server(bot):
    '''
    Sends a DM when a user joins the server. Also sends a message in #immigration-office.
    '''
    @bot.event
    async def on_member_join(member):
        guild = bot.get_guild(config["guild_id"])
        await member.send("Welcome to {} {}! \n Please read #welcome-citizen as you may need a certain role.".format(guild, member)) 
        print("{} has joined The Dome.".format(member))
        channel = bot.get_channel(839597320378253372) #Sends welcome message in #immigration-office.
        await channel.send("Welcome {}!".format(member)) #Shows who joined in terminal.