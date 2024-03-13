from aiogram import Bot, Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from services.user_service import add_user_to_database, get_user_status, update_user_status
from aiogram import types
from database.engine import SessionLocal
from states import RegistrationStates
from models.user import User
from utils.debug import logger
from aiogram import types
from states import CommonStates, UserStates
from aiogram.types import ReactionTypeEmoji



async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(CommonStates.default)
    await message.answer("Welcome! Use /register to sign up and /start_chatting to begin chatting with someone.")


async def message_reaction_handler(message_reaction: types.MessageReactionUpdated):
    # TODO: store all the messages sent by bot in DB, check whether this message is in DB to determine the sender: user or bot
    try:
        logger.debug("We're inside message_reaction_handler function.")
        #expected_emoji_reaction = ReactionTypeEmoji(emoji='❤').emoji
        expected_emoji_reaction = ReactionTypeEmoji(emoji='🔥').emoji
        logger.debug("Expected emoji reaction: " + str(expected_emoji_reaction))
        actual_emoji_reaction = message_reaction.new_reaction[0].emoji
        logger.debug("Actual emoji reaction: " + str(actual_emoji_reaction))

        if actual_emoji_reaction == expected_emoji_reaction:
            logger.debug("Test heart emoji detected.")
            
        pass
    except Exception as e:
        logger.debug("An exception occurred while handling the message reaction: " + str(e))
        pass

    #TODO: logger.debud / logging.critical / logging.error — send errors to the user via message in DEBUG mode
    