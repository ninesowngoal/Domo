import os
import sqlite3
import datetime
from definitions.path import root_dir

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
        db_file = os.path.join(root_dir, "events/experience/experience.db")
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

class MemberVoice:
    def __init__(self, member_id):
        self.member_id = member_id
        self.voice_join = None
        self.voice_leave = None

    def join_voice(self):
        self.voice_join = datetime.datetime.now()
    
    def leave_voice(self):
        self.voice_leave = datetime.datetime.now()
    
    def calculate_xp(self, xp_per_minute = 16.67):
        if self.voice_join is None or self.voice_leave is None:
            return 0 # - no xp earned if not joined or left.
        
        elapsed_time = (self.voice_leave - self.voice_join).total_seconds() / 60
        xp_earned = elapsed_time * xp_per_minute
        return xp_earned