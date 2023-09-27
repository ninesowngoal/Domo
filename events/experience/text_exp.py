import sqlite3
import os
from definitions.classes import MemberExp
from definitions.classes import MemberExpDatabase

# Function to load data from the database into the dictionary on bot startup
def load_data_from_database():
    absolute_path = os.path.dirname(__file__)
    db_file = os.path.join(absolute_path, "experience.db")
    db_con = sqlite3.connect(db_file)
    cur = db_con.cursor()

    # Fetch data from the database and update the member_exp_dict
    cur.execute("SELECT member, level, xp FROM experience")
    data = cur.fetchall()

    for member_id, level, curr_xp in data:
        if member_id not in member_exp_dict:
            member_exp = MemberExp(member_id)
            member_exp.level = level
            member_exp.curr_xp = curr_xp
            member_exp_dict[member_id] = member_exp
        else:
            member_exp_dict[member_id].level = level
            member_exp_dict[member_id].curr_xp = curr_xp

    db_con.close()

# - Create an instance of MemberExpDatabase
member_exp_db = MemberExpDatabase()

# - Dictionary to store MemberExp instances by member_id
member_exp_dict = {}

# Load data from the database when the bot starts
load_data_from_database()

def member_text_exp(bot, discord):
    '''
    Gives members of a server 50xp per message. Ignores it if its
    from a bot. Sends a message when a user has levelled up.
    '''
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        guild = bot.get_guild(240758377913778177)
        member_id = message.author.id
        channel = bot.get_channel(1140664734484549765)
        ctx = await bot.get_context(message)

        # - Gets or creates a MemberExp instance for the member
        member_exp = member_exp_dict.get(member_id)
        if member_exp is None:
            member_exp = MemberExp(member_id)
            member_exp_dict[member_id] = member_exp

        # - Stores the previous level before gaining XP
        previous_level = member_exp.level

        # - Gain XP for the message and saves to the database
        member_exp.gain_xp(50)  # - 50 XP per message
        member_exp_db.save_member_exp(member_id, member_exp.level, member_exp.curr_xp)

        # - Check if the member has leveled up
        if member_exp.level > previous_level:
            await ctx.send(f"<@{message.author.id}> has levelled up to level {member_exp.level}!")
            await channel.send(f"{message.author} has levelled up to level {member_exp.level}!")
        
        absolute_path = os.path.dirname(__file__)
        db_file = os.path.join(absolute_path, "experience.db")
        db_con = sqlite3.connect(db_file)
        
        db_con.set_trace_callback(member_text_exp)
        db_con.close()