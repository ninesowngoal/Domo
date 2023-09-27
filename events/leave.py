def leave_server(bot):
    @bot.event
    async def on_member_remove(member):
        guild = member.guild
        channel = bot.get_channel(1140664734484549765)
        await channel.send("{} has left the server.".format(member))
        print("{} has left {}.".format(member, guild))