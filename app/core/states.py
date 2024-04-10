from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import StorageKey
from core.bot import bot_instance
from core.dispatcher import dispatcher
from typing import Union
from utils.d_debug import d_logger


class RegistrationStates(StatesGroup):
    starting = State()
    receiving_messages = State()
    completed = State()


class CommonStates(StatesGroup):
    test = State()
    just_started_bot = State()


class UserStates(StatesGroup):
    not_ready_to_chat = State()
    ready_to_chat = State()
    chatting_in_progress = State()
    wants_to_end_chatting = State()


async def access_user_context(chat_id: int, user_id: int, bot_id: int):
    d_logger.debug("D_logger")
    user_context = FSMContext(
        dispatcher.storage,
        StorageKey(chat_id=chat_id, user_id=user_id, bot_id=bot_id),
    )
    return user_context


async def initialize_states_for_chatter_to_start_conversation(
    state: FSMContext,
) -> None:
    d_logger.debug("D_logger")
    await state.set_state(UserStates.chatting_in_progress)
    await state.update_data(current_score=0)
    await state.update_data(message_count=0)
    await state.update_data(disclosure_level=-1)


async def get_user_context(user_id: int) -> FSMContext:
    d_logger.debug("D_logger")
    user_context = FSMContext(
        dispatcher.storage,
        StorageKey(chat_id=user_id, user_id=user_id, bot_id=bot_instance.id),
    )

    return user_context


async def check_user_state(
    user_id: int = -1, state: Union[RegistrationStates, UserStates, CommonStates] = None
) -> bool:
    d_logger.debug("D_logger")
    if user_id == -1:
        raise ValueError("User id must be provided")
    if state is None:
        return False
    user_context = await get_user_context(user_id)
    if await user_context.get_state() == state:
        return True
    else:
        return False


async def is_current_state_legitimate(
    user_id: int,
    state: FSMContext,
    allowed_states: list[Union[RegistrationStates, UserStates, CommonStates]],
) -> bool:
    d_logger.debug("D_logger")
    for state in allowed_states:
        if state is None:
            return True
        if await check_user_state(user_id=user_id, state=state):
            return True
    return False


async def is_current_state_is_not_allowed(
    user_id: int,
    state: FSMContext,
    not_allowed_states: list[Union[RegistrationStates, UserStates, CommonStates]],
) -> bool:
    d_logger.debug("D_logger")
    for state in not_allowed_states:
        if await check_user_state(user_id=user_id, state=state):
            return True
    return False


start_cmd_allowed_states = [None]
regitser_cmd_allowed_states = [
    RegistrationStates.starting,
    CommonStates.just_started_bot,
    RegistrationStates.completed,
]
unregister_cmd_allowed_states = [
    RegistrationStates.completed,
    UserStates.not_ready_to_chat,
]
show_my_profile_cmd_allowed_states = [
        UserStates.chatting_in_progress,
        UserStates.ready_to_chat,
        UserStates.not_ready_to_chat,
        RegistrationStates.completed,
    ]


start_chatting_cmd_allowed_states = [
    RegistrationStates.completed,
    UserStates.not_ready_to_chat,
]
next_please_cmd_allowed_states = [UserStates.chatting_in_progress]

help_cmd_allowed_states = [
    RegistrationStates.starting,
    RegistrationStates.receiving_messages,
    RegistrationStates.completed,
    CommonStates.test,
    CommonStates.just_started_bot,
    UserStates.not_ready_to_chat,
    UserStates.ready_to_chat,
    UserStates.chatting_in_progress,
    UserStates.wants_to_end_chatting,
    None,
]

chatting_process_message_receiving_allowed_states = [
    UserStates.chatting_in_progress,        
    UserStates.wants_to_end_chatting,    
]

receiving_registration_profile_messages_allowed_states = [    
    RegistrationStates.receiving_messages,
    RegistrationStates.starting,   
]


all_states = [
    RegistrationStates.starting,
    RegistrationStates.receiving_messages,
    RegistrationStates.completed,
    CommonStates.test,
    CommonStates.just_started_bot,
    UserStates.not_ready_to_chat,
    UserStates.ready_to_chat,
    UserStates.chatting_in_progress,
    UserStates.wants_to_end_chatting,
]


# class RegistrationStates(StatesGroup):
#     starting = State()
#     receiving_messages = State()
#     completed = State()


# class CommonStates(StatesGroup):
#     default = State()  # The default state for general bot interactions
#     test = State()
#     just_started_bot = State()


# class UserStates(StatesGroup):
#     not_ready_to_chat = State()
#     ready_to_chat = State()
#     chatting_in_progress = State()
#     wants_to_end_chatting = State()
