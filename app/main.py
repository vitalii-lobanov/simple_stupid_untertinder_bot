# app/main.py
import asyncio
from aiogram import Bot, Dispatcher
from app.database.engine import SessionLocal
from app.config import BOT_TOKEN, REDIS_URL
from app.redis.client import get_redis_storage
from app.database.engine import initialize_db
from app.routers.user_router import user_router


async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    storage = await get_redis_storage()
    dp = Dispatcher(storage=storage)

    # Initialize database
    initialize_db()

    # Include the router in the dispatcher
    dp.include_router(user_router)

    # Start the bot
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
