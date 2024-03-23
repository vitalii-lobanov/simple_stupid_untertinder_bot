# app/main.py
from utils.debug import logger
import asyncio
from config import BOT_TOKEN, REDIS_URL

from database.engine import initialize_db
from routers.user_router import user_router
from bot import bot_instance
from dispatcher import dispatcher

logger.sync_debug("Bot token: {}".format(BOT_TOKEN))
logger.sync_debug("Redis URL: {}".format(REDIS_URL))

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
#TODO: check the starting number for the DB id's (0 or 1)
#TODO: save all the messages in the database. Use all the handlers. Add saving from logger and bot_service_message
#TODO: test reactions cancellation!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#TODO: global timer for a conversation
#TODO: profile versioning. Add profile_version field to the User, Message, Conversation, ProfileData models

#TODO: types for functions and arguments

