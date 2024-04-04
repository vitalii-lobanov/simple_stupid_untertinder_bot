# app/main.py
import asyncio

from config import BOT_TOKEN, REDIS_URL
from core.bot import bot_instance
from core.dispatcher import dispatcher
from database.engine import initialize_db
from routers.user_router import user_router
from utils.debug import logger


logger.sync_debug("Bot token: {}".format(BOT_TOKEN))
logger.sync_debug("Redis URL: {}".format(REDIS_URL))


async def main():
    # Initialize database
    await initialize_db()
    logger.sync_debug('Database initialized successfully.')

    # Include the router in the dispatcher
    dispatcher.include_router(user_router)

    # Start the bot
    logger.sync_debug('Initializing complete.')
    await dispatcher.start_polling(bot_instance)

if __name__ == "__main__":
    asyncio.run(main())





# TODO: look TODO's
# TODO: message not found (like handler)     

# TODO: Profile version is null
# TODO: check reactiuons for the multimedia messages
# Try Trunk Check extension instead of ruff
# TODO: change info message for messages before /start command
# TODO: end time for the conversation in the DB
# TODO: -> and argument types for functions
# TODO: looak at all the .get_state() and change them to check_user_state() from core.states
# TODO: save all the messages in the database. Use all the handlers. Add saving from logger and bot_service_message | ??
# TODO: states: default and not_ready_to_chat — choose one of them
# TODO: handle is_ready_to_chat status for the users in the database according to states changes
# TODO: check the starting number for the DB id's (0 or 1)

# TODO: test reactions cancellation!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO: global timer for a conversation
# TODO: profile versioning. Added profile_version field to the User, Message, Conversation, ProfileData models. Now: rewrite /register and /unregister
# TODO: client.py from redis_helper_utils -> utils
# TODO: check session.close() for all the open sessions
# TODO: types for functions and arguments
# TODO: edit command descriptions via BotFather/sta
# TODO: states chaeching in user_router before command handling
# TODO: test: condition — not registered user sends a message. 
# TODO: json / list serializers from dao.py to helpers module
# TODO: handle forwarded messages in registration process
# TODO: handle forwarded messages in conversations
# TODO: racing conditions: when user runs start_chatting, the user's is_ready_to_chat flag is set to True, the other user could start the conversation and get a new partner, while she really already in another conversation