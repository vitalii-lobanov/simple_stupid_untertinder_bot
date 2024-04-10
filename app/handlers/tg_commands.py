from aiogram import types
from aiogram.fsm.context import FSMContext
from core.states import CommonStates, UserStates
from core.telegram_messaging import send_service_message
from handlers.tg_chatting_handlers import one_more_user_is_ready_to_chat
from handlers.tg_user_register_handlers import (
    ask_user_to_send_messages_to_fill_profile,
    create_new_registration,
)
from services.dao import (
    get_user_from_db,
    set_is_active_flag_for_user_in_db,
    mark_user_as_inactive_in_db,
    set_is_ready_to_chat_flag_for_user_in_db,
    get_user_is_active_status_from_db,
    get_max_profile_version_of_user_from_db,
    set_user_profile_version_in_db,
)
from utils.text_messages import (
    message_cannot_unregister_not_registered_user,
    message_cmd_start_welcome_message,
    message_non_registered_users_cannot_start_chatting,
    message_user_has_been_unregistered,
    message_you_are_not_in_default_state_and_cannot_register,
    message_you_cannot_unregister_now,
    message_you_have_been_registered_successfully,
    message_you_now_ready_to_chat_please_wait_the_partner_to_connect,
    message_you_have_already_been_registered,
    message_help_message,
    message_your_message_is_bad_and_was_not_saved
)
from core.states import RegistrationStates
from services.dao import save_telegram_message
from core.states import is_current_state_legitimate, is_current_state_is_not_allowed

from utils.debug import logger
from utils.d_debug import d_logger
from models.message import MessageSource

from services.score_tiers import message_tiers_count

# TODO: all the cmd_ functions from handlers should be here



async def save_received_telegram_message(message: types.Message) -> bool:
    d_logger.debug("D_logger")
    if not await get_user_from_db(user_id=message.from_user.id):
        logger.sync_debug("User is not registered, so the message was not saved")
        return False
    else:       
        if not await save_telegram_message(
                message=message, message_source=MessageSource.command_received
            ):         
                await send_service_message(
                        message=message_your_message_is_bad_and_was_not_saved(),
                        chat_id=message.from_user.id,)
                return False

        return True
    

async def cmd_start(message: types.Message, state: FSMContext) -> None:
    d_logger.debug("D_logger")
    # await save_telegram_message(message=message, message_source=MessageSource.command_received)
    await state.clear()
    await state.set_data({})
    await state.set_state(CommonStates.just_started_bot)
    await send_service_message(
        message=message_cmd_start_welcome_message(), chat_id=message.from_user.id
    )


async def cmd_unregister(message: types.Message, state: FSMContext) -> None:
    d_logger.debug("D_logger")

    # await save_telegram_message(message=message, message_source=MessageSource.command_received)
    user_id = message.from_user.id
           
    if await mark_user_as_inactive_in_db(user_id):
        await send_service_message(
            message=message_user_has_been_unregistered(), chat_id=user_id
        )
    else:
        await send_service_message(
            message=message_cannot_unregister_not_registered_user(), chat_id=user_id
        )


    # if await is_current_state_legitimate(
    #     user_id=message.from_user.id,
    #     state=state,
    #     allowed_states=[
    #         UserStates.not_ready_to_chat,
    #         CommonStates.default,            
    #     ],
    # ):
    #     await send_service_message(
    #         message=message_you_cannot_unregister_now(), chat_id=message.from_user.id
    #     )

async def cmd_register(message: types.Message, state: FSMContext) -> None:
    d_logger.debug("D_logger")
    user_id = message.from_user.id
    
    user = await get_user_from_db(user_id=user_id)
    
    if not user:
        await create_new_registration(
            message,
            state,
            user_id,
            (
                message.from_user.username
                or f"{message.from_user.first_name} {message.from_user.last_name}"
            ),
        )
        await state.set_state(RegistrationStates.starting)
        await send_service_message(
            message=message_you_have_been_registered_successfully(), chat_id=user_id
        )
        await ask_user_to_send_messages_to_fill_profile(message, state)

    elif not await get_user_is_active_status_from_db(user_id): 
        user_profile_version = await get_max_profile_version_of_user_from_db(user_id=user_id)
        await set_user_profile_version_in_db(user_id=user_id, profile_version=user_profile_version+1)
        await set_is_active_flag_for_user_in_db(user_id=user_id, is_active=True)
        await send_service_message(
            message=message_you_have_already_been_registered(), chat_id=user_id
        )
        await state.set_state(RegistrationStates.starting)
        await ask_user_to_send_messages_to_fill_profile(message, state)
    else:
        await logger.error(msg="Registration failed, try /unregister", chat_id=user_id)
        raise ValueError(f"Inconsistency in registration. User id: {user_id}")
        
    # elif user.is_active and profile_messages_count == message_tiers_count.MESSAGE_TIERS_COUNT:
    #     #profile_message_count requires versioning to work
    #     #TODO: implement versionong
    #     send_service_message(message=message_reactivation_user_profile_completed(), chat_id=user_id)

    # +

    #  # The user is active but doesn't have message_tiers_count.MESSAGE_TIERS_COUNT messages, proceed with message collection
    # await ask_user_to_send_messages_to_fill_profile(message, state)


async def cmd_start_chatting(message: types.Message, state: FSMContext) -> None:
    d_logger.debug("D_logger")
    user_id = message.from_user.id
    user = await get_user_from_db(user_id)
    if user is None:
        await send_service_message(
            message=message_non_registered_users_cannot_start_chatting(),
            chat_id=user_id,
        )
        raise ValueError(
            "Value error in cmd_start_chatting. Cannot determine the sender's id"
        )
    else:
        if not await set_is_ready_to_chat_flag_for_user_in_db(user_id, True):
            raise RuntimeError(
                f"Failed to set is_ready_to_chat flag for user: {user_id}"
            )
        else:
            await send_service_message(
                message=message_you_now_ready_to_chat_please_wait_the_partner_to_connect(),
                chat_id=user_id,
            )
            await state.set_state(UserStates.ready_to_chat)
            await one_more_user_is_ready_to_chat(user_id, state)


async def default_handler(message: types.Message, state: FSMContext) -> None:
    d_logger.debug("D_logger")
    pass

async def cmd_help(message: types.Message, state: FSMContext, total_message_count: int = message_tiers_count.MESSAGE_TIERS_COUNT) -> None:
    d_logger.debug("D_logger")
    await send_service_message(message=message_help_message(total_messages_count=total_message_count), chat_id=message.from_user.id)