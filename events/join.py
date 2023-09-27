def join_server(bot):
    '''
    Sends a DM when a user joins the server.
    Also sends a message in #immigration-office.
    '''
    @bot.event
    async def on_member_join(member):
        guild = member.guild
        await member.send(f"Welcome to {guild}, {member}! \n Please make sure to read the message in #welcome-citizen.") 
        print(f"{member} has joined {guild}.") # - shows who joined in bot terminal.
        channel = bot.get_channel(1140664734484549765)
        await channel.send(f"{member} has entered {guild}.")