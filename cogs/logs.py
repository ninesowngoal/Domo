import sqlite3
from discord.ext import commands
import os

# - Path to sql folder for databases.
root_dir = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '..')
    )
db_path = os.path.join(root_dir, "sql")

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
    '''
    Grabs the channel that the user was in before.
    Checks it against the channel that they just left.\n
    Sends a message when a user joins/leaves a channel.
    '''
    if before.channel != after.channel:
        voice_channel_name = after.channel.name if after.channel else before.channel.name
        if before.channel is not None:
            await channel.send(f"{member.name} left {voice_channel_name}.")
        if after.channel is not None:
                await channel.send(f"{member.name} joined {voice_channel_name}.")


async def database_check(guild, column_name, table_name):
    '''
    A function to check the database.\n
    Replace the 'column_name' and 'table_name' to
    check for data using those conditions.
    '''
    db_path = os.path.join(root_dir, "sql")
    con = sqlite3.connect(f"{db_path}/{guild}.db")
    cur = con.cursor()

    check = cur.execute(
        f"""
        SELECT {column_name}
        FROM {table_name}
        """
        )
    check_res = check.fetchone()
    con.close()
    return check_res[0]


async def toggle_on(ctx, column_name, table_name):
    '''
    Changes a 0 to a 1 in the database. Effectively
    'turning on' a Domo event or command.\n
    As with the database check function, change the
    'column_name' and 'table_name'.
    '''
    con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
    cur = con.cursor()
    cur.execute(
        f"""
        UPDATE {table_name}
        SET {column_name} = ?
        """, (1,)
    )
    con.commit()
    con.close()


async def toggle_off(ctx, column_name, table_name):
    '''
    Changes a 1 to a 0 in the database. Effectively
    'turning off' a Domo event or command.\n
    As with the database check function, change the
    'column_name' and 'table_name'.
    '''
    con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
    cur = con.cursor()
    cur.execute(
        f"""
        UPDATE {table_name}
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
    async def log_test(self, ctx):
        '''
        A command that displays the data stored in the
        'logs' table in the server database.\n
        Effectively shows what the logs channel is set to
        and the features that have been toggled on or off.
        '''
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            cur = con.cursor()
            cur.execute("SELECT * FROM logs")
            result = cur.fetchone()

            # - Process the fetched result
            logs_data = {
                "logs_chan": "None",
                "vlog_res": None,
            }

            if result is not None:
                logs_data["logs_chan"] = result[0]
                logs_data["vlog_res"] = result[1]

            # - Convert integer values to corresponding strings
            on_off_map = {0: "OFF", 1: "ON"}
            
            await ctx.send(
                f"**Logs channel:** " 
                f"{logs_data['logs_chan']}\n"
                f"**Voice logs:** " 
                f"{on_off_map.get(logs_data['vlog_res'])}\n"
                )
        except sqlite3.Error as e:
            if len(e.args) > 1:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: log_test] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: log_test] Error: {e}")
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
            if len(e.args) > 1:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: logs] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: logs] Error: {e}")
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
        guild = ctx.guild.id
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            log_chan = await database_check(guild, "channel_id", "logs")
            voice_log = await database_check(guild, "voice", "logs")

            if (log_chan is not None and
                voice_log == 0):
                await toggle_on(ctx, 'voice', 'logs')
                await ctx.send(
                "I will now send voice channel updates to the server!"
                )
                print(
                f"[COMMAND: $voicelog] Successfully turned on logs in {ctx.guild}."
                )
            elif (log_chan is not None and
                voice_log == 1):
                await toggle_off(ctx, 'voice', 'logs')
                await ctx.send(
                "I will no longer send voice channel updates to the server."
                )
                print(
                    f"[COMMAND: $voicelog] Successfully turned off logs in: {ctx.guild}."
                )
        except sqlite3.Error as e:
            if len(e.args) > 1:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: voicelog] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: voicelog] Error: {e}")
        finally:
            if con:
                con.close()


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild.id
        # Check if logs are enabled.
        con = sqlite3.connect(f"{db_path}/{guild}.db")
        try:
            chan_id = await database_check(guild, "channel_id", "logs")
            channel = member.guild.get_channel(chan_id)
            voice_log = await database_check(guild, "voice", "logs")

            # Check for logs channel id in database and if
            # voice logs are toggled on.
            if (channel is not None and
            voice_log == 1):
                await voice_state(before, after, channel, member)

        except sqlite3.Error as e:
            if len(e.args) > 1:
                print(f"[EVENT ERROR: on_voice_state_update] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                print(f"[EVENT ERROR: on_voice_state_update] Error: {e}")
        finally:
            if con:
                con.close()   


async def setup(bot):
    await bot.add_cog(Logs(bot))