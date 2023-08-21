def ban(bot, discord, commands):
    '''
    Bans a member of the discord server. Sends who was banned
    to a specified channel and for what reason. User can ban
    multiple members.
    '''
    @bot.command()
    @commands.has_permissions(ban_members = True)
    async def ban(ctx, members: commands.Greedy[discord.Member], *, reason = " "):
        for member in members:
            await member.ban(reason = reason)
        channel = bot.get_channel(YOUR_CHANNEL_ID_HERE) # - Bot-logs text channel.
        await member.ban(reason = reason)
        await channel.send(f"{member} has been banned from the server. Reason: {reason}")
        print(f"{member} has been banned. Reason: {reason}") # - Prints who was banned in terminal.
    
    @ban.error # - Tells user without sufficient permissions that they don't have permissions.
    async def ban_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to ban people.")