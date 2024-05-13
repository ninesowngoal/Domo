import os
import sqlite3
import discord

def server_join(bot):
    '''
    Called when Domo joins a server.\n
    Domo will do two things:\n
    First, Domo will thank the user and send
    them info about using the help command to
    see what she can do. Will also link the
    github.\n
    Second, Domo will create a database for
    the server. Essential for the commands
    and events to work.
    '''
    @bot.event
    async def on_guild_join(guild):
        '''
        DMs the user who added the bot to the server.
        Gives a brief outline of main functions.

        Creates a database and tables for the server
        to be used for commands and events.
        '''
        async for entry in guild.audit_logs(
            limit=1, action=discord.AuditLogAction.bot_add):
            inviter = entry.user
            embed = discord.Embed(
            title = "Thank you for adding me to your server!")
            embed.set_thumbnail(
                url="https://i.imgur.com/zToL9Jh.png"
                )
            embed.add_field(
                name="**Help commands**", 
                value="""`.h` Lists all commands.
                `.hcmd [command name]` Gives info about a specific command."""
                )
            embed.set_footer(
                text="github link: https://github.com/ninesowngoal/DOMO"
                )
        await inviter.send(embed=embed)

        try:
            # - Create server database.
            root_dir = os.path.realpath(
                os.path.join(os.path.dirname(__file__), '..')
                )
            db_path = os.path.join(root_dir, "sql")
            os.makedirs(db_path, exist_ok=True)
            con = sqlite3.connect(f"{db_path}/{guild.id}.db")
            cur = con.cursor()
        
            tables = ['''CREATE TABLE IF NOT EXISTS experience (
                    member INTEGER PRIMARY KEY AUTOINCREMENT,
                    level INTEGER,
                    xp INTEGER,
                    ping INTEGER
                    )''',
                    '''
                    CREATE TABLE IF NOT EXISTS xp_settings (
                    voicechan INTEGER PRIMARY KEY AUTOINCREMENT,
                    textchan INTEGER,
                    voicexp INTEGER,
                    textxp INTEGER
                    )''',
                    '''CREATE TABLE IF NOT EXISTS xp_roles (
                    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level INTEGER
                    )''',
                    '''CREATE TABLE IF NOT EXISTS kick (
                    member INTEGER PRIMARY KEY AUTOINCREMENT,
                    date INTEGER,
                    reason TEXT
                    )''',
                    '''CREATE TABLE IF NOT EXISTS ban (
                    member INTEGER PRIMARY KEY AUTOINCREMENT,
                    date INTEGER,
                    reason TEXT
                    )''',
                    '''CREATE TABLE IF NOT EXISTS auto_assign_role (
                    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    toggle INTEGER
                    )''',
                    '''CREATE TABLE IF NOT EXISTS role_on_react (
                    channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER,
                    emoji_id INTEGER,
                    role_id INTEGER
                    )''',
                    '''
                    CREATE TABLE IF NOT EXISTS logs (
                    channel_id INTEGER NULL,
                    voice INTEGER,
                    xp INTEGER,
                    roles_given INTEGER,
                    del_msgs INTEGER
                    )''',
                    '''
                    CREATE TABLE IF NOT EXISTS salutations (
                    channel_id INTEGER NULL,
                    welcome INTEGER,
                    welcome_dm INTEGER,
                    welcome_msg TEXT,
                    welcome_dm_msg TEXT,
                    leave INTEGER,
                    leave_dm INTEGER,
                    leave_msg TEXT,
                    leave_dm_msg TEXT
                    )'''
                  ]
        
            for table in tables:
                cur.execute(table)

            # - Input default values for exp tracking.
            cur.execute(
                "INSERT INTO xp_settings (voicexp, textxp) VALUES (?, ?)",
                (16.67, 50)
            )
            con.commit()

            # - Input default value for the salutations table.
            cur.execute(
                """INSERT INTO salutations (
                    channel_id,
                    welcome,
                    welcome_dm,
                    welcome_msg,
                    welcome_dm_msg,
                    leave,
                    leave_dm,
                    leave_msg,
                    leave_dm_msg
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                (
                 None,
                 0,
                 0,
                 "Welcome /user/!",
                 "Welcome to /server/, /user/!",
                 0,
                 0,
                 "Goodbye /user/!",
                 "I hope you enjoyed your stay in /server/, /user/!"
                 )
                )
            con.commit()

            # - Input default values for bot logs.
            cur.execute(
                '''INSERT INTO logs (
                    channel_id,
                    voice,
                    xp,
                    roles_given,
                    del_msgs
                    ) VALUES (?, ?, ?, ?, ?)''',
                (None, 0, 0, 0, 0)
                )
            con.commit()

            print(
                "[EVENT: on_guild_join] " 
                f"Successfully set up database and tables for: {guild.name}"
                )
        except sqlite3.Error as e:
            if len(e.args) > 1:
                print(f"[EVENT ERROR: on_guild_join] Error: {e}"
                    f"Error code: {e.args[0]}"
                    f"Error message: {e.args[1]}")
            else:
                print(f"[EVENT ERROR: on_guild_join] Error: {e}")
        finally:
            if con:
                con.close()