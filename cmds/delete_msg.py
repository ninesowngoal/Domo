def delete_msgs(bot, commands):
    @bot.command
    @commands.has_permissions(manage_messages = True)
    async def delete(ctx):
        await ctx