from aiogram import Bot, Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from services.user_service import add_user_to_database, get_user_status, update_user_status
from aiogram import types
from core.states import  RegistrationStates
from models.user import User
from utils.debug import logger
from aiogram import types
from core.states import  CommonStates, UserStates
from aiogram.types import ReactionTypeEmoji
from models.base import MessageSource
from services.dao import save_telegram_message
from aiogram.fsm.context import FSMContext
from core.states import  RegistrationStates
from models.user import User
from aiogram import types
from core.states import  CommonStates
from utils.debug import logger
from models.message import Message
from models.base import MessageSource
from services.dao import save_telegram_message, save_tiered_registration_message
from services.score_tiers import message_tiers_count
from handlers.tg_user_register_handlers import ask_user_to_send_messages_to_fill_profile, create_new_registration, registration_failed
from handlers.tg_chatting_handlers import one_more_user_is_ready_to_chat
from services.dao import mark_user_as_inactive_in_db
from core.telegram_messaging import send_service_message
from core.bot import bot_instance
from utils.text_messages import message_user_has_been_unregistered, message_cannot_unregister_not_registered_user, message_user_has_already_been_hardly_unregistered
from utils.text_messages import message_non_registered_users_cannot_start_chatting
from services.dao import delete_user_profile_from_db, get_user_from_db, set_is_ready_to_chat_flag_for_user_in_db
from utils.text_messages import message_you_now_ready_to_chat_please_wait_the_partner_to_connect


#TODO: all the cmd_ functions from handlers should be here

async def cmd_start(message: types.Message, state: FSMContext):
    #await save_telegram_message(message=message, message_source=MessageSource.command_received)
    await state.set_state(CommonStates.default)
    await message.answer("Welcome! Use /register to sign up and /start_chatting to begin chatting with someone.")


async def cmd_unregister(message: types.Message):
    user_id = message.from_user.id
    if await mark_user_as_inactive_in_db(user_id):
        await send_service_message(bot_instance=bot_instance, message=message_user_has_been_unregistered(), chat_id=user_id)
    else:
        await send_service_message(bot_instance=bot_instance, message=message_cannot_unregister_not_registered_user(), chat_id=user_id)


async def cmd_hard_unregister(message: types.Message):
    user_id = message.from_user.id
    if await delete_user_profile_from_db(user_id):
        await send_service_message(bot_instance=bot_instance, message=message_user_has_already_been_hardly_unregistered(), chat_id=user_id)
    else:
        await send_service_message(bot_instance=bot_instance, message=message_cannot_unregister_not_registered_user(), chat_id=user_id)


async def cmd_register(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user_from_db(user_id)
    if user is None:
        await create_new_registration(message, state, user_id, (message.from_user.username or f"{message.from_user.first_name} {message.from_user.last_name}"))
    # elif user.is_active and profile_messages_count == message_tiers_count.MESSAGE_TIERS_COUNT:
    #     #profile_message_count requires versioning to work
    #     #TODO: implement versionong
    #     send_service_message(bot_instance=bot_instance, message=message_reactivation_user_profile_completed(), chat_id=user_id)
        
    # +

    #  # The user is active but doesn't have message_tiers_count.MESSAGE_TIERS_COUNT messages, proceed with message collection
    # await ask_user_to_send_messages_to_fill_profile(message, state)


async def cmd_start_chatting(message: types.Message, state: FSMContext):    
    user_id = message.from_user.id
    user = await get_user_from_db(user_id)
    if user is None:
        send_service_message(bot_instance=bot_instance, message=message_non_registered_users_cannot_start_chatting(), chat_id=user_id)
        return False
    else:
        if not await set_is_ready_to_chat_flag_for_user_in_db(user_id, True):
            raise RuntimeError(f"Failed to set is_ready_to_chat flag for user: {user_id}")
        else: 
            await send_service_message(bot_instance=bot_instance, message=message_you_now_ready_to_chat_please_wait_the_partner_to_connect(), chat_id=user_id)
            await one_more_user_is_ready_to_chat(user_id, state)

   
   