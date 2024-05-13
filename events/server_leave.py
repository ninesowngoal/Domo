import os

def server_leave(bot):
    '''
    Called when Domo is removed from a server.
    Domo will delete the database made for that
    server.
    '''
    @bot.event
    async def on_guild_remove(guild):
        root_dir = os.path.realpath(
                os.path.join(os.path.dirname(__file__), '..')
                )
        db_path = os.path.join(root_dir, "sql")
        if os.path.exists(f"{db_path}/{guild.id}.db"):
            os.remove(f"{db_path}/{guild.id}.db")
        else:
            print(
                "[EVENT: SERVER LEAVE] "
                f"{guild.name} did not have a database to delete. "
                "There is an issue with the code."
                )