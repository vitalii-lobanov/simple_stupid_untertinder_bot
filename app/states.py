# states.py
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
# from app.tasks.tasks import celery_app
from dispatcher import dispatcher

class RegistrationStates(StatesGroup):
    starting = State()
    receiving_messages = State()
    completed = State()

class CommonStates(StatesGroup):
    default = State()  # The default state for general bot interactions
    test = State()

class UserStates(StatesGroup):
    not_ready_to_chat = State()
    ready_to_chat = State()
    chatting_in_progress= State()
    wants_to_end_chatting = State()

async def access_user_context(chat_id: int, user_id: int, bot_id: int):
        user_context = FSMContext(
        dispatcher.storage,
        StorageKey(
            chat_id=chat_id, user_id=user_id, bot_id=bot_id
        ),
            )
        return user_context