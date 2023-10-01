import os
import sys
import json
from definitions.path import root_dir

# - Check for config.json, if it doesn't find it, will exit and give an error message.
if os.path.exists("{}/config.json".format(root_dir)) == False:
    sys.exit("Unable to find 'config.json'! Please add it and try again.")
else:
    with open("{}/config.json".format(root_dir)) as file:
        config = json.load(file)

def role_on_react(bot, discord):
    @bot.event
    async def on_raw_reaction_add(payload):
        # Replace MESSAGE_ID with the message ID you want to track reactions on
        if payload.message_id == YOUR MESSAGE ID HERE and payload.emoji.id == YOUR EMOJI ID HERE:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            channel = bot.get_channel(config["log_private"])
            role = discord.utils.get(guild.roles, name="YOUR ROLE NAME HERE")

            if role and member: # - checks if the role and member id exist.
                await member.add_roles(role)
                await channel.send(f"Gave {member.name} the role: {role.name}.")
                print(f"Gave {member.name} the role: {role.name}")

# - COPY LINES 5 TO 14 TO MAKE A NEW MESSAGE/ROLE TO REACT TO, 
# - CHANGE THE ROLE/EMOJI ID/MESSAGE ID TO HAVE: A NEW ROLE TO 
# - ADD ON REACT, NEW EMOJI TO LISTEN FOR, MESSAGE ID TO TRACK. 