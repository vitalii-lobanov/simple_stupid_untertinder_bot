# app/routers/user_router.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from handlers.tg_commands import cmd_start

#from handlers.tg_commands import message_reaction_handler
from handlers.tg_user_unregister_handlers import cmd_unregister
from handlers.tg_commands import cmd_register
from handlers.tg_user_register_handlers import receiving_messages_on_registration_handler
from handlers.tg_user_unregister_handlers import cmd_hard_unregister

from handlers.tg_chatting_handlers import cmd_start_chatting #, state_user_is_ready_to_chat_handler

from aiogram import Dispatcher, types
from core.states import  RegistrationStates
from utils.debug import logger
# registration_handlers.py
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.filters import Command
from filters.custom_filters import InStateFilter
from core.telegram_messaging import send_tiered_parnter_s_message_to_user
from handlers.tg_chatting_handlers import state_user_is_in_chatting_progress_handler, stop_chatting_command_handler
from core.bot import bot_instance
from core.states import  UserStates, CommonStates
from aiogram.types import ReactionTypeEmoji
from handlers.tg_chatting_handlers import message_reaction_handler
from services.score_tiers import message_tiers_count
from handlers.tg_partner_change_handlers import next_please_handler
from services.dao import save_telegram_message
from models.base import MessageSource
from handlers.tg_commands import cmd_renew_profile


#bot_instance = None

# Custom filter for registration process

user_is_in_starting_registration_state_filter = InStateFilter(RegistrationStates.starting)
user_is_in_receiving_messages_during_registration_state_filter = InStateFilter(RegistrationStates.receiving_messages)
user_is_in_completed_registration_state_filter = InStateFilter(RegistrationStates.completed)
user_is_in_ready_for_chatting_state_filter = InStateFilter(UserStates.ready_to_chat)
user_is_in_chatting_in_progress_state_filter = InStateFilter(UserStates.chatting_in_progress)
user_is_in_not_ready_to_chat_state_filter = InStateFilter(UserStates.not_ready_to_chat)



user_router = Router()


@user_router.message(Command(commands=['unregister']))
async def cmd_user_unregister(message: types.Message, state: FSMContext):
    await save_telegram_message(message=message, message_source=MessageSource.command_received)
    await cmd_unregister(message, state)

#TODO: all the command handlers rename to cmd_*
#TODO: handle start command corrtectly
@user_router.message(Command(commands=['start']))
async def cmd_user_start(message: types.Message, state: FSMContext):
    await save_telegram_message(message=message, message_source=MessageSource.command_received)
    logger.sync_debug("'/start' command received")
    await cmd_start(message)



# @user_router.message(Command(commands=['hard_unregister']))
# async def cmd_user_hard_unregister(message: types.Message):
#     await save_telegram_message(message=message, message_source=MessageSource.command_received)
#     logger.sync_debug("'/hard_unregister' command received")
#     await cmd_hard_unregister(message)


# @user_router.message(Command(commands=['renew_profile']))
# async def cmd_user_renew_profile(message: types.Message, state: FSMContext):
#     await save_telegram_message(message=message, message_source=MessageSource.command_received)
#     logger.sync_debug("'/renew_profile' command received")
#     await cmd_renew_profile(message, state)

# The user starts a registration process
@user_router.message(Command(commands=['register']))
async def cmd_user_register_start(message: types.Message, state: FSMContext):
    await save_telegram_message(message=message, message_source=MessageSource.command_received)
    logger.sync_debug("'/register' command received")
    await cmd_register(message, state)


@user_router.message(Command(commands=['next_please']))
async def cmd_next_please(message: types.Message, state: FSMContext):
    await save_telegram_message(message=message, message_source=MessageSource.command_received)
    logger.sync_debug("'/next_please' command received")
    await next_please_handler(message, state)

@user_router.message(Command(commands=['show_my_profile']))
async def cmd_user_show_my_profile(message: types.Message):
    await save_telegram_message(message=message, message_source=MessageSource.command_received)
    logger.sync_debug("'/hard_unregister' command received")
    for i in range(0, message_tiers_count.MESSAGE_TIERS_COUNT):
        await send_tiered_parnter_s_message_to_user(bot_instance, message.from_user.id, i)


@user_router.message(Command(commands=['start_chatting']))
async def cmd_cmd_start_chatting(message: types.Message, state: FSMContext):    
    await save_telegram_message(message=message, message_source=MessageSource.command_received)
    logger.sync_debug("'/start_chatting' command received")
    await cmd_start_chatting(message, state)
    #await state.set_state(UserStates.ready_to_chat)


# The user sends message_tiers_count.MESSAGE_TIERS_COUNT messages to complete registration
@user_router.message(user_is_in_receiving_messages_during_registration_state_filter)
async def handle_user_receiving_messages_on_registration(message: types.Message, state: FSMContext):
    logger.sync_debug("Handler for receiving_messages state")
    await receiving_messages_on_registration_handler(message, state)


# Default handler for all other messages
@user_router.message_reaction()
async def message_user_reaction_handler(message_reaction: types.MessageReactionUpdated, state: FSMContext):
    logger.sync_debug("Message reaction handler...")
    #if state is UserStates.chatting_in_progress:
    await message_reaction_handler(message_reaction, state)


#The user is in a chatting state
@user_router.message(user_is_in_chatting_in_progress_state_filter)
async def state_user_is_in_chatting_progress(message: types.Message, state: FSMContext):
    logger.sync_debug("We're inside state_user_is_in_chatting_progress")
    await state_user_is_in_chatting_progress_handler(message, state)  
    









#TODO: REMOVE, testing artefacts ==========================

# @user_router.message(Command(commands=['stop_chatting']))
# async def cmd_user_stop_chatting(message: types.Message, state: FSMContext):
#     logger.sync_debug("'/stop_chatting' command received")
#     await state.set_state(UserStates.not_ready_to_chat)    
#     await stop_chatting_command_handler(message, state, True)

@user_router.message(Command(commands=['test']))
async def  test_delete_me(message: types.Message, state: FSMContext):
    await save_telegram_message(message=message, message_source=MessageSource.command_received)
    logger.sync_debug("'/test' command received")
    await state.set_state(CommonStates.test)

