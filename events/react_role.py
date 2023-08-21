def role_on_react(bot, discord):
    '''
    Domo will track the message that you specify for reactions using
    a certain custom (server) emoji.
    When a user reacts with that emoji, Domo will give the role
    specified. 
    '''
    @bot.event
    async def on_raw_reaction_add(payload):
        # Replace MESSAGE_ID with the message ID you want to track reactions on
        if payload.message_id == YOUR_MESSAGE_ID_HERE and payload.emoji.id == YOUR_SERVER_EMOJI_ID_HERE:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = discord.utils.get(guild.roles, name = "YOUR_ROLE_NAME_HERE")

            if role and member:
                await member.add_roles(role) # Gives the role specified.
                print(f"Gave {member.name} the role {role.name}")
        '''
        UNCOMMENT THIS CODE AND CHANGE ROLE VARIABLE TO ADD ANOTHER MESSAGE OR REACTION
        FOR THE BOT TO TRACK REACTIONS ON.

        if payload.message_id == YOUR_MESSAGE_ID_HERE and payload.emoji.id == YOUR_SERVER_EMOJI_ID_HERE:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role_two = discord.utils.get(guild.roles, name="YOUR_ROLE_NAME_HERE")

            if role_two and member:
                await member.add_roles(role_fc)
                print(f"Gave {member.name} the role {role_two.name}")
        '''