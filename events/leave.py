def leave_server(bot):
    '''
    Sends a message in the specified channel when
    a user leaves the server.
    '''
    @bot.event
    async def on_member_remove(member):
        guild = member.guild
        channel = bot.get_channel(YOUR CHANNEL ID HERE)
        await channel.send("{} has left the server.".format(member))
        print("{} has left {}.".format(member, guild))