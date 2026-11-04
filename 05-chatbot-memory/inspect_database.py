import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).with_name("chatbot.sqlite")

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()


# List tables

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
""")

print("Tables:")
for row in cursor.fetchall():
    print(row[0])


# Show checkpoints table schema

cursor.execute("""
    SELECT sql
    FROM sqlite_master
    WHERE type = 'table'
      AND name = 'checkpoints'
""")

print("\nCheckpoints schema:")
print(cursor.fetchone()[0])


# List checkpoints without binary data

cursor.execute("""
    SELECT
        thread_id,
        checkpoint_id,
        parent_checkpoint_id
    FROM checkpoints
    ORDER BY checkpoint_id
""")

print("\nCheckpoints:")
for row in cursor.fetchall():
    print(row)


connection.close()
