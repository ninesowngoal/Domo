import os
import sqlite3
import discord
from discord.ext import commands
import math
import asyncio
import json
import sys
from definitions.path import root_dir

absolute_path = os.path.dirname(__file__)

# - Check for config.json, if it doesn't find it, will exit and give an error message.
if os.path.exists("{}/config.json".format(root_dir)) == False:
    sys.exit("Unable to find 'config.json'! Please add it and try again.")
else:
    with open("{}/config.json".format(root_dir)) as file:
        config = json.load(file)

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

def new_member_exp(member_exp):
    '''
    Creates a new instance of the MemberExp class
    when a new member does something to warrant
    xp tracking.
    '''
    if member_exp is None:
        member_exp = MemberExp(member_exp)
        member_exp_dict[member_exp] = member_exp
    
def calculate_voice_exp(time_spent):
    '''
    Calculates the amount of time spent in
    voice call and returns the xp earned based
    on that time.
    '''
    time_spent_minutes = (time_spent.total_seconds() - 120) / 60
    xp_earned = math.floor(time_spent_minutes * 16.67)
    return xp_earned

class Experience(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        '''
        Gives 50xp every message a user sends in
        the guild. Disregards itself as a target
        for xp.
        '''
        if message.author.bot:
            return
        
        channel = self.bot.get_channel(config["log_private"])
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
        # - Check if has Fellow Citizens already.
        has_desired_role = any(role.name == "Fellow Citizens" for role in message.author.roles)
        # - Get required guild, role and member ids.
        guild = message.guild
        role = discord.utils.get(guild.roles, name="Fellow Citizens")
        member = guild.get_member(message.author.id)

        # - Give Fellow Citizens if they don't have it. Or else don't.
        if role and member_exp.level == 7:
            if has_desired_role:
                return
            elif has_desired_role == False:
                await member.add_roles(role)
                await ctx.send(f"Congratulations <@{message.author.id}>! You are now a Fellow Citizen!")
        
        role_model = discord.utils.get(guild.roles, name="Model Citizens")

        if role_model and member_exp.level == 75:
            await member.add_roles(role_model)
            await ctx.send(f"Congratulations <@{message.author.id}>! You are a Model Citizen!")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        '''
        Timestamps when a user joins and leaves a voice channel.
        Calculates time spent and xp earned based on the total
        time spent in voice chat.
        '''
        voice_channels = [YOUR VOICE CHANNEL IDS HERE]

        if before.channel != after.channel:
            # - User joined a voice channel.
            if after.channel and after.channel.id in voice_channels:
                voice_sessions[member.id] = discord.utils.utcnow()
            # - User has left a voice channel.
            elif before.channel and before.channel.id in voice_channels:
                # - Get timestamp value of user who left the voice channel.
                start_time = voice_sessions.get(member.id)
                if start_time is not None:
                    channel = self.bot.get_channel(config["log_public"])

                    member_exp = member_exp_dict.get(member.id)
                    new_member_exp(member_exp)
                    previous_level = member_exp.level

                    # - Sleep to cover accidental disconnects and channel moving.
                    print(f"Domo will wait 2 minutes for {member.name} to come back!")
                    await asyncio.sleep(120)
                    print("Domo has finished waiting!")

                    # - Calculate time spent and xp earned.
                    end_time = discord.utils.utcnow()
                    time_spent = end_time - start_time
                    xp_earned = calculate_voice_exp(time_spent)
                    member_exp.gain_xp(xp_earned)
                    member_exp_db.save_member_exp(member.id, member_exp.level, member_exp.curr_xp)
                    await channel.send(f"<@{member.id}>, you have gained {xp_earned}xp.")
                    print(f"<{member.name}> gained {xp_earned}xp.")

                    if member_exp.level > previous_level:
                        await channel.send(f"<@{member.id}> has levelled up to level {member_exp.level}!")
                    
                    #------------Add roles for certain levels------------
                    # - Check if has Fellow Citizens already.
                    has_desired_role = any(role.name == "Fellow Citizens" for role in member.roles)
                    # - Get required guild and role.
                    guild = member.guild
                    role = discord.utils.get(guild.roles, name="Fellow Citizens")

                    if role and member_exp.level == 7:
                        if has_desired_role:
                            return
                        elif has_desired_role == False:
                            await member.add_roles(role)
                            await channel.send(f"Congratulations <@{member.id}>! You are now a Fellow Citizen!")
                    
                    role_model = discord.utils.get(guild.roles, name="Model Citizens")

                    if role_model and member_exp.level == 75:
                        await member.add_roles(role_model)
                        await channel.send(f"Congratulations <@{member.id}>! You are a Model Citizen!")

    @commands.command(name = "checklvl")
    async def check_level(self, ctx):
        absolute_path = os.path.dirname(__file__)
        db_file = os.path.join(absolute_path, "experience.db")
        db_con = sqlite3.connect(db_file)
        cur = db_con.cursor()
        member_id = ctx.author.id
        cur.execute(f"SELECT level, xp FROM experience WHERE member = ?", (member_id,))
        level_check = cur.fetchone()
        await ctx.send(f"<@{member_id}>")
        await ctx.send("Here are your details:")
        if level_check:
            await ctx.send(f"Level: {level_check[0]}")
            await ctx.send(f"XP: {level_check[1]}")
        else:
            await ctx.send("You don't have any data in the database.")
        
        db_con.close()

async def setup(bot):
    await bot.add_cog(Experience(bot))