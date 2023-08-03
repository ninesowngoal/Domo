# - Domo will log who has left the server in the specified channel.
# - Replace YOUR_CHANNEL_ID_HERE with the channel you want the message to be sent to.
def leave_server(bot):
    @bot.event
    async def on_member_remove(member):
        guild = member.guild #Grabs the server id of the current server.
        channel = bot.get_channel(YOUR_CHANNEL_ID_HERE)
        await channel.send("{} has left the server.".format(member))
        print("{} has left {}.".format(member, guild))