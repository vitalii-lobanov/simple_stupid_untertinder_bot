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
from states import CommonStates




async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(CommonStates.default)
    await message.answer("Welcome! Use /register to sign up and /start_chatting to begin chatting with someone.")


async def message_reaction_handler(message_reaction: types.MessageReactionUpdated):
    # TODO: store all the messages sent by bot in DB, check whether this message is in DB to determine the sender: user or bot
    try:
        #logger.debug("Emoji: ", message_reaction.new_reaction[0].emoji)
        pass
    except:
       # logger.debug("Emoji: ", message_reaction.new_reaction.emoji)
        pass