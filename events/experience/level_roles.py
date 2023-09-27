import sqlite3
import os
from definitions.classes import MemberExp
from definitions.classes import MemberExpDatabase
from events.experience.text_exp import load_data_from_database
from events.experience.text_exp import member_exp_dict

member_exp_db = MemberExpDatabase()
member_exp_dict
load_data_from_database()

def level_up_role(bot, discord):
    @bot.event
    async def on_message(message):
        guild = bot.get_guild(240758377913778177)
        member_id = message.author.id
        member_exp = member_exp_dict.get(member_id) # - get member id from library
        role = discord.utils.get(guild.roles, name="Fellow Citizens")
        ctx = await bot.get_context(message)
        channel = bot.get_channel(1140664734484549765)

        if member_exp is None: # - new entry to dictionary
            member_exp = MemberExp(member_id)
            member_exp_dict[member_id] = member_exp

        absolute_path = os.path.dirname(__file__)
        db_file = os.path.join(absolute_path, "experience.db")
        db_con = sqlite3.connect(db_file)
        db_cur = db_con.cursor()
        db_cur.execute("SELECT level FROM experience WHERE member=?")
        db_mem_lvl = db_cur.fetchone()

        print(f"db_mem_lvl: {db_mem_lvl}")

        if db_mem_lvl and db_mem_lvl[0] == 7:
            member = guild.get_member(member_id)
            if role and member:
                await member.add_roles(role)
                await ctx.send(f"Congratulations <@{message.author.id}>! You are now a Fellow Citizen!")
                await channel.send(f"{message.author} is now a Fellow Citizen.")
                print(f"Gave {message.author} Fellow Citizens.")