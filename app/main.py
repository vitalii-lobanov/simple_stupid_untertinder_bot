# app/main.py
from utils.debug import logger
import asyncio
from aiogram import Bot, Dispatcher
from database.engine import SessionLocal
from config import BOT_TOKEN, REDIS_URL
from redis_helper_utils.client import get_redis_storage
from database.engine import initialize_db
from routers.user_router import user_router
from bot import bot_instance

logger.debug("Bot token: {}".format(BOT_TOKEN))
logger.debug("Redis URL: {}".format(REDIS_URL))

async def main():
    # Initialize bot and dispatcher
   
    storage = await get_redis_storage()
    dp = Dispatcher(storage=storage)

    # Initialize database
    initialize_db()

    # Include the router in the dispatcher
    dp.include_router(user_router)
    
    # Start the bot
    await dp.start_polling(bot_instance)


tet

if __name__ == '__main__':
    asyncio.run(main())
    
