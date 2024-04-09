# app/main.py
import asyncio

from config import BOT_TOKEN, REDIS_URL
from core.bot import bot_instance
from core.dispatcher import dispatcher
from database.engine import initialize_db
from routers.user_router import user_router
from utils.debug import logger
from utils.d_debug import d_logger, d_logger


logger.sync_debug("Bot token: {}".format(BOT_TOKEN))
logger.sync_debug("Redis URL: {}".format(REDIS_URL))


async def main():
    # Initialize database
    await initialize_db()
    logger.sync_debug('Database initialized successfully.')

    # Include the router in the dispatcher
    dispatcher.include_router(user_router)

    d_logger.debug("D_logger")

    # Start the bot
    logger.sync_debug('Initializing complete.')
    await dispatcher.start_polling(bot_instance)



if __name__ == "__main__":
    asyncio.run(main())





# TODO: look TODO's


# TODO: -> and argument types for functions

# TODO: save all the messages in the database. Use all the handlers. Add saving from logger and bot_service_message | ??
# TODO: states: default and not_ready_to_chat — choose one of them
# TODO: handle is_ready_to_chat status for the users in the database according to states changes
# TODO: check the starting number for the DB id's (0 or 1)

# TODO: test reactions cancellation!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# TODO: profile versioning. Added profile_version field to the User, Message, Conversation, ProfileData models. Now: rewrite /register and /unregister
# TODO: client.py from redis_helper_utils -> utils
# TODO: check session.close() for all the open sessions
# TODO: types for functions and arguments

# Try Trunk Check extension instead of ruff
