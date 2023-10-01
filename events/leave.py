import json
import os
import sys
from definitions.path import root_dir

# - Check for config.json, if it doesn't find it, will exit and give an error message.
if os.path.exists("{}/config.json".format(root_dir)) == False:
    sys.exit("Unable to find 'config.json'! Please add it and try again.")
else:
    with open("{}/config.json".format(root_dir)) as file:
        config = json.load(file)

def leave_server(bot):
    '''
    Sends a message in the specified channel when
    a user leaves the server.
    '''
    @bot.event
    async def on_member_remove(member):
        guild = member.guild
        channel = bot.get_channel(config["log_private"])
        await channel.send("{} has left the server.".format(member))
        print("{} has left {}.".format(member, guild))