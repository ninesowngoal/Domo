def kick(bot, discord, commands):
    '''
    Kicks a member of the discord server. Prints who was kicked in the same channel.
    Can only be done by a user with sufficient permissions.
    '''
    @bot.command(name = "kick")
    @commands.has_permissions(kick_members = True)
    async def kick(ctx, member: discord.Member, *, reason=None): #reason = none, bot won't give a reason for kick. Change so user can give a reason.
        await member.kick(reason = reason)
        await ctx.send(f"{member} has been kicked.") #sends who was kicked in #admin-only.
        channel = bot.get_channel(839557877567455233)
        await channel.send(f"{member} has been kicked from the server.")
        print(f"{member} has been kicked.") #prints who was kicked in terminal.
    
    @kick.error #if someone who isn't a mod or admin tries to kick, it tells them that they don't have permissions.
    async def kick_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to kick people.")