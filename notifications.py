import asyncpg
import asyncio
from fastapi import FastAPI


class PostgresNotify:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.db_url)

    async def listen(self, channel: str):
        async with self.pool.acquire() as connection:
            await connection.add_listener(channel, self.notify_listener)

    async def notify_listener(self, connection, channel, payload):
        print(f"Received notification on channel {channel}: {payload}")

    async def send_notification(self, channel: str, payload: str):
        async with self.pool.acquire() as connection:
            await connection.execute(f"NOTIFY {channel}, '{payload}'")

    async def close(self):
        await self.pool.close()
