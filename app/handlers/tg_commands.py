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
)
from core.states import RegistrationStates

from utils.debug import logger


# TODO: all the cmd_ functions from handlers should be here


async def cmd_start(message: types.Message, state: FSMContext) -> None:
    # await save_telegram_message(message=message, message_source=MessageSource.command_received)
    await state.clear()
    await state.set_data({})
    await state.set_state(CommonStates.default)
    await send_service_message(
        message=message_cmd_start_welcome_message(), chat_id=message.from_user.id
    )


async def cmd_unregister(message: types.Message, state: FSMContext) -> None:
    # await save_telegram_message(message=message, message_source=MessageSource.command_received)
    user_state = await state.get_state()
    if (user_state == CommonStates.default) or (user_state == UserStates.not_ready_to_chat):
        user_id = message.from_user.id
        if await mark_user_as_inactive_in_db(user_id):
            await send_service_message(
                message=message_user_has_been_unregistered(), chat_id=user_id
            )
        else:
            await send_service_message(
                message=message_cannot_unregister_not_registered_user(), chat_id=user_id
            )
    else:
        await send_service_message(
            message=message_you_cannot_unregister_now(), chat_id=message.from_user.id
        )


# async def cmd_hard_unregister(message: types.Message):
#     user_id = message.from_user.id
#     if await delete_user_profile_from_db(user_id):
#         await send_service_message(message=message_user_has_already_been_hardly_unregistered(), chat_id=user_id)
#     else:
#         await send_service_message(message=message_cannot_unregister_not_registered_user(), chat_id=user_id)


# async def cmd_renew_profile(message: types.Message, state: FSMContext):
#     try:
#         user_state = await state.get_state()
#     except:
#         user_state = None
#     if (user_state == CommonStates.default):
#         kjh
#         await state.clear()
#         await state.set_state(UserStates.not_ready_to_chat)
#     else:
#         await send_service_message(message=message_you_are_not_in_default_state_and_cannot_renew_profile(), chat_id=message.from_user.id)
#         return


async def cmd_register(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user = await get_user_from_db(user_id=user_id)
    user_state = await state.get_state()
    if user_state != CommonStates.default:
        await send_service_message(
            message=message_you_are_not_in_default_state_and_cannot_register(),
            chat_id=user_id,
        )
        return False
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
        await logger.error(msg="User {} is already registered, but the users profile is active, so cmd_register failed", chat_id=user_id)
        raise ValueError(f"User {user_id} is already registered, but the users profile is active, so cmd_register failed")
        
    # elif user.is_active and profile_messages_count == message_tiers_count.MESSAGE_TIERS_COUNT:
    #     #profile_message_count requires versioning to work
    #     #TODO: implement versionong
    #     send_service_message(message=message_reactivation_user_profile_completed(), chat_id=user_id)

    # +

    #  # The user is active but doesn't have message_tiers_count.MESSAGE_TIERS_COUNT messages, proceed with message collection
    # await ask_user_to_send_messages_to_fill_profile(message, state)


async def cmd_start_chatting(message: types.Message, state: FSMContext) -> None:
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
    pass
