from aiogram.fsm.storage.redis import RedisStorage
from aioredis import Redis
from app.utils.debug import logger
from app.config import REDIS_URL



async def get_redis_storage() -> RedisStorage:
    redis = Redis.from_url(REDIS_URL, encoding='utf-8', decode_responses=True)
    storage = RedisStorage(redis)
    return storage
