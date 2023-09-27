import os
import sqlite3
import discord
from discord.ext import commands
import math

absolute_path = os.path.dirname(__file__)

class MemberExp:
    # - Class to store exp and level for each member.
    def __init__(self, member_id):
        self.member_id = member_id
        self.level = 0
        self.curr_xp = 0
        self.xp_to_next = 1000

    # - Calculate exp to next for level up.
    def gain_xp(self, amount):
        self.curr_xp += amount
        while self.curr_xp >= self.xp_to_next:
            self.level_up()

    # - Calculate level up.
    def level_up(self):
        self.curr_xp -= self.xp_to_next
        self.xp_to_next = 1000
        self.level += 1

class MemberExpDatabase:
    # - SQL database for member, exp and level.
    def __init__(self):
        db_file = os.path.join(absolute_path, "experience.db")
        self.db_connection = sqlite3.connect(db_file)
        self.create_table()

    def create_table(self):
        # - Create the 'experience' database if it doesn't exist
        self.db_connection.execute('''
            CREATE TABLE IF NOT EXISTS experience (
                member INTEGER PRIMARY KEY,
                level INTEGER,
                xp INTEGER
            )
        ''')
        self.db_connection.commit()

    def save_member_exp(self, member_id, level, curr_xp):
        self.db_connection.execute("INSERT OR REPLACE INTO experience(member, level, xp) VALUES (?, ?, ?)",
                                   (member_id, level, curr_xp))
        self.db_connection.commit()

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

# - Library to assign users to times
voice_sessions = {}

# Load data from the database when the bot starts
load_data_from_database()

class Experience(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        channel = self.bot.get_channel(YOUR CHANNEL ID HERE)
        ctx = await self.bot.get_context(message)

        # - Get or create a MemberExp instance.
        member_exp = member_exp_dict.get(message.author.id)
        if member_exp is None:
            member_exp = MemberExp(message.author.id)
            member_exp_dict[message.author.id] = member_exp

        # - Store previous level.
        previous_level = member_exp.level

        # - Gain XP for message. Save to database.
        member_exp.gain_xp(50)
        member_exp_db.save_member_exp(message.author.id, member_exp.level, member_exp.curr_xp)

        # - Check if member has levelled up.
        if member_exp.level > previous_level:
            await ctx.send(f"<@{message.author.id}> has levelled up to level {member_exp.level}!")
            await channel.send(f"{message.author} is now level {member_exp.level}.")
        
        #------------Add roles for certain levels------------
        # - Check if has desired role already.
        has_desired_role = any(role.name == "YOUR ROLE NAME HERE" for role in message.author.roles)
        # - Get required guild, role and member ids.
        guild = message.guild
        role = discord.utils.get(guild.roles, name="YOUR ROLE NAME HERE")
        member = guild.get_member(message.author.id)

        # - Give desired role if they don't have it. Or else don't.
        if role and member_exp.level == 7:
            if has_desired_role:
                return
            elif has_desired_role == False:
                await member.add_roles(role)
                await ctx.send(f"Congratulations <@{message.author.id}>! You are now a {role}!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            # - User joined a voice channel.
            if after.channel is not None:
                voice_sessions[member.id] = discord.utils.utcnow()
            elif before.channel is not None:
                start_time = voice_sessions.get(member.id)
                if start_time is not None:
                    end_time = discord.utils.utcnow()
                    time_spent = end_time - start_time

                    channel = self.bot.get_channel(YOUR CHANNEL ID HERE)
                    member_exp = member_exp_dict.get(member.id)

                    if member_exp is None:
                        member_exp = MemberExp(member.id)
                        member_exp_dict[member.id] = member_exp
                    
                    previous_level = member_exp.level

                    time_spent_minutes = time_spent.total_seconds() / 60
                    xp_earned = math.floor(time_spent_minutes * 16.67) # - adjust 16.67 as you wish
                    member_exp.gain_xp(math.floor(xp_earned))
                    member_exp_db.save_member_exp(member.id, member_exp.level, member_exp.curr_xp)
                    await channel.send(f"<@{member.id}>, you have gained {xp_earned}xp.")
                    print(f"<{member.id}> gained {xp_earned}xp.")

                    if member_exp.level > previous_level:
                        await channel.send(f"<@{member.id}> has levelled up to level {member_exp.level}!")
                    
                    #------------Add roles for certain levels------------
                    # - Check if has desired role already.
                    has_desired_role = any(role.name == "YOUR ROLE NAME HERE" for role in member.roles)
                    # - Get required guild and role.
                    guild = member.guild
                    role = discord.utils.get(guild.roles, name="YOUR ROLE NAME HERE")

                    if role and member_exp.level == 7:
                        if has_desired_role:
                            return
                        elif has_desired_role == False:
                            await member.add_roles(role)
                            await channel.send(f"Congratulations <@{member.id}>! You are now a {role}!")

async def setup(bot):
    await bot.add_cog(Experience(bot))