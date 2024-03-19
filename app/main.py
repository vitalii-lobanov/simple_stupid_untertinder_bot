# app/main.py
from utils.debug import logger
import asyncio
from config import BOT_TOKEN, REDIS_URL

from database.engine import initialize_db
from routers.user_router import user_router
from bot import bot_instance
from dispatcher import dispatcher

logger.debug("Bot token: {}".format(BOT_TOKEN))
logger.debug("Redis URL: {}".format(REDIS_URL))

async def main():
    # Initialize database
    initialize_db()

    # Include the router in the dispatcher
    dispatcher.include_router(user_router)
    
    # Start the bot
    await dispatcher.start_polling(bot_instance)

if __name__ == '__main__':
    asyncio.run(main())

#TODO: look TODO's
#TODO: test reactions cancellation!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!