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