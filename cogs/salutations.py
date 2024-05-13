import sqlite3
from discord.ext import commands
import os
from cogs.logs import database_check, toggle_on, toggle_off

# - Path to sql folder for databases.
root_dir = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '..')
    )
db_path = os.path.join(root_dir, "sql")

async def set_logs_channel(cur, con, ctx):
    cur.execute(
        """
        UPDATE salutations
        SET channel_id = ?
        """,
        (ctx.channel.id,)
        )
    con.commit()
    con.close()
    await ctx.send(
        "Salutations channel set.\n"
        "Sending salutations to this channel."
        )
    print(
        "[COMMAND: $salchannel] "
        f"Successfully set salutations channel to: {ctx.channel.id} "
        f"for: {ctx.guild.name}"
        )
    

async def unset_logs_channel(cur, con, ctx):
    cur.execute(
        """
        UPDATE salutations
        SET channel_id = ?
        """,
        (None,)
    ) 
    con.commit()
    con.close()
    await ctx.send(
        "I will no longer send salutations to the server."
        )
    print(
        "[COMMAND: $salchannel] Turned off feature for: "
        f"{ctx.guild.name}"
    )


async def update_message(con, ctx, column, message):
    con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
    con.execute(
        f"""
        UPDATE salutations
        SET {column} = ?
        """,
        (message.lstrip(),))
    con.commit()
    con.close()


class Salutations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="salutationcheck", aliases=["salcheck"])
    @commands.has_permissions(administrator=True)
    async def salutation_check(self, ctx):
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            cur = con.cursor()
            cur.execute("SELECT * FROM salutations")
            result = cur.fetchone()

            # Initialize a dictionary to store the fetched values
            salutations_data = {
                "channel_res": "None",
                "welcome_res": None,
                "welcome_dm_res": None,
                "welcome_msg": None,
                "welcome_dm_msg": None,
                "leave_res": None,
                "leave_dm_res": None,
                "leave_msg": None,
                "leave_dm_msg": None,
            }

            # Process the fetched result if not None
            if result is not None:
                salutations_data["channel_res"] = result[0]
                salutations_data["welcome_res"] = result[1]
                salutations_data["welcome_dm_res"] = result[2]
                salutations_data["welcome_msg"] = result[3]
                salutations_data["welcome_dm_msg"] = result[4]
                salutations_data["leave_res"] = result[5]
                salutations_data["leave_dm_res"] = result[6]
                salutations_data["leave_msg"] = result[7]
                salutations_data["leave_dm_msg"] = result[8]

            # Convert integer values to corresponding strings
            on_off_map = {0: "OFF", 1: "ON"}

            # Construct the response message using the dictionary
            response = (
                f"**Salutations channel:** " 
                f"{salutations_data['channel_res']}\n"
                f"**Welcome server messages:** " 
                f"{on_off_map.get(salutations_data['welcome_res'])}\n"
                f"**Welcome server message:**\n"
                f"{salutations_data['welcome_msg']}\n"
                f"**Welcome dm:** " 
                f"{on_off_map.get(salutations_data['welcome_dm_res'])}\n"
                f"**Welcome dm message:**\n"
                f"{salutations_data['welcome_dm_msg']}\n"
                f"**Leave server messages:** " 
                f"{on_off_map.get(salutations_data['leave_res'])}\n"
                f"**Leave server message:**\n"
                f"{salutations_data['leave_msg']}\n"
                f"**Leave dm:** " 
                f"{on_off_map.get(salutations_data['leave_dm_res'])}\n"
                f"**Leave dm message:**\n"
                f"{salutations_data['leave_dm_msg']}"
            )

            await ctx.send(response)
            print(f"[COMMAND: salutationcheck] Successfully executed in {ctx.guild.name}")
        except sqlite3.Error as e:
            if len(e.args) > 1:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: salutation check] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: salutation check] Error: {e}")
        finally:
            if con:
                con.close()



    @commands.command(name = "salchannel", aliases = ["schan", "salchan"])
    @commands.has_permissions(administrator = True)
    async def set_salutations_channel(self, ctx):
        guild = ctx.guild.id
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        cur = con.cursor()
        try:
            chan_check = await database_check(guild, "channel_id", "salutations")

            if chan_check != ctx.channel.id:
                await set_logs_channel(cur, con, ctx)
            elif chan_check == ctx.channel.id:
                await unset_logs_channel(cur, con, ctx)

        except sqlite3.Error as e:
            if len(e.args) > 1:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: set salutations channel] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")        
                print(f"[COMMAND ERROR: set salutations channel] Error: {e}")
        finally:
            if con:
                con.close()


    @commands.command(name = "welcome", aliases = ["wel", "welsvr"])
    @commands.has_permissions(administrator = True)
    async def server_welcome(self, ctx):
        guild = ctx.guild.id
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            salutations_chan = await database_check(guild, 'channel_id', 'salutations')
            welcome_toggle = await database_check(guild, 'welcome', 'salutations')
            welcome_msg = await database_check(guild, 'welcome_msg', 'salutations')

            if (salutations_chan is not None and
                welcome_toggle == 0):
                await toggle_on(ctx, 'welcome', 'salutations')
                await ctx.send(
                    "I will now send a message when someone joins the server!\n"
                    "Right now, the message is:\n"
                    f"'{welcome_msg}'\n"
                    "To change this, please use the $welcomemsg command."
                )
                print(
                    f"[COMMAND: $welcome] Successfully executed in: {ctx.guild.name}."
                )
            elif (salutations_chan is not None and
                  welcome_toggle == 1):
                await toggle_off(ctx, 'welcome', 'salutations')
                await ctx.send(
                    "I will no longer send a message when someone joins the server."
                )
                print(
                    f"[COMMAND: $welcome] Turned off feature for: {ctx.guild.name}."
                )
        except sqlite3.Error as e:
            if len(e.args) > 1:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: server welcome] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: server welcome] Error: {e}")
        finally:
            if con:
                con.close()


    @commands.command(name = "welcomedm", aliases = ["weldm", "wdm"])
    @commands.has_permissions(administrator = True)
    async def welcome_dm(self, ctx):
        guild = ctx.guild.id
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            welcome_dm_toggle = await database_check(guild, 'welcome_dm', 'salutations')
            welcome_dm_msg = await database_check(guild, 'welcome_dm_msg', 'salutations')

            if welcome_dm_toggle == 0:
                await toggle_on(ctx, 'welcome_dm', 'salutations')
                await ctx.send(
                    "I will now send a dm when someone joins the server!\n"
                    "For now, the default message is:\n"
                    f"'{welcome_dm_msg}'\n"
                    "To change this, please use the $welcomemsg command."
                )
                print(
                    f"[COMMAND: $welcome] Successfully executed in: {ctx.guild.name}."
                )
            elif welcome_dm_toggle == 1:
                await toggle_off(ctx, 'welcome_dm', 'salutations')
                await ctx.send(
                    "I will no longer send a dm when someone joins the server."
                )
                print(
                    f"[COMMAND: $welcome] Successfully turned off feature for: {ctx.guild.name}."
                )
        except sqlite3.Error as e:
            if len(e.args) > 1:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: welcome dm] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: welcome dm] Error: {e}")
        finally:
            if con:
                con.close()


    @commands.command(name = "welcomemsg", aliases = ["welmsg", "wmsg"])
    @commands.has_permissions(administrator = True)
    async def welcome_message(self, ctx, *message):
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            welcome_msg = ctx.message.content[len(ctx.invoked_with) + 1:]
            message = welcome_msg
            
            await update_message(con, ctx, "welcome_msg", message)
            await ctx.send("Welcome message set successfully!")
            print(
                "[COMMAND $welcomemsg] "
                f"Successfully set custom welcome message for: {ctx.guild.name}"
                )
        except sqlite3.Error as e:
            if len(e.args) > 1:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: welcome message] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: welcome message] Error: {e}")
        finally:
            if con:
                con.close()


    @commands.command(name = "welcomedmsg", aliases = ["weldmsg", "wdmsg"])
    @commands.has_permissions(administrator = True)
    async def welcome_dm_message(self, ctx, *message):
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            welcome_dm_msg = ctx.message.content[len(ctx.invoked_with) + 1:]
            message = welcome_dm_msg
            
            await update_message(con, ctx, "welcome_dm_msg", message)
            await ctx.send("Welcome dm message set successfully!")
            print(
                "[COMMAND: $welcomedmsg] "
                f"Successfully set custom welcome dm message for: {ctx.guild.name}"
                )
        except sqlite3.Error as e:
            if len(e.args) > 1:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: welcome dm message] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: welcome dm message] Error: {e}")
        finally:
            if con:
                con.close()


    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild.id
        ctx = member.guild
        # - For sql database connections.
        # - To make sure all connections are closed.
        con = sqlite3.connect(f"{db_path}/{ctx.id}.db")
        try:
            chan_id = await database_check(guild, 'channel_id', 'salutations')
            channel = ctx.get_channel(chan_id)
            welcome = await database_check(guild, 'welcome', 'salutations')
            welcome_msg = await database_check(guild, 'welcome_msg', 'salutations')
            welcome_dm = await database_check(guild, 'welcome_dm', 'salutations')
            welcome_dm_msg = await database_check(guild, 'welcome_dm_msg', 'salutations')

            replace_holders = {'/user/': member.mention,
                               '/server/': member.guild.name}

            if (channel is not None and
                welcome == 1):
                # - Replace /user/ and /server/ if found in welcome message.
                for key, value in replace_holders.items():
                    welcome_msg = welcome_msg.replace(key, value)
                # - Send replaced result.
                await channel.send(welcome_msg)
            
            replace_dm_holders = {'/user/': member.name,
                                  '/server/': member.guild.name}

            if (welcome_dm == 1):
                # - Replace /user/ and /server/ if found in welcome dm message.
                for key, value in replace_dm_holders.items():
                    welcome_dm_msg = welcome_dm_msg.replace(key, value)
                # - Send replaced result.
                await member.send(welcome_dm_msg)
        except sqlite3.Error as e:
            if len(e.args) > 1:
                print(f"[EVENT ERROR: on_member_join] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                print(f"[EVENT ERROR: on_member_join] Error: {e}")
        finally:
            if con:
                con.close()


    @commands.command(name = "leave", aliases = ["lsvr"])
    @commands.has_permissions(administrator = True)
    async def server_leave(self, ctx):
        guild = ctx.guild.id
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            salutations_chan = await database_check(guild, 'channel_id', 'salutations')
            leave_toggle = await database_check(guild, 'leave', 'salutations')
            leave_msg = await database_check(guild, 'leave_msg', 'salutations')

            if (salutations_chan is not None and
                leave_toggle == 0):
                await toggle_on(ctx, 'leave', 'salutations')
                await ctx.send(
                    "I will now send a message when someone leaves the server!\n"
                    "Right now, the message is:\n"
                    f"'{leave_msg}'\n"
                    "To change this, please use the $leavemsg command."
                )
                print(
                    f"[COMMAND: $leave] Successfully executed in: {ctx.guild.name}."
                )
            elif (salutations_chan is not None and
                  leave_toggle == 1):
                await toggle_off(ctx, 'leave', 'salutations')
                await ctx.send(
                    "I will no longer send a message when someone leaves the server."
                )
                print(
                    f"[COMMAND: $leave] Turned off feature for: {ctx.guild.name}."
                )
        except sqlite3.Error as e:
            if len(e.args) > 1:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: server leave] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: server leave] Error: {e}")
        finally:
            if con:
                con.close()


    @commands.command(name = "leavedm", aliases = ["ldm"])
    @commands.has_permissions(administrator = True)
    async def leave_dm(self, ctx):
        guild = ctx.guild.id
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            leave_dm_toggle = await database_check(guild, 'leave_dm', 'salutations')
            leave_dm_msg = await database_check(guild, 'leave_dm_msg', 'salutations')

            if leave_dm_toggle == 0:
                await toggle_on(ctx, 'leave_dm', 'salutations')
                await ctx.send(
                    "I will now send a dm when someone leaves the server!\n"
                    "Right now, the message is:\n"
                    f"'{leave_dm_msg}'\n"
                    "To change this, please use the $leavedmsg command."
                )
                print(
                    f"[COMMAND: $leavedm] Successfully executed in: {ctx.guild.name}."
                )
            elif leave_dm_toggle == 1:
                await toggle_off(ctx, 'leave_dm', 'salutations')
                await ctx.send(
                    "I will no longer send a message when someone leaves the server."
                )
                print(
                    f"[COMMAND: $leavedm] Turned off feature for: {ctx.guild.name}."
                )
        except sqlite3.Error as e:
            if len(e.args) > 1:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: leave dm] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: leave dm] Error: {e}")
        finally:
            if con:
                con.close()


    @commands.command(name = "leavemsg", aliases = ["lmsg"])
    @commands.has_permissions(administrator = True)
    async def leave_message(self, ctx, *message):
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            leave_msg = ctx.message.content[len(ctx.invoked_with) + 1:]
            message = leave_msg
            
            await update_message(con, ctx, "leave_msg", message)
            await ctx.send("Leave message set successfully!")
            print(
                "[COMMAND $leavemsg] "
                f"Successfully set custom leave message for: {ctx.guild.name}"
                )
        except sqlite3.Error as e:
            if len(e.args) > 1:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: leave message] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: leave message] Error: {e}")
        finally:
            if con:
                con.close()


    @commands.command(name = "leavedmsg", aliases = ["ldmsg"])
    @commands.has_permissions(administrator = True)
    async def leave_dm_message(self, ctx, *message):
        con = sqlite3.connect(f"{db_path}/{ctx.guild.id}.db")
        try:
            leave_dm_msg = ctx.message.content[len(ctx.invoked_with) + 1:]
            message = leave_dm_msg
            
            await update_message(con, ctx, "leave_dm_msg", message)
            await ctx.send("Leave dm message set successfully!")
            print(
                "[COMMAND: $leavedmsg] "
                f"Successfully set custom leave dm message for: {ctx.guild.name}"
                )
        except sqlite3.Error as e:
            if len(e.args) > 1:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: leave dm message] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                await ctx.send(
                    "I cannot execute the command. "
                    "Please check my terminal and logs!")
                print(f"[COMMAND ERROR: leave dm message] Error: {e}")
        finally:
            if con:
                con.close()


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild = member.guild.id
        ctx = member.guild
        # - For sql database connections.
        # - To make sure all connections are closed.
        con = sqlite3.connect(f"{db_path}/{ctx.id}.db")
        try:
            chan_id = await database_check(guild, 'channel_id', 'salutations')
            channel = ctx.get_channel(chan_id)
            leave = await database_check(guild, 'leave', 'salutations')
            leave_msg = await database_check(guild, 'leave_msg', 'salutations')
            leave_dm = await database_check(guild, 'leave_dm', 'salutations')
            leave_dm_msg = await database_check(guild, 'leave_dm_msg', 'salutations')

            replace_holders = {'/user/': member.mention,
                               '/server/': member.guild.name}

            if (channel is not None and
                leave == 1):
                # - Replace /user/ and /server/ if found in welcome message.
                for key, value in replace_holders.items():
                    leave_msg = leave_msg.replace(key, value)
                # - Send replaced result.
                await channel.send(leave_msg)
            
            replace_dm_holders = {'/user/': member.name,
                                  '/server/': member.guild.name}

            if (leave_dm == 1):
                # - Replace /user/ and /server/ if found in welcome dm message.
                for key, value in replace_dm_holders.items():
                    leave_dm_msg = leave_dm_msg.replace(key, value)
                # - Send replaced result.
                await member.send(leave_dm_msg)
        except sqlite3.Error as e:
            if len(e.args) > 1:
                print(f"[EVENT ERROR: on_member_remove] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                print(f"[EVENT ERROR: on_member_remove] Error: {e}")
        finally:
            if con:
                con.close()

async def setup(bot):
    await bot.add_cog(Salutations(bot))