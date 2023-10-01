import os
import json
import sys
from definitions.path import root_dir

# - Check for config.json, if it doesn't find it, will exit and give an error message.
if os.path.exists("{}/config.json".format(root_dir)) == False:
    sys.exit("Unable to find 'config.json'! Please add it and try again.")
else:
    with open("{}/config.json".format(root_dir)) as file:
        config = json.load(file)

def kick(bot, discord, commands):
    '''
    Kicks a member of the discord server. Sends who was kicked
    to a specified channel and for what reason.
    User can kick multiple members.
    '''
    @bot.command(name = "kick")
    @commands.has_permissions(kick_members = True)
    async def kick(ctx, members: commands.Greedy[discord.Member], *, reason = " "):
        for member in members: # - iterate over the commands.Greedy[discord.Member] list.
            await member.kick(reason = reason)
        channel = bot.get_channel(config["log_private"])
        await channel.send(f"{member} has been kicked from the server. Reason: {reason}")
        print(f"{member} has been kicked. Reason: {reason}")
    
    @kick.error # - Tells user without sufficient permissions that they don't have permissions.
    async def kick_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to kick people.")