from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import StorageKey
from core.bot import bot_instance
from core.dispatcher import dispatcher
from typing import Union


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
    chatting_in_progress = State()
    wants_to_end_chatting = State()


async def access_user_context(chat_id: int, user_id: int, bot_id: int):
    user_context = FSMContext(
        dispatcher.storage,
        StorageKey(chat_id=chat_id, user_id=user_id, bot_id=bot_id),
    )
    return user_context


async def initialize_states_for_chatter_to_start_conversation(
    state: FSMContext,
) -> None:
    await state.set_state(UserStates.chatting_in_progress)
    await state.update_data(current_score=0)
    await state.update_data(message_count=0)
    await state.update_data(disclosure_level=-1)


async def get_user_context(user_id: int) -> FSMContext:
    user_context = FSMContext(
        dispatcher.storage,
        StorageKey(chat_id=user_id, user_id=user_id, bot_id=bot_instance.id),
    )

    return user_context


async def check_user_state(user_id:int = -1, state: Union[RegistrationStates, UserStates, CommonStates] = None) -> bool:
    if user_id == -1:
        raise ValueError("User id must be provided")
    if state is None:
        raise ValueError("State must be provided")
    user_context = await get_user_context(user_id)
    if await user_context.get_state() == state:
        return True
    else:
        return False