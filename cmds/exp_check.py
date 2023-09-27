import os
import sqlite3

absolute_path = os.path.dirname(__file__)
db_file = os.path.join(absolute_path, "experience.db")
db_connection = sqlite3.connect(db_file)
cur = db_connection.cursor()
cursor = db_connection.execute("SELECT level, xp FROM experience WHERE member = ?")
result = cursor.fetchone()
print(result)