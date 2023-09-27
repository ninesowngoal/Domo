def voice_log(bot):
    @bot.event
    async def on_voice_state_update(member, before, after):
        '''
        Logs who has joined or left a voice channel.
        Sends a message of who joined or left in a specified
        channel.
        '''
        channel = bot.get_channel(YOUR CHANNEL HERE) # - sends message in specified channel.
        if before.channel != after.channel:
            voice_channel_name = after.channel.name if after.channel else before.channel.name
            # - when a user leaves a vc.
            if before.channel:
                await channel.send(f"{member.name} left {voice_channel_name}.")
                print(f"{member.name} left {voice_channel_name}.")
            # - when a user joins a vc.
            if after.channel:
                await channel.send(f"{member.name} joined {voice_channel_name}.")
                print(f"{member.name} joined {voice_channel_name}")