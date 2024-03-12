# app/routers/user_router.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from handlers.tg_commands import cmd_start

from handlers.tg_commands import message_reaction_handler
from handlers.tg_user_unregister_handlers import cmd_unregister
from handlers.tg_user_register_handlers import start_registration_handler
from handlers.tg_user_register_handlers import receiving_messages_on_registration_handler
from handlers.tg_user_unregister_handlers import cmd_hard_unregister

from handlers.tg_chatting_handlers import user_start_chatting, state_user_is_ready_to_chat_handler

from aiogram import Dispatcher, types
from states import RegistrationStates
from utils.debug import logger
# registration_handlers.py
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.filters import Command
from filters.custom_filters import InStateFilter
from handlers.tg_user_staging import send_tiered_message_to_user
from handlers.tg_chatting_handlers import state_user_is_in_chatting_progress_handler

from states import UserStates

bot_instance = None

# Custom filter for registration process

user_is_in_starting_registration_state_filter = InStateFilter(RegistrationStates.starting)
user_is_in_receiving_messages_during_registration_state_filter = InStateFilter(RegistrationStates.receiving_messages)
user_is_in_completed_registration_state_filter = InStateFilter(RegistrationStates.completed)
user_is_in_ready_for_chatting_state_filter = InStateFilter(UserStates.ready_to_chat)
user_is_in_chatting_in_progress_state_filter = InStateFilter(UserStates.chatting_in_progress)

def setup_router(bot):
    global bot_instance
    bot_instance = bot

user_router = Router()


@user_router.message(Command(commands=['unregister']))
async def cmd_user_unregister(message: types.Message, state: FSMContext):
    await cmd_unregister(message)

@user_router.message(Command(commands=['restart']))
async def cmd_user_start(message: types.Message):
    logger.debug("'/start' command received")
    await cmd_start(message)


@user_router.message(Command(commands=['hard_unregister']))
async def cmd_user_hard_unregister(message: types.Message):
    logger.debug("'/hard_unregister' command received")
    await cmd_hard_unregister(message)


# The user starts a registration process
@user_router.message(Command(commands=['register']))
async def cmd_user_register_start(message: types.Message, state: FSMContext):
    # check whether the user is not in a registration process
    logger.debug("'/register' command received")
    await start_registration_handler(message, state)


# The user sends 10 messages to complete registration
@user_router.message(user_is_in_receiving_messages_during_registration_state_filter)
async def handle_user_receiving_messages_on_registration(message: types.Message, state: FSMContext):
    logger.debug("Handler for receiving_messages state")
    await receiving_messages_on_registration_handler(message, state)


# Default handler for all other messages
@user_router.message_reaction()
async def message_user_reaction_handler(message_reaction: types.MessageReactionUpdated):
    logger.debug("Message reaction handler, all messages are handled here")
    await message_reaction_handler(message_reaction)

@user_router.message(Command(commands=['show_my_profile']))
async def cmd_user_show_my_profile(message: types.Message):
    logger.debug("'/hard_unregister' command received")
    for i in range(0, 9):
        await send_tiered_message_to_user(bot_instance, message.from_user.id, i)


@user_router.message(Command(commands=['start_chatting']))
async def cmd_user_start_chatting(message: types.Message, state: FSMContext):    
    await user_start_chatting(message, state)
    await state.set_state(UserStates.ready_to_chat)

#The user send '/start_chatting' command
@user_router.message(user_is_in_ready_for_chatting_state_filter)
async def state_user_is_ready_to_chat(message: types.Message, state: FSMContext):
    await state_user_is_ready_to_chat_handler(message, state)
    

#The user is in a chatting state
@user_router.message(user_is_in_chatting_in_progress_state_filter)
async def state_user_is_in_chatting_progress(message: types.Message, state: FSMContext):
    await state_user_is_in_chatting_progress_handler(message, state)  
    