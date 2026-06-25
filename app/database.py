import aiosqlite


class DataBase:
    def __init__(self):
        self.conn = None

    async def connect_db(self):
        self.conn = await aiosqlite.connect("database.db")
        return self.conn

    async def close_db(self):
        await self.conn.commit()
        await self.conn.close()

    async def create_db(self) -> None:
        async with aiosqlite.connect("database.db") as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS groups (
    ID INTEGER PRIMARY KEY,
    chat_id TEXT NOT NULL,
    interval_minutes INTEGER NOT NULL,
    next_send_at INTEGER NOT NULL,
    name TEXT NOT NULL)""")
            await db.commit()

