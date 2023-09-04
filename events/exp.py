import os
import sqlite3

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
        absolute_path = os.path.dirname(__file__)
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

# - Function to load data from the database into the dictionary on bot startup
def load_data_from_database():
    absolute_path = os.path.dirname(__file__)
    db_file = os.path.join(absolute_path, "experience.db")
    db_con = sqlite3.connect(db_file)
    cur = db_con.cursor()

    # - Fetch data from the database and update the member_exp_dict
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

# Load data from the database when the bot starts
load_data_from_database()

def member_exp(bot):
    '''
    Gives members of a server 50xp per message. Ignores it if its
    from a bot. Sends a message when a user has levelled up.
    '''
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        member_id = message.author.id
        channel = bot.get_channel(YOUR_CHANNEL_ID_HERE) # - Can delete if you want.
        ctx = await bot.get_context(message)

        # - Gets or creates a MemberExp instance for the member
        member_exp = member_exp_dict.get(member_id)
        if member_exp is None:
            member_exp = MemberExp(member_id)
            member_exp_dict[member_id] = member_exp

        # - Stores the previous level before gaining XP
        previous_level = member_exp.level

        # - Gain XP for the message and saves to the database
        member_exp.gain_xp(50)  # - 50 XP per message
        member_exp_db.save_member_exp(member_id, member_exp.level, member_exp.curr_xp)

        # - Check if the member has leveled up
        if member_exp.level > previous_level:
            await channel.send(f"{message.author} has levelled up to level {member_exp.level}!")
            # - Delete above line if you deleted the channel variable.
            await ctx.send(f"<@{message.author.id}> has levelled up to level {member_exp.level}!")
