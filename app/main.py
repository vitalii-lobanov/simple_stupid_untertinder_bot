# app/main.py
from utils.debug import logger
import asyncio
from config import BOT_TOKEN, REDIS_URL

from database.engine import initialize_db
from routers.user_router import user_router
from core.bot import bot_instance
from core.dispatcher import  dispatcher

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
#TODO: save all the messages in the database. Use all the handlers. Add saving from logger and bot_service_message | ??    

#TODO: check the starting number for the DB id's (0 or 1)

#TODO: test reactions cancellation!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#TODO: global timer for a conversation
#TODO: profile versioning. Added profile_version field to the User, Message, Conversation, ProfileData models. Now: rewrite /register and /unregister
#TODO: client.py from redis_helper_utils -> utils
#TODO: check session.close() for all the open sessions
#TODO: types for functions and arguments
#TODO: edit command descriptions via BotFather

