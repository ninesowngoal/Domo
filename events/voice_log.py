def voice_log(bot):
    @bot.event
    async def on_voice_state_update(member, before, after):
        channel = bot.get_channel(1140664734484549765)
        if before.channel != after.channel:
            voice_channel_name = after.channel.name if after.channel else before.channel.name
            if before.channel:
                await channel.send(f"{member.name} left {voice_channel_name}.")
                print(f"{member.name} left {voice_channel_name}.")
            if after.channel:
                await channel.send(f"{member.name} joined {voice_channel_name}.")
                print(f"{member.name} joined {voice_channel_name}")

# - Put voice_exp here.