import asyncio

from aiogram import types
from aiogram.fsm.context import FSMContext
from config import NEXT_PLEASE_WAITING_TIMEOUT
from core.bot import bot_instance

# from app.tasks.tasks import celery_app
from core.states import UserStates, access_user_context
from core.telegram_messaging import send_service_message
from services.dao import (
    get_conversation_partner_id_from_db,
    get_currently_active_conversation_for_user_from_db,
    is_conversation_active,
    set_conversation_inactive,
)
from utils.debug import logger
from utils.text_messages import (
    message_you_are_not_in_chatting_state,
    message_you_send_end_command_and_your_partner_has_sent_it_earlier,
    message_you_sent_end_command_earlier_and_timer_expired,
    message_you_sent_end_command_earlier_and_your_just_sent_it_now,
    message_your_partner_sent_end_command_earlier_and_timer_expired,
)


async def pause(time: int = 0) -> None:
    await asyncio.sleep(time)


async def __close_up_conversation__(
    message: types.Message, state: FSMContext, time_countdown: int
) -> bool:
    user_id = message.from_user.id

    logger.sync_debug(
        f"Closing up conversation... Timer for {time_countdown} seconds started."
    )
    await pause(time_countdown)
    logger.sync_debug("Timer ended")

    user_state = await state.get_state()
    if (user_state == UserStates.chatting_in_progress) or (
        user_state == UserStates.wants_to_end_chatting
    ):
        await state.clear()
        await state.set_state(UserStates.not_ready_to_chat)
    else:
        await logger.info(msg=message_you_are_not_in_chatting_state, chat_id=user_id)
        return False

    partner_id = await get_conversation_partner_id_from_db(user_id=user_id)

    partner_context = await access_user_context(
        chat_id=partner_id, user_id=partner_id, bot_id=bot_instance.id
    )
    partner_state = await partner_context.get_state()

    if (partner_state == UserStates.chatting_in_progress) or (
        partner_state == UserStates.wants_to_end_chatting
    ):
        await partner_context.clear()
        await partner_context.set_state(UserStates.not_ready_to_chat)
        conversation = await get_currently_active_conversation_for_user_from_db(
            user_id=user_id
        )
        if await is_conversation_active(conversation_id=conversation.id):
            await set_conversation_inactive(conversation_id=conversation.id)
        return True
    else:
        await logger.error(
            msg=f"Partner is not in a conversation. User_id: {user_id}, partner_id: {partner_id}, conversation partner state: {partner_state}",
            state=state,
        )
        raise RuntimeError(
            f"Partner is not in a conversation. User_id: {user_id}, partner_id: {partner_id}, conversation partner state: {partner_state}"
        )

    # TODO: return


async def next_please_handler(message: types.Message, state: FSMContext) -> None:
    # TODO: REMOVE IT!!!!!!!!!!!!!!
    # await state.set_state(UserStates.chatting_in_progress)

    user_state = await state.get_state()
    if user_state != UserStates.chatting_in_progress:
        await logger.info(msg=message_you_are_not_in_chatting_state, state=state)
        return

    user_id = message.from_user.id
    await state.set_state(UserStates.wants_to_end_chatting)

    partner_id = await get_conversation_partner_id_from_db(user_id=user_id)

    if partner_id is None:
        await logger.error(
            msg="Failed to find the partner's user ID during /next_please", state=state
        )
        raise RuntimeError("Failed to find the partner's user ID during /next_please")

    partner_state = await access_user_context(
        chat_id=partner_id, user_id=partner_id, bot_id=bot_instance.id
    )
    partner_state = await partner_state.get_state()

    if partner_state == UserStates.wants_to_end_chatting:
        close_result = await __close_up_conversation__(message, state, time_countdown=0)
        if close_result is True:
            await send_service_message(
                message=message_you_send_end_command_and_your_partner_has_sent_it_earlier(),
                chat_id=user_id,
            )
            await send_service_message(
                message=message_you_sent_end_command_earlier_and_your_just_sent_it_now(),
                chat_id=partner_id,
            )

    elif partner_state == UserStates.chatting_in_progress:
        close_result = await __close_up_conversation__(
            message, state, time_countdown=NEXT_PLEASE_WAITING_TIMEOUT
        )
        if close_result is True:
            await send_service_message(
                message=message_you_sent_end_command_earlier_and_timer_expired(),
                chat_id=user_id,
            )
            await send_service_message(
                message=message_your_partner_sent_end_command_earlier_and_timer_expired(),
                chat_id=partner_id,
            )
    else:
        await logger.error(
            msg=f"Partner is not in a conversation or wants to end.. User_id: {user_id}, partner_id: {partner_id}, conversation partner state: {partner_state}",
            state=state,
        )
        raise RuntimeError(
            f"Partner is not in a conversation or wants to end.. User_id: {user_id}, partner_id: {partner_id}, conversation partner state: {partner_state}"
        )
