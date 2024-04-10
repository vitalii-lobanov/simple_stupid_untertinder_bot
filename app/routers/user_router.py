# app/routers/user_router.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from core.bot import bot_instance
from database.engine import get_session
from sqlalchemy.exc import SQLAlchemyError

# , state_user_is_ready_to_chat_handler
from core.states import RegistrationStates, UserStates, CommonStates
from core.telegram_messaging import (
    send_reconstructed_telegram_message_to_user,
    send_service_message,

)
from services.tiered_messages import send_tiered_partner_s_message_to_user
from core.telegram_messaging import check_message_is_part_of_mediagroup_and_notify_user
# registration_handlers.py
from filters.custom_filters import InStateFilter
from handlers.tg_chatting_handlers import (
    message_reaction_handler,
    state_user_is_in_chatting_progress_handler,
)
from handlers.tg_commands import cmd_register, cmd_start, default_handler
from handlers.tg_partner_change_handlers import next_please_handler
from handlers.tg_user_register_handlers import (
    receiving_messages_on_registration_handler,
)
import sys
# from handlers.tg_commands import message_reaction_handler

from services.dao import get_user_from_db

from models.base import MessageSource
from services.dao import save_telegram_message
from services.score_tiers import message_tiers_count
from utils.debug import logger
from utils.d_debug import d_logger
from handlers.tg_commands import (
    cmd_start_chatting,
    cmd_unregister,
    save_received_telegram_message,
    cmd_help,
)
from core.states import check_user_state
from utils.text_messages import (
    message_you_cannot_unregister_now,
    message_you_should_not_run_start_command_when_not_starting,
    message_you_cannot_register_now_please_unregister,
    message_you_cannot_run_next_please_now,
    message_you_cannot_use_show_my_profile_now,
    message_you_cannot_start_chatting_now,
    message_i_do_not_know_what_to_do_with_this_message,
    message_your_message_is_bad_and_was_not_saved,
    message_your_registration_completed_stop_send_messages,
    message_you_cannot_use_reactions_now,
)
from core.states import is_current_state_legitimate, is_current_state_is_not_allowed
from core.telegram_messaging import reply_to_telegram_message
from handlers.middleware import MessageOrderingMiddleware

from core.states import (
    start_cmd_allowed_states,
    regitser_cmd_allowed_states,
    unregister_cmd_allowed_states,
    show_my_profile_cmd_allowed_states,
    start_chatting_cmd_allowed_states,
    next_please_cmd_allowed_states,
    chatting_process_message_receiving_allowed_states,
    receiving_registration_profile_messages_allowed_states
)

# bot_instance = None

# Custom filter for registration process

# user_is_in_starting_registration_state_filter = InStateFilter(
#     RegistrationStates.starting
# )
user_is_in_receiving_messages_during_registration_state_filter = InStateFilter(
    [RegistrationStates.receiving_messages]
)
user_is_in_completed_registration_state_filter = InStateFilter(
    [RegistrationStates.completed]
)
user_is_in_ready_for_chatting_state_filter = InStateFilter(UserStates.ready_to_chat)
user_is_in_chatting_in_progress_state_filter = InStateFilter(
    [UserStates.chatting_in_progress,
    UserStates.wants_to_end_chatting,]
)
user_is_in_not_ready_to_chat_state_filter = InStateFilter(UserStates.not_ready_to_chat)


user_router = Router()
user_router.message.middleware(MessageOrderingMiddleware(user_router))


@user_router.message(Command(commands=["unregister"]))
async def cmd_user_unregister(message: types.Message, state: FSMContext) -> None:
    d_logger.debug("D_logger")
    current_state = await state.get_state()    
    d_logger.debug(f"Trying to unregister. Current state: {current_state}")
    if not await is_current_state_legitimate(
        user_id=message.from_user.id,
        state=state,
        # allowed_states=[
        #     UserStates.ready_to_chat,
        #     CommonStates.default,
        #     UserStates.not_ready_to_chat,
        #     RegistrationStates.completed,
        # ],
        allowed_states=unregister_cmd_allowed_states,
    ):
        await send_service_message(
            message=message_you_cannot_unregister_now(),
            chat_id=message.from_user.id,
        )
        return
    if await check_message_is_part_of_mediagroup_and_notify_user(message=message):
        return
    if not await save_telegram_message(
        message=message, message_source=MessageSource.command_received
    ):
        await send_service_message(
                        message=message_your_message_is_bad_and_was_not_saved(),
                        chat_id=message.from_user.id,)
        return
    await cmd_unregister(message, state)


# TODO: all the command handlers rename to cmd_*
# TODO: handle start command corrtectly
@user_router.message(Command(commands=["start"]))
async def cmd_user_start(message: types.Message, state: FSMContext) -> None:
    d_logger.debug("D_logger")
    try:
        if await state.get_state():
            await save_received_telegram_message(message)
            await send_service_message(
                message=message_you_should_not_run_start_command_when_not_starting(),
                chat_id=message.from_user.id,
            )
            return

        await state.set_state(CommonStates.just_started_bot)
        logger.sync_debug("'/start' command received")
        await cmd_start(message, state)
    except Exception as e:
        logger.sync_error(msg=f"Error starting user handling: {e}")

# The user starts a registration process
@user_router.message(Command(commands=["register"]))
async def cmd_user_register_start(message: types.Message, state: FSMContext) -> None:
    d_logger.debug("D_logger")
    current_state = await state.get_state()
    d_logger.debug(f"Trying to register. Current state: {current_state}")
    if await is_current_state_legitimate(
        user_id=message.from_user.id,
        state=state,
        # allowed_states=[RegistrationStates.starting, CommonStates.just_started_bot],
        allowed_states=regitser_cmd_allowed_states,
    ):
        await save_received_telegram_message(message)
        logger.sync_debug("'/register' command received")
        await cmd_register(message, state)
    else:
        await send_service_message(
            message=message_you_cannot_register_now_please_unregister(),
            chat_id=message.from_user.id,
        )


@user_router.message(Command(commands=["next_please"]))
async def cmd_next_please(message: types.Message, state: FSMContext) -> None:
    d_logger.debug("D_logger")
    if not await is_current_state_legitimate(
        user_id=message.from_user.id,
        state=state,
        # allowed_states=[UserStates.chatting_in_progress],
        allowed_states=next_please_cmd_allowed_states,
    ):
        await send_service_message(
            message=message_you_cannot_run_next_please_now(),
            chat_id=message.from_user.id,
        )
        return
    await save_received_telegram_message(message)
    logger.sync_debug("'/next_please' command received")
    if await check_message_is_part_of_mediagroup_and_notify_user(message=message):
        return
    await next_please_handler(message, state)


@user_router.message(Command(commands=["show_my_profile"]))
async def cmd_user_show_my_profile(message: types.Message, state: FSMContext) -> None:
    d_logger.debug("D_logger")
    current_state = await state.get_state()
    d_logger.debug(f"Trying to show profile. Current state: {current_state}")
    if not await is_current_state_legitimate(
        user_id=message.from_user.id,
        state=state,

        allowed_states=show_my_profile_cmd_allowed_states,
    ):
        await send_service_message(
            message=message_you_cannot_use_show_my_profile_now(),
            chat_id=message.from_user.id,
        )
        return

    if await check_message_is_part_of_mediagroup_and_notify_user(message=message):
        return
    await save_received_telegram_message(message)

    logger.sync_debug("'/show_my_profile' command received")
    for i in range(0, message_tiers_count.MESSAGE_TIERS_COUNT):
        await send_tiered_partner_s_message_to_user(
            user_id=message.from_user.id, tier=i, partner_id=message.from_user.id
        )


@user_router.message(Command(commands=["start_chatting"]))
async def cmd_user_start_chatting(message: types.Message, state: FSMContext) -> None:
    d_logger.debug("D_logger")
    if await is_current_state_legitimate(
        user_id=message.from_user.id,
        state=state,

        allowed_states=start_chatting_cmd_allowed_states,
    ):
        await save_received_telegram_message(message)
        if await check_message_is_part_of_mediagroup_and_notify_user(message=message):
            return
        await cmd_start_chatting(message, state)
    else:
        await send_service_message(
            message=message_you_cannot_start_chatting_now(),
            chat_id=message.from_user.id,
        )
        # await state.set_state(UserStates.ready_to_chat)


@user_router.message(Command(commands=["help"]))
async def cmd_user_help(message: types.Message, state: FSMContext) -> None:
    d_logger.debug("D_logger")
    # await save_telegram_message(
    #     message=message, message_source=MessageSource.command_received
    # )
    await cmd_help(message, state)


# The user sends message_tiers_count.MESSAGE_TIERS_COUNT messages to complete registration
@user_router.message(user_is_in_receiving_messages_during_registration_state_filter)
async def handle_user_receiving_messages_on_registration(
    message: types.Message, state: FSMContext
) -> None:
    if await is_current_state_legitimate(
        user_id=message.from_user.id,
        state=state,
        allowed_states=receiving_registration_profile_messages_allowed_states,
    ):    
        current_state = await state.get_state()
        d_logger.debug(f"Receiving registration messages. Current state: {current_state}")
        
        logger.sync_debug("Handler for receiving_messages state")
        if await check_message_is_part_of_mediagroup_and_notify_user(message=message):
            return
        await receiving_messages_on_registration_handler(message, state)
    else:
        await reply_to_telegram_message(message=message, text=message_your_registration_completed_stop_send_messages())


@user_router.message_reaction()
async def message_user_reaction_handler(
    message_reaction: types.MessageReactionUpdated, state: FSMContext
) -> None:
    d_logger.debug("D_logger")
    logger.sync_debug("Message reaction handler...")
    if not is_current_state_legitimate(user_id=message_reaction.user.id, state=state, allowed_states=chatting_process_message_receiving_allowed_states):
       await send_service_message(message=message_you_cannot_use_reactions_now(), chat_id=message_reaction.user.id)
       return
    await message_reaction_handler(message_reaction, state)


@user_router.message(user_is_in_chatting_in_progress_state_filter)
async def state_user_is_in_chatting_progress(
    message: types.Message, state: FSMContext
) -> None:
    d_logger.debug("D_logger")
    logger.sync_debug("We're inside state_user_is_in_chatting_progress")
    if not is_current_state_legitimate(user_id=message.from_user.id, state=state, allowed_states=chatting_process_message_receiving_allowed_states):
       return

    if await check_message_is_part_of_mediagroup_and_notify_user(message=message):
        return
    await state_user_is_in_chatting_progress_handler(message, state)


@user_router.message()
async def default_message_handler(message: types.Message, state: FSMContext) -> None:
    d_logger.debug("D_logger")
    logger.sync_debug("Default message handler...")
    current_st = await state.get_state()
    d_logger.debug(current_st)
    if not current_st:
        await reply_to_telegram_message(
            message=message, text=message_i_do_not_know_what_to_do_with_this_message()
        )
        return

    if not await is_current_state_is_not_allowed(
        user_id=message.from_user.id,
        state=state,
        not_allowed_states=[CommonStates.just_started_bot],
    ):
        if await check_message_is_part_of_mediagroup_and_notify_user(message=message):
            return
        if not await save_telegram_message(
            message=message, message_source=MessageSource.bot_message_received
        ): 
            await send_service_message(
                        message=message_your_message_is_bad_and_was_not_saved(),
                        chat_id=message.from_user.id,)
            return
        await default_handler(message, state)
