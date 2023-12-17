import sqlite3
import time
import discord
from discord.ext import commands
import os
root_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

async def log_cmd_first(cur, con, ctx):
    '''
    Sets the log channel to the channel
    the command was executed in.
    For the first time the command is
    executed.
    '''
    cur.execute(f"""
                UPDATE logs
                SET state = 1, channel_id = {ctx.channel.id}
                WHERE server_id = {ctx.guild.id}
                """)
    con.commit()
    con.close()
    await ctx.send("Logs will now be sent to this channel.")
    print(f"""[COMMAND: $logs] Executed successfully in: {ctx.guild.name}.
                 Set logs channel to: {ctx.channel.name}""")

async def log_cmd_second(cur, con, ctx):
    '''
    Updates the log channel to the channel
    the $logs command was called in.
    Must have been called in a different
    channel to the original.
    '''
    cur.execute(f"""
                UPDATE logs
                SET channel_id = {ctx.channel.id}
                WHERE server_id = {ctx.guild.id}
                """)
    con.commit()
    con.close()
    # - New logs channel set.
    await ctx.send("Logs channel updated. Sending logs to this channel instead.")
    print(f"""[COMMAND: $logs] Successfully updated the logs channel to: {ctx.channel.name},
                 for: {ctx.guild.name}.""")

async def log_cmd_off(cur, con, ctx):
    '''
    Turns off the logging feature when
    the command is called in the same
    channel as the designated logs
    channel.
    '''
    cur.execute(f"""
                UPDATE logs
                SET channel_id = NULL, state = 0
                WHERE server_id = {ctx.guild.id}
                """)
    con.commit()
    con.close()
    await ctx.send("Logs will no longer be sent in this server.")
    print(f"[COMMAND: $logs] Turned off feature for: {ctx.guild.name}.")

class Administration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name = "logs")
    @commands.has_permissions(administrator = True)
    async def logs(self, ctx):
        '''
        Will toggle bot logs being sent to the text channel
        that this command was entered in.
        Stores the preference in a SQL database.
        '''
        root_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
        db_path = os.path.join(root_dir, "sql")
        con = sqlite3.connect(f"{db_path}/toggles.db")
        cur = con.cursor()
        try:
            # - Check if logs are on or off for the server.
            state_check = cur.execute(f"SELECT state FROM logs WHERE server_id = {ctx.guild.id}")
            state_check_res = state_check.fetchone()
            # - Check for a channel id entry for the server.
            chan_check = cur.execute(f"SELECT channel_id FROM logs WHERE server_id = {ctx.guild.id}")
            chan_check_res = chan_check.fetchone()

            if chan_check_res[0] is None and state_check_res[0] == 0:
                await log_cmd_first(cur, con, ctx)
            elif chan_check_res[0] is not None and state_check_res[0] == 1:
                if ctx.channel.id != chan_check_res[0]:
                    await log_cmd_second(cur, con, ctx)
                elif ctx.channel.id == chan_check_res[0]:
                    await log_cmd_off(cur, con, ctx)
        except sqlite3.Error as e:
            await ctx.send("I cannot execute the command. Please check my terminal!")
            print(f"[COMMAND ERROR: $logs] Error: {e} ")
        finally:
            con.close()

    @commands.command(name = "kick")
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason=""):
        '''
        Kicks a member of the discord server.
        If the admin of the server has specified a channel
        for logs, Domo will send who was kicked there as well.
        Saves who has been kicked into the server database.
        Multiple members can be kicked.
        '''
        for member in members:
            await member.kick(reason=reason)

        db_path = os.path.join(root_dir, "sql")
        log_con = sqlite3.connect(f"{db_path}/toggles.db")
        log_cur = log_con.cursor()

        # - Check if logs are enabled in the server.
        channel_check = log_cur.execute(f"SELECT channel_id FROM logs WHERE server_id = {ctx.guild.id}")
        channel = channel_check.fetchone()
        if channel[0] is not None:
            await channel.send(f"{member} has been kicked from the server. Reason: {reason}")
        else:
            pass
        await ctx.send(f"{member} has been kicked from the server. Reason: {reason}")
        print(f"{member} has been kicked. Reason: {reason}")

        kick_con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        kick_cur = kick_con.cursor()
        date = int(time.time())

        kick_cur.execute("INSERT INTO kick (member, reason, date) VALUES (?, ?, ?)", 
                        (member, reason, date))
        kick_con.commit()
        kick_con.close()

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to kick people.")
    
    @commands.command(name="kick-log")
    @commands.has_permissions(administrator = True)
    async def kick_log(self, ctx):
        db_path = os.path.join(root_dir, "sql")
        kick_con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        kick_cur = kick_con.cursor()
        
        for row in kick_cur.execute(f"SELECT member, reason, date FROM kick ORDER BY date"):
            await ctx.send(row)
            #await ctx.send(f"{kick_cur[0]} \n Date: {kick_cur[2]} \n Reason: {kick_cur[1]}")
            kick_con.close()
    
    @kick_log.error
    async def kick_log_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the required permission: Admin.")
    
    @commands.command(name = "ban")
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member], *, reason=""):
        '''
        Bans a member of the discord server.
        If the admin of the server has specified a channel
        for logs, Domo will send who was banned there as well.
        Saves who has been banned into the server database.
        Multiple members can be banned.
        '''
        for member in members:
            await member.ban(reason=reason)

        db_path = os.path.join(root_dir, "sql")
        log_con = sqlite3.connect(f"{db_path}/toggles.db")
        log_cur = log_con.cursor()

        # - Check if logs are enabled in the server.
        channel_check = log_cur.execute(f"SELECT channel_id FROM logs WHERE server_id = {ctx.guild.id}")
        channel = channel_check.fetchone()
        if channel[0] is not None:
            await channel.send(f"{member} has been banned from the server. Reason: {reason}")
        else:
            pass
        await ctx.send(f"{member} has been banned from the server. Reason: {reason}")
        print(f"{member} has been banned. Reason: {reason}")

        ban_con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        ban_cur = ban_con.cursor()
        date = int(time.time())

        ban_cur.execute("INSERT INTO ban (member, date, reason) VALUES (?, ?, ?)", 
                        (member, reason, date))
        ban_con.commit()
        ban_con.close()

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to ban people.")
    
    @commands.command(name="ban-log")
    @commands.has_permissions(administrator = True)
    async def ban_log(self, ctx):
        db_path = os.path.join(root_dir, "sql")
        ban_con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        ban_cur = ban_con.cursor()
        
        for row in ban_cur.execute(f"SELECT member, reason, date FROM ban ORDER BY date"):
            await ctx.send(row)
            #await ctx.send(f"{kick_cur[0]} \n Date: {kick_cur[2]} \n Reason: {kick_cur[1]}")
        ban_con.close()
    
    @ban_log.error
    async def ban_log_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the required permission: Admin.")

async def setup(bot):
    await bot.add_cog(Administration(bot))