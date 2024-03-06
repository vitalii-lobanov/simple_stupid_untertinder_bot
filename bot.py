import asyncio
from aiogram import Bot, Dispatcher, Router
from config import BOT_TOKEN
from models import initialize_db
from handlers import  router
from storage import get_redis_storage


async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    storage = await get_redis_storage()
    dp = Dispatcher(storage=storage)

    # Initialize database
    initialize_db()

    # Include the router in the dispatcher
    dp.include_router(router)



    # Start the bot
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())