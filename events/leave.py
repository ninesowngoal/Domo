def leave_server(bot):
    '''
    Sends a message of who left the server in the
    specified text channel. Will also print the
    same in the bot terminal.
    '''
    @bot.event
    async def on_member_remove(member):
        guild = member.guild # - Grabs the server id of the current server.
        channel = bot.get_channel(YOUR_CHANNEL_ID_HERE)
        await channel.send("{} has left the server.".format(member))
        print("{} has left {}.".format(member, guild))