from aiogram import types
from aiogram.fsm.context import FSMContext
from core.states import CommonStates, RegistrationStates
from core.telegram_messaging import send_service_message
from models.user import User
from services.dao import (
    get_max_profile_version_of_user_from_db,
    get_user_from_db,
    save_tiered_registration_message,
    save_user_to_db,
    set_is_active_flag_for_user_in_db,
)
from services.score_tiers import message_tiers_count
from utils.debug import logger
from utils.text_messages import (
    message_now_please_send_profile_messages,
    message_profile_message_received_please_send_the_remaining,
    message_registration_failed,
    message_your_profile_message_saved_and_profile_successfully_filled_up,
    message_your_message_is_bad_and_was_not_saved,
)

# from app.tasks.tasks import celery_app


# This function will create a new user instance in the database and initiate the message receiving state.
async def create_new_registration(
    message: "types.Message",
    state: "FSMContext",
    user_id: "int",
    username: "str",
) -> "None":
    existing_user = await get_user_from_db(user_id=user_id)
    if existing_user:
        existing_user.is_active = True
        existing_user.profile_version += 1
        await save_user_to_db(existing_user)
    else:
        user_profile_version = 0
        new_user = User(
            id=user_id,
            username=username,
            is_active=True,
            is_ready_to_chat=False,
            profile_version=user_profile_version,
        )
        await save_user_to_db(new_user)

    await ask_user_to_send_messages_to_fill_profile(message, state)


# This function will handle any exceptions that occur during the registration process.
async def registration_failed(
    message: types.Message, state: FSMContext, exception: Exception
) -> None:
    await state.set_state(CommonStates.default)
    await logger.error(
        msg=f"{message_registration_failed()} Exception: {str(exception)}", state=state
    )


async def increment_message_count(message: types.Message, state: FSMContext) -> int:
    user_data = await state.get_data()
    message_count = user_data.get("message_count", 0) + 1
    await state.update_data(message_count=message_count)
    return message_count


async def check_message_threshold(
    message: types.Message, state: FSMContext, message_count: int
) -> None:
    if message_count < message_tiers_count.MESSAGE_TIERS_COUNT:
        await send_service_message(
            message=message_profile_message_received_please_send_the_remaining(
                message_count=message_count,
                total_messages_count=message_tiers_count.MESSAGE_TIERS_COUNT,
            ),
            chat_id=message.from_user.id,
        )
    else:
        await complete_registration(message, state)


async def complete_registration(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user = await get_user_from_db(user_id)
    if user is not None:
        await set_is_active_flag_for_user_in_db(user_id, True)
        await send_service_message(
            message=message_your_profile_message_saved_and_profile_successfully_filled_up(),
            chat_id=user_id,
        )
    else:
        await logger.error(msg="No user found with ID {}", user_id=user_id)
        raise ValueError(f"No user found with ID {user_id}")
    await state.set_state(CommonStates.default)


async def ask_user_to_send_messages_to_fill_profile(
    message: types.Message, state: FSMContext
) -> None:
    
    user_state = await state.get_state()
    if user_state == RegistrationStates.starting:
        await state.set_state(RegistrationStates.receiving_messages)
        await state.update_data(message_count=0)
        logger.sync_debug(f"User {message.from_user.id} has started registration.")
        await send_service_message(
            message=message_now_please_send_profile_messages(
                message_tiers_count.MESSAGE_TIERS_COUNT
            ),
            chat_id=message.from_user.id,
        )


async def receiving_messages_on_registration_handler(
    message: types.Message, state: FSMContext
) -> None:
    if (
        state is RegistrationStates.receiving_messages
        or RegistrationStates.starting
        or RegistrationStates.completed
    ):
        user_profile_version = await get_max_profile_version_of_user_from_db(
            user_id=message.from_user.id
        )
        message_count = await increment_message_count(message, state)
        if not await save_tiered_registration_message(message=message, message_count=message_count, profile_version = user_profile_version):
            await send_service_message(
                message=message_your_message_is_bad_and_was_not_saved(),
                chat_id=message.from_user.id,
            )
        else:    
            await check_message_threshold(message, state, message_count)
    else:
        await logger.error(
            msg=f"Unexpected state encountered while receiving messages on registration: {state}",
            state=state,
        )
