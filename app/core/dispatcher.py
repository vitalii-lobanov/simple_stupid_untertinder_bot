from core.bot import bot_instance
from aiogram import Dispatcher
from redis_helper_utils.client import get_redis_storage
import asyncio

storage =  asyncio.run(get_redis_storage())
dispatcher = Dispatcher(storage=storage)

