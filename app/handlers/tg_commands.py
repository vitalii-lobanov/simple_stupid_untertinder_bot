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




    #TODO: logger.debud / logging.critical / logging.error — send errors to the user via message in DEBUG mode
    