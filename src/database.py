import sqlite3

db = sqlite3.connect("users.db")

cursor = db.cursor()


async def connect():
    await cursor.execute(
        """CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, incomes INTEGER NOT NULL, expenses INTEGER NOT NULL)"""
    )
    await db.commit()


async def get_items():
    await cursor.execute("""SELECT * FROM users""")
    print(cursor.fetchall())
    await db.commit()


db.close()
