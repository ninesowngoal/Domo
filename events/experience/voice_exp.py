#import datetime
#from datetime import datetime, timedelta
from definitions.classes import MemberVoice
from definitions.classes import MemberExpDatabase as mem_xp_db
from events.experience.text_exp import load_data_from_database as load_db

# - Create an instance of MemberExpDatabase
member_exp_db = mem_xp_db()

# - Dictionary to store MemberExp instances by member_id
member_exp_dict = {}

# - Load data from the database when the bot starts
load_db()

# - Library to assign users to times
voice_sessions = {}

def member_voice_exp(bot):
    @bot.event
    async def on_voice_state_update(member, before, after):
        # - Checks when a user has joined the voice channel
        # - and awards xp based on how long they have been
        # - in the voice channel for.
        member_id = member.id

        if before.channel != after.channel:
            # - User joined a voice channel
            if after.channel is not None:
            # User joined a voice channel
                if member_id not in voice_sessions:
                    voice_sessions[member_id] = MemberVoice(member_id)
                voice_sessions[member_id].join_voice()
        elif before.channel is not None and member_id in voice_sessions:
            # User left a voice channel
            voice_sessions[member_id].leave_voice()
            xp_earned = voice_sessions[member_id].calculate_xp()
            print(f"{member_id} earned {xp_earned} XP.")
    
    #time_spent_in_voice = (for loop)
    
    '''@tasks.loop(minutes=1)
    async def calculate_voice_time(member):
        member_id = member.id
        if member_id in voice_sessions and len(voice_sessions[member.id]) % 2 == 0:
            total_time = sum((voice_sessions[member.id][i + 1] - voice_sessions[member.id][i] for i in range(0, len(voice_sessions[member.id]), 2)), timedelta())
        else:
            return timedelta()
        
        channel = bot.get_channel(559167491985899530)
        member_exp = member_exp_dict.get(member.id)

        if member_exp is None:
            member_exp = memxp(member.id)
            member_exp_dict[member.id] = member_exp
        
        previous_level = member_exp.level

        xp_earned = total_time * 16.67  # XP per minute
        member_exp.gain_xp(xp_earned)
        member_exp_db.save_member_exp(member.id, member_exp.level, member_exp.curr_xp)
        print(xp_earned)

        if member_exp.level > previous_level:
            await channel.send(f"<@{member.id}> has levelled up to level {member_exp.level}!")'''
    '''
    @calculate_voice_time.before_loop
    async def before_calculate_voice_time():
        await bot.wait_until_ready()

    @calculate_voice_time.after_loop
    async def after_calculate_voice_time():
        print("Voice chat xp calculation stopped.")
    
    calculate_voice_time.start()
    '''