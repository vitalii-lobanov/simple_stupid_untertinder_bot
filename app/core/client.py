from aiogram.fsm.storage.redis import RedisStorage
from aioredis import Redis
from config import REDIS_URL
from utils.debug import logger


async def get_redis_storage() -> RedisStorage:
    redis = Redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    storage = RedisStorage(redis)
    logger.sync_debug(f"Redis storage created: {storage}")
    return storage
