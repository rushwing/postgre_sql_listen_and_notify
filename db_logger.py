import asyncio
import asyncpg
import asyncpg_listen
from asyncpg_listen import ConnectFunc, NotificationOrTimeout, Timeout, NO_TIMEOUT
import logging
import json

class DbLogger:
    def __init__(self, db_config):
        self.conn = None
        self.db_config = db_config
        self.logger = None
        self.setup_logging()

    def setup_logging(self):
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("db_logger.log"),  # Log to file
                logging.StreamHandler()  # Log to terminal
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        if self.conn is None:
            self.conn = await asyncpg.connect(**self.db_config)
        return self.conn

    async def listen_notifications(self):
        conn_func: ConnectFunc = asyncpg_listen.connect_func(**self.db_config)
        listener = asyncpg_listen.NotificationListener(conn_func)
        # Set notification_timeout to NO_TIMEOUT for a long-running listener
        listener_task = asyncio.create_task(
            listener.run(
                {
                    "STATION_CREATED": self.on_station_created,
                    "STATION_UPDATED": self.on_station_updated,
                    "STATION_DELETED": self.on_station_deleted,
                },
                policy=asyncpg_listen.ListenPolicy.LAST,
                notification_timeout=NO_TIMEOUT  # No timeout
            )
        )

        self.logger.info("Listening for notifications...")
        return listener_task

    async def on_station_created(self, notification: NotificationOrTimeout) -> None:
        """Handle STATION_CREATED event."""
        if isinstance(notification, Timeout):
            self.logger.info(f"Received Station Created timeout: {notification}")
            return
        data = json.loads(notification.payload)
        print(f"Station Created: {data}")
        self.logger.info(f"Station Created: {data}")

    async def on_station_updated(self, notification: NotificationOrTimeout) -> None:
        """Handle STATION_UPDATED event."""
        if isinstance(notification, Timeout):
            self.logger.info(f"Received Station Updated timeout: {notification}")
            return
        data = json.loads(notification.payload)
        print(f"Station Updated: {data}")
        self.logger.info(f"Station Updated: {data}")

    async def on_station_deleted(self, notification: NotificationOrTimeout) -> None:
        """Handle STATION_DELETED event."""
        if isinstance(notification, Timeout):
            self.logger.info(f"Received Station Deleted timeout: {notification}")
            return
        data = json.loads(notification.payload)
        print(f"Station Deleted: {data}")
        self.logger.info(f"Station Deleted: {data}")


async def main():
    # Database configuration
    db_config = {
        "database": "test_stations",
        "user": "tsd_harbor",
        "password": "tst_harbor",
        "host": "localhost"
    }

    logger = DbLogger(db_config)
    listener_task = await logger.listen_notifications()

    # Keep the listener running indefinitely
    await listener_task


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program terminated by user.")
