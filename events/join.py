def join_server(bot):
    '''
    Sends a DM when a user joins the server.
    Can also send a message to a channel that you specify here.
    Delete the last two lines of code if you don't want that feature.
    '''
    @bot.event
    async def on_member_join(member):
        guild = member.guild
        await member.send("Welcome to {} {}! \n Please read #welcome-citizen as you may need a certain role.".format(guild, member)) 
        print("{} has joined The Dome.".format(member)) # - Shows who joined in terminal.
        channel = bot.get_channel(YOUR_CHANNEL_ID_HERE) # - Sends welcome message in the specified channel.
        await channel.send("Welcome {}!".format(member))