import sqlite3
from discord.ext import commands
import os
root_dir = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '..')
    )

async def log_cmd_first(cur, con, ctx):
    '''
    Sets the log channel to the channel
    the command was executed in.
    For the first time the command is
    executed.
    '''
    cur.execute("""
                INSERT INTO logs (channel_id)
                SELECT ?
                WHERE channel_id IS NULL
                """, (ctx.channel.id,))
    con.commit()
    con.close()
    await ctx.send("Logs will now be sent to this channel.")
    print(
        f"[COMMAND: $logs] Executed successfully in: {ctx.guild.name}. "
        f"Set logs channel to: {ctx.channel.name}"
        )


async def log_cmd_second(cur, con, ctx):
    '''
    Updates the log channel to the channel
    the $logs command was called in.
    Must have been called in a different
    channel to the original.
    '''
    cur.execute("""
                UPDATE logs
                SET channel_id = ?
                """, (ctx.channel.id,))
    con.commit()
    con.close()
    # - New logs channel set.
    await ctx.send(
        "Logs channel updated. " 
        "Now sending logs to this channel.")
    print(
        "[COMMAND: $logs] " 
        f"Successfully updated the logs channel to: {ctx.channel.name}, "
        f"for: {ctx.guild.name}.")


async def log_cmd_off(cur, con, ctx):
    '''
    Turns off the logging feature when
    the command is called in the same
    channel as the designated logs
    channel.
    '''
    cur.execute(f"""
                UPDATE logs
                SET channel_id = NULL
                """)
    con.commit()
    con.close()
    await ctx.send(
        "Logs will no longer be sent in this server."
        )
    print(
        "[COMMAND: $logs] Turned off feature for: " 
        f"{ctx.guild.name}."
        )


async def voice_state(before, after, channel, member):
    if before.channel != after.channel:
        voice_channel_name = after.channel.name if after.channel else before.channel.name
        if before.channel:
            await channel.send(f"{member.name} left {voice_channel_name}.")
            print(f"{member.name} left {voice_channel_name}.")
        if after.channel:
                await channel.send(f"{member.name} joined {voice_channel_name}.")
                print(f"{member.name} joined {voice_channel_name}")


async def log_check(guild, column_name):
    db_path = os.path.join(root_dir, "sql")
    con = sqlite3.connect(f"{db_path}/{guild.id}.db")
    cur = con.cursor()

    check = cur.execute(
        f"""
        SELECT {column_name}
        FROM logs
        """
        )
    check_res = check.fetchone()
    con.close()
    return check_res[0]


async def turn_on_logs(ctx, column_name):
    db_path = os.path.join(root_dir, "sql")
    con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
    cur = con.cursor()

    cur.execute(
        f"""
        UPDATE logs
        SET {column_name} = ?
        """, (1,)
    )
    con.commit()
    con.close()


async def turn_off_logs(ctx, column_name):
    db_path = os.path.join(root_dir, "sql")
    con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
    cur = con.cursor()

    cur.execute(
        f"""
        UPDATE logs
        SET {column_name} = ?
        """, (0,)
    )
    con.commit()
    con.close()


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command(name = "logtest")
    @commands.has_permissions(administrator = True)
    async def test(self, ctx):
        guild = ctx.guild
        root_dir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), '..')
        )
        db_path = os.path.join(root_dir, "sql")
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            log_res = await log_check(guild, "channel_id")
            vlog_res = await log_check(guild, "voice")
            vlog_res_map = {0: "OFF", 1: "ON"}
            jlog_res = await log_check(guild, "user_join")
            jlog_res_map = {0: "OFF", 1: "ON"}
            await ctx.send(
                f"Logs channel: {log_res}\n"
                f"Voice logs: {vlog_res_map.get(vlog_res)}\n"
                f"Join message: {jlog_res_map.get(jlog_res)}"
                )
        except sqlite3.Error as e:
            await ctx.send("Command failed, check terminal.")
            print(e)
        finally:
            if con:
                con.close()


    @commands.command(name = "logs", aliases = ["log"])
    @commands.has_permissions(administrator = True)
    async def logs(self, ctx):
        '''
        Will toggle bot logs being sent to the text channel
        that this command was entered in.
        Stores the preference in a SQL database.
        '''
        root_dir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), '..')
            )
        db_path = os.path.join(root_dir, "sql")
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        cur = con.cursor()
        try:
            # - Check if logs are enabled by checking
            # - for a channel id entry for the server.
            cur.execute("SELECT channel_id FROM logs")
            chan_check_res = cur.fetchone()

            # - No channel id. First time set.
            if (chan_check_res is None):
                await log_cmd_first(cur, con, ctx)
            # - Found channel id. After first time set.
            elif chan_check_res[0] != ctx.channel.id:
                await log_cmd_second(cur, con, ctx)
            elif ctx.channel.id == chan_check_res[0]:
                await log_cmd_off(cur, con, ctx)
        except sqlite3.Error as e:
            await ctx.send(
                "I cannot execute the command. " 
                "Please check my terminal!"
                )
            print(f"[COMMAND ERROR: $logs] Error: {e} ")
        finally:
            if con:
                con.close()
    

    @commands.command(name = "voicelog", aliases = ["vlog"])
    @commands.has_permissions(administrator = True)
    async def voicelog(self, ctx):
        '''
        Toggles logs that will tell you who joined or
        left a voice channel at any time.
        Requires you to set a 'logs' channel by using
        the $logs command.
        '''
        guild = ctx.guild
        root_dir = os.path.realpath(
        os.path.join(os.path.dirname(__file__), '..'))
        db_path = os.path.join(root_dir, "sql")
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            log_chan = await log_check(guild, 'channel_id')
            voice_log = await log_check(guild, 'voice')

            if (log_chan is not None and
                voice_log == 0):
                await turn_on_logs(ctx, 'voice')
                await ctx.send(
                "I will now send voice channel updates to the server!"
                )
                print(
                f"[COMMAND: $voicelog] Successfully turned on logs in {ctx.guild}."
                )
            elif (log_chan is not None and
                voice_log == 1):
                await turn_off_logs(ctx, 'voice')
                await ctx.send(
                "I will no longer send voice channel updates to the server."
                )
                print(
                    f"[COMMAND: $voicelog] Successfully turned off logs in: {ctx.guild}."
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
    async def on_voice_state_update(self, member, before, after):
        ctx = member.guild
        guild = ctx
        # - Check if logs enabled.
        root_dir = os.path.realpath(
        os.path.join(os.path.dirname(__file__), '..'))
        db_path = os.path.join(root_dir, "sql")
        con = sqlite3.connect(f"{db_path}/{ctx.id}.db")
        try:
            chan_id = await log_check(guild, 'channel_id')
            channel = ctx.get_channel(chan_id)
            voice_log = await log_check(guild, 'voice')

            if (channel is not None and
            voice_log == 1):
                await voice_state(before, after, channel, member)

        except sqlite3.Error as e:
            print(f"[VOICE_STATE_UPDATE] Error: {e}")
        finally:
            if con:
                con.close()


async def setup(bot):
    await bot.add_cog(Logs(bot))