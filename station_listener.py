import asyncio
from db_listener import DatabaseListener


class StationListener(DatabaseListener):
    def __init__(self, pool, handlers):
        self.pool = pool
        self.handlers = handlers

    async def notify_listener(self, connection, channel, payload):
        if channel in self.handlers:
            await self.handlers[channel].handle(payload)

    async def listen(self):
        async with self.pool.acquire() as connection:
            for channel in self.handlers.keys():
                await connection.add_listener(channel, self.notify_listener)

            while True:
                await asyncio.sleep(1)  # Prevent busy waiting
