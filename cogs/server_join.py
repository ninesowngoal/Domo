import os
import sqlite3
import discord
from discord.ext import commands

class server_join(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        '''
        DMs the user who added the bot to the server.
        Gives a brief outline of main functions.

        Creates a database and tables for the server
        to be used for commands and events.
        '''
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
            inviter = entry.user
            ctx = self.context
            embed = discord.Embed(
                title = "Thank you for adding me to your server!")
            embed.set_thumbnail(url=ctx.me.display_avatar)
            embed.add_field(name="**Help commands**", value="""`$help` Lists all commands.
                            `$help [command name]` Gives info about a specific command.""")
            embed.set_footer(text="github link: https://github.com/ninesowngoal/DOMO")
            await inviter.send(embed=embed)

        try:
            # - Create server database.
            root_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(root_dir, "sql")
            os.makedirs(db_path, exist_ok=True)
            con = sqlite3.connect(f"{db_path}/{guild.id}.db")
            cur = con.cursor()
        
            tables = ['''CREATE TABLE IF NOT EXISTS experience (
                    member INTEGER PRIMARY KEY AUTOINCREMENT,
                    level INTEGER,
                    xp INTEGER
                    )''',
                    '''CREATE TABLE IF NOT EXISTS xp_roles (
                    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level INTEGER
                    )''',
                    '''CREATE TABLE IF NOT EXISTS xp_ping (
                    member INTEGER PRIMARY KEY AUTOINCREMENT,
                    ping INTEGER
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
                    '''CREATE TABLE IF NOT EXISTS welcome_leave (
                    welcome INTEGER PRIMARY KEY,
                    leave INTEGER
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
                    )'''
                  ]
        
            for table in tables:
                cur.execute(table)

            # - Input default value for the welcome/leave table.
            cur.execute("INSERT INTO welcome_leave (welcome, leave) VALUES (?, ?)",
                    (0, 0))

            con.commit()
            con.close()

            # - Input default values for bot logs.
            log_con = sqlite3.connect(f"{db_path}/toggles.db")
            log_cur = log_con.cursor()

            log_cur.execute("INSERT INTO logs (server_id, state) VALUES (?, ?)",
                        (guild.id, 0))
            log_con.commit()
            log_con.close()
            print(f"[EVENT: on_guild_join] Successfully set up database and tables for: {guild.id}")
        except sqlite3.error as e:
            print(f"[EVENT ERROR: on_guild_join] Error: {e}")
        finally:
            con.close()
            log_con.close()

async def setup(bot):
    await bot.add_cog(server_join(bot))