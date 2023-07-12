# - import required modules for relative path and config.
import os
import json
from path.definitions import root_dir

config_path = os.path.join(root_dir, 'config.json')

with open(config_path) as file:
    config = json.load(file)

def leave_server(bot):
    @bot.event
    async def on_member_remove(member):
        guild = bot.get_guild(config["guild_id"])
        channel = bot.get_channel(839557877567455233)
        await channel.send("{} has left the server.".format(member)) #Sends leave message in #admin-only.
        print("{} has left {}.".format(member, guild)) #Shows who left in terminal.