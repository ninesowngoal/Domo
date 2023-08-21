def voice_log(bot):
    '''
    Will send a message to the specified text channel
    about who has either joined or left a voice channel.
    '''
    @bot.event
    async def on_voice_state_update(member, before, after):
        channel = bot.get_channel(YOUR_CHANNEL_ID_HERE)
        if before.channel != after.channel:
            voice_channel_name = after.channel.name if after.channel else before.channel.name
            #-----Leaving the voice channel-----
            if before.channel:
                await channel.send(f"{member.name} left {voice_channel_name}.")
                print(f"{member.name} left {voice_channel_name}.")
            #-----Joining the voice channel-----
            if after.channel:
                await channel.send(f"{member.name} joined {voice_channel_name}")
                print(f"{member.name} joined {voice_channel_name}")