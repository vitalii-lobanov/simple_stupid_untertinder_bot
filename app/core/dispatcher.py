import asyncio

from aiogram import Dispatcher

from core.client import get_redis_storage

storage = asyncio.run(get_redis_storage())
dispatcher = Dispatcher(storage=storage)
