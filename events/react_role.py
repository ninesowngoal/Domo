def role_on_react(bot, discord):
    @bot.event
    async def on_raw_reaction_add(payload):
        # Replace MESSAGE_ID with the message ID you want to track reactions on
        if payload.message_id == 1134952357252313142 and payload.emoji.id == 812184626659065866:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            channel = bot.get_channel(1140664734484549765)
            role = discord.utils.get(guild.roles, name="Star City")

            if role and member:
                await member.add_roles(role)
                await channel.send(f"Gave {member.name} the role: {role.name}.")
                print(f"Gave {member.name} the role: {role.name}")

        if payload.message_id == 1134952357252313142 and payload.emoji.id == 820088519468908614:
            guild = bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            channel = bot.get_channel(1140664734484549765)
            role_im = discord.utils.get(guild.roles, name="Immigrants")

            if role_im and member:
                await member.add_roles(role_im)
                await channel.send(f"Gave {member.name} the role: {role_im.name}.")
                print(f"Gave {member.name} the role {role_im.name}")