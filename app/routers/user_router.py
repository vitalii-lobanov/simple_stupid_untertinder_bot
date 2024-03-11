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


from aiogram import Dispatcher, types
from states import RegistrationStates
from utils.debug import logger
# registration_handlers.py
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.filters import Command
from filters.custom_filters import InStateFilter

bot_instance = None

# Custom filter for registration process

user_is_in_starting_registration_state_filter = InStateFilter(RegistrationStates.starting)
user_is_in_receiving_messages_during_registration_state_filter = InStateFilter(RegistrationStates.receiving_messages)
user_is_in_completed_registration_state_filter = InStateFilter(RegistrationStates.completed)


def setup_router(bot):
    global bot_instance
    bot_instance = bot

user_router = Router()


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
