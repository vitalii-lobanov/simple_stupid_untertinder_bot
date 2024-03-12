
from aiogram.fsm.context import FSMContext
from database.engine import SessionLocal
from states import RegistrationStates
from models.user import User
from aiogram import types
from states import CommonStates, UserStates
from utils.debug import logger
from models import ProfileDataTieredMessage
from tasks import celery_app

async def start_chatting(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.ready_to_chat)
    await message.answer("You are now ready to chat with someone.")