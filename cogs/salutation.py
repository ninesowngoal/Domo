import sqlite3
from discord.ext import commands
import os
from logs import log_check, turn_on_logs, turn_off_logs
root_dir = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '..')
    )

class Salutation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "joinlog", aliases = ["jlog"])
    @commands.has_permissions(administrator = True)
    async def joinlog(self, ctx):
        guild = ctx.guild
        root_dir = os.path.realpath(
        os.path.join(os.path.dirname(__file__), '..'))
        db_path = os.path.join(root_dir, "sql")
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            log_chan = await log_check(guild, 'channel_id')
            join_log = await log_check(guild, 'user_join')

            if (log_chan is not None and
                join_log == 0):
                await turn_on_logs(ctx, 'user_join')
                await ctx.send(
                "I will now send a message when someone joins the server!"
                )
                print(
                f"[COMMAND: $joinlog] Successfully turned on logs in {ctx.guild}."
                )
            elif (log_chan is not None and
                join_log == 1):
                await turn_off_logs(ctx, 'user_join')
                await ctx.send(
                "I will no longer send a message when someone joins the server."
                )
                print(
                    f"[COMMAND: $joinlog] Successfully turned off logs in: {ctx.guild}."
                )
        except sqlite3.Error as e:
            await ctx.send(
                "I cannot execute the command. "
                "Please check my terminal and logs!"
            )
            print(f"[COMMAND: $voicelog] Error: {e}")
        finally:
            if con:
                con.close()

    @commands.Cog.listener()
    async def on_member_join(member):
        guild = member.guild
        ctx = guild
        # - For sql database connections.
        # - To make sure all connections are closed.
        root_dir = os.path.realpath(
        os.path.join(os.path.dirname(__file__), '..'))
        db_path = os.path.join(root_dir, "sql")
        con = sqlite3.connect(f"{db_path}/{ctx.id}.db")
        try:
            chan_id = await log_check(guild, 'channel_id')
            channel = ctx.get_channel(chan_id)
            join_log = await log_check(guild, 'user_join')

            if (channel is not None and
                join_log == 1):
                await member.send(f"Welcome to {guild}, {member}!") 
                await channel.send(f"{member} has entered {guild}.")
        except sqlite3.Error as e:
            print(f"[ON_MEMBER_JOIN] Error: {e}")
        finally:
            if con:
                con.close()