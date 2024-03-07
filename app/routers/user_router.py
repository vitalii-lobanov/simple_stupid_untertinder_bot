# app/routers/user_router.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.handlers.tg_commands import handle_user_messages, add_user_to_database, get_user_status, update_user_status
from app.handlers.tg_commands import set_ready_to_chat, set_not_ready_to_chat, cmd_register_start, cmd_start
from app.handlers.tg_commands import cmd_unregister, message_reaction_handler, cmd_hard_unregister
from app.handlers.tg_commands import handle_receiving_messages_on_registration, cmd_register_start
from aiogram import Dispatcher, types
from app.states import RegistrationStates
from app.utils.debug import logger
# registration_handlers.py
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.filters import Command
from app.filters.custom_filters import InStateFilter

bot_instance = None

# Custom filter for registration process

user_is_in_starting_registration_state_filter = InStateFilter(RegistrationStates.starting)
user_is_in_receiving_messages_during_registration_state_filter = InStateFilter(RegistrationStates.receiving_messages)
user_is_in_completed_registration_state_filter = InStateFilter(RegistrationStates.completed)


def setup_router(bot):
    global bot_instance
    bot_instance = bot


user_router = Router()


# Handler for user to set status to ready to chat
@user_router.message(Command(commands=['ready']))
async def set_user_ready_to_chat(message: types.Message):
    await set_ready_to_chat(message)


# Handler for user to set status to not ready to chat
@user_router.message(Command(commands=['notready']))
async def set_user_not_ready_to_chat(message: types.Message):
    await set_not_ready_to_chat(message)


@user_router.message(Command(commands=['unregister']))
async def cmd_user_unregister(message: types.Message, state: FSMContext):
    await cmd_unregister(message)


# Handler for user to set status to ready to chat

@user_router.message(Command(commands=['start']))
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
    if (state is not RegistrationStates.receiving_messages) and (state is not RegistrationStates.starting):
        await cmd_register_start(message, state)


# The user sends 10 messages to complete registration
@user_router.message(user_is_in_receiving_messages_during_registration_state_filter)
async def handle_user_receiving_messages_on_registration(message: types.Message, state: FSMContext):
    logger.debug("Handler for receiving_messages state")
    await handle_receiving_messages_on_registration(message, state)


# Default handler for all other messages
@user_router.message_reaction()
async def message_user_reaction_handler(message_reaction: types.MessageReactionUpdated):
    logger.debug("Message reaction handler, all messages are handled here")
    await message_reaction_handler(message_reaction)
