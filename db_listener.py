from abc import ABC, abstractmethod


class DatabaseListener(ABC):
    @abstractmethod
    async def listen(self):
        pass
