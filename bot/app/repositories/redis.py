import os
import redis.asyncio as redis
from datetime import datetime


class RedisRepository:
    CONNECTION_URL = os.getenv("REDIS_URL", "redis://localhost?decode_responses=true")

    def __init__(self):
        self.connection = redis.Redis.from_url(self.CONNECTION_URL, decode_responses=True)

    async def add_mailing_user_ids(self, mailing_id: int, *user_ids: int):
        async with self.connection.pipeline(transaction=True) as pipe:
            add_time = datetime.now().isoformat()
            for user_id in user_ids:
                key = f"{mailing_id}:{user_id}"
                pipe.set(key, add_time)
            pipe.set(str(mailing_id), str(user_ids[-1]))
            await pipe.execute()

    async def save(self):
        await self.connection.bgsave()

    async def get_mailing_user_ids(self, mailing_id: int) -> list[int]:
        user_ids = []
        async for key in self.connection.scan_iter(f"{mailing_id}:*"):
            user_ids.append(int(key.split(":")[1]))
        return list(sorted(user_ids))

    async def get_mailing_last_user_id(self, mailing_id: int) -> int | None:
        value = await self.connection.get(str(mailing_id))
        return None if value is None else int(value)

    async def set_mailing_status(self, mailing_id: int, status: str):
        await self.connection.set(f"status:{mailing_id}", status)

    async def get_mailing_status(self, mailing_id: int) -> str | None:
        return await self.connection.get(f"status:{mailing_id}")

    async def delete_mailing(self, mailing_id: int):
        async with self.connection.pipeline(transaction=True) as pipe:
            async for key in self.connection.scan_iter(f"{mailing_id}:*"):
                pipe.delete(key)
            await pipe.execute()

    async def close(self):
        await self.connection.close()

    async def list_mailings_statuses(self) -> dict[int, str]:
        mailings = {}
        async for key in self.connection.scan_iter("status:*"):
            status = await self.connection.get(key)
            mailings[int(key.split(":")[1])] = status
        return mailings

