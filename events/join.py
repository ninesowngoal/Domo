def join_server(bot):
    '''
    Sends a DM when a user joins the server.
    Also sends a message to the specified text channel.
    '''
    @bot.event
    async def on_member_join(member):
        guild = member.guild # - grabs server id of the current server.
        await member.send("YOUR_DM_WELCOME_MESSAGE_HERE") 
        print(f"{member} has joined {guild}.") # - shows who joined in bot terminal.
        channel = bot.get_channel(YOUR_CHANNEL_ID_HERE) # - specify channel to send message below to.
        await channel.send(f"{member} has entered {guild}.")