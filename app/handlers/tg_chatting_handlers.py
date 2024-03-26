from datetime import datetime
from typing import Union

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReactionTypeEmoji
from core.bot import bot_instance

# from app.tasks.tasks import celery_app
from core.states import (
    CommonStates,
    UserStates,
    get_user_context,
    initialize_states_for_chatter_to_start_conversation,
)
from core.telegram_messaging import (
    send_reconstructed_telegram_message_to_user,
    send_service_message,
    send_tiered_partner_s_message_to_user,
)
from models.message import MessageSource
from services.dao import (
    create_new_conversation_for_users_in_db,
    get_conversation_partner_id_from_db,
    get_currently_active_conversation_for_user_from_db,
    get_max_profile_version_of_user_from_db,
    get_message_for_given_conversation_from_db,
    get_message_in_inactive_conversations_from_db,
    get_new_partner_for_conversation_for_user_from_db,
    save_telegram_message,
    save_telegram_reaction,
)
from services.emoji_rank import EmojiRank
from services.score_tiers import profile_disclosure_tiers_score_levels
from sqlalchemy.exc import SQLAlchemyError
from utils.debug import logger
from utils.text_messages import (
    message_a_conversation_partner_found,
    message_no_partners_ready_to_chat_available_we_will_inform_you_later,
    message_the_last_tier_reached,
    message_you_have_reached_the_next_tier,
    message_you_now_connected_to_the_conversation_partner,
    message_you_should_not_react_your_own_messages,
)


async def __set_disclosure_level__(
    state: FSMContext,
    level: int,
) -> None:
    await state.update_data(disclosure_level=level)


async def __get_disclosure_level__(
    state: FSMContext,
) -> int:
    disclosure_level_data = await state.get_data()
    disclosure_level: int = disclosure_level_data["disclosure_level"]
    return disclosure_level


# TODO: возможно, во всех случаях Exceptions ставить default_state, причём не только тут.


async def one_more_user_is_ready_to_chat(user_id: int, state: FSMContext) -> None:
    # TODO: test this logic!
    user_readiness = await state.get_state
    if user_readiness != UserStates.ready_to_chat:
        return

    try:
        partner = await get_new_partner_for_conversation_for_user_from_db(user_id)
        if partner is None:
            await send_service_message(
                message=message_no_partners_ready_to_chat_available_we_will_inform_you_later(),
                chat_id=user_id,
            )

        # TODO: why ready_to_chat? It should be chatting_in_progress | COMMENTED WITHOUT TEST!!!
        # await state.set_state(UserStates.ready_to_chat)
        # TODO: remove this:
        await logger.debug(msg="Разберись со строкой выше!!!111", state=state)

        # Step 3: Create a new Conversation instance
        user_profile_version = get_max_profile_version_of_user_from_db(user_id=user_id)
        partner_profile_version = get_max_profile_version_of_user_from_db(
            user_id=partner.id
        )
        conversation = await create_new_conversation_for_users_in_db(
            user_id=user_id,
            user_profile_version=user_profile_version,
            partner_id=partner.id,
            patner_profile_version=partner_profile_version,
        )
        if conversation is None:
            await logger.error(
                msg=f"Conversation was not created. User_id: {user_id}, partner_id: {partner.id}",
                chat_id=user_id,
            )
            await logger.error(
                msg=f"Conversation was not created. User_id: {user_id}, partner_id: {partner.id}",
                chat_id=partner.id,
            )
            return False
        else:
            logger.sync_debug(
                f"Conversation created. Conversation_id: {conversation.id}"
            )

        # Update the state for both users
        partner_context = await get_user_context(user_id=partner.id)
        await initialize_states_for_chatter_to_start_conversation(state=state)
        await initialize_states_for_chatter_to_start_conversation(state=partner_context)

        # Inform both the users and log
        await logger.info(
            msg=message_you_now_connected_to_the_conversation_partner(),
            chat_id=user_id,
        )

        await logger.info(
            msg=message_a_conversation_partner_found(),
            chat_id=partner.id,
        )

    except Exception as e:
        await logger.error(
            msg=f"Caught exception in state_user_is_ready_to_chat_handler: {str(e)}",
            chat_id=user_id,
        )
        await logger.error(
            msg=f"Caught exception in state_user_is_ready_to_chat_handler: {str(e)}",
            chat_id=partner.id,
        )

        # TODO:Check state management logic!
        await state.set_state(CommonStates.default)
        await partner_context.set_state(CommonStates.default)


async def state_user_is_in_chatting_progress_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    conversation = get_currently_active_conversation_for_user_from_db(user_id=user_id)
    if conversation is not None:
        partner_id = get_conversation_partner_id_from_db(user_id=user_id)
        if partner_id is not None:
            reconstructed_message = await save_telegram_message(
                message=message,
                message_source=MessageSource.conversation,
                conversation_id=conversation.id,
            )
            await send_reconstructed_telegram_message_to_user(
                message=reconstructed_message, user_id=partner_id
            )
        else:
            await logger.error(
                msg="Partner ID is None in state_user_is_in_chatting_progress_handler. Please contact support."
            )
    else:
        await logger.error(
            msg="Conversation is None in state_user_is_in_chatting_progress_handler. Please contact support."
        )


async def update_user_score_in_conversation(state: FSMContext, delta: float) -> int:
    score_data = await state.get_data()
    new_score = score_data["current_score"] + delta
    await state.update_data(current_score=new_score)
    return new_score


async def check_conversation_score_threshold(
    current_score: int, state: FSMContext
) -> Union[int, bool]:
    current_disclosure_level = await __get_disclosure_level__(state)
    for index, tier_threshold in enumerate(
        reversed(profile_disclosure_tiers_score_levels.PROFILE_DISCLOSURE_TIER_LEVELS)
    ):
        reversed_index = (
            len(profile_disclosure_tiers_score_levels.PROFILE_DISCLOSURE_TIER_LEVELS)
            - 1
            - index
        )
        if (current_score >= tier_threshold) and (
            current_disclosure_level < reversed_index
        ):
            await __set_disclosure_level__(state, reversed_index)
            await logger.debug(
                msg=f"Your score is {current_score}. You have reached the {tier_threshold} score threshold at index {index}.",
                state=state,
            )
            return reversed_index

    await logger.debug(
        msg=f"Your score is {current_score}. You have not reached the {tier_threshold} score threshold at index {index}.",
        state=state,
    )
    return False


#
# TODO: handle changing or removing the reactions
async def message_reaction_handler(
    message_reaction: types.MessageReactionUpdated, user_context: FSMContext
) -> None:
    user_id = message_reaction.user.id

    conversation = await get_currently_active_conversation_for_user_from_db(
        user_id=user_id
    )

    if not conversation:
        await logger.error(
            msg="Failed to find the conversation where the message was sent",
            state=user_context,
        )
        raise SQLAlchemyError(
            "Failed to find the conversation where the message was sent"
        )

    message_from_db = await get_message_for_given_conversation_from_db(
        message_id=message_reaction.message_id, conversation_id=conversation.id
    )
    if message_from_db is None:
        message_from_db = await get_message_in_inactive_conversations_from_db(
            message_id=message_reaction.message_id
        )
        if message_from_db is not None:
            await logger.error(
                msg="It seems the user reacted the message in an inactive conversation",
                state=user_context,
            )
            return
        await logger.error(
            msg="Failed to find the message in the database", state=user_context
        )
        raise SQLAlchemyError("Failed to find the message in the database")

    # Users should not react to their own messages
    message_sender = message_from_db.sender_in_conversation_id

    if message_sender is None:
        await logger.error(
            msg="Failed to find the message sender in the database for the message was reacted.",
            state=user_context,
        )

        # TODO:
        # А вот тут посмотреть, что делать. None может быть разным:
        # Первые два пункта пофиксятся, когда все сообщения будут сохраняться
        # 1 — когда юзер лайкнул что-то из предыдущей беседы -
        # 2 — когда юзер лайкнул сервисное сообщение бота
        # 3 — реальная ошибка логики / бота
        # В первом случае надо ему послать сообщение о том, что не надо лайкать предыдущее
        # Во втором надо сказать, что бота лайкать не нужно (и не продолжать логику исполнения)
        # В третьем — кинуть не только исключение, но и сообщение юзеру — полезно на тест.

        return

    if user_id == message_sender:
        # TODO: add more user messages text for this (i.e. narcissism)
        await send_service_message(
            message=message_you_should_not_react_your_own_messages(), chat_id=user_id
        )
        return

    try:
        try:
            new_emoji = message_reaction.new_reaction[0].emoji
            inverse_multiplier = 1
        except IndexError:
            new_emoji = None

        try:
            old_emoji = message_reaction.old_reaction[0].emoji
            inverse_multiplier = -1
        except IndexError:
            old_emoji = None

        emoji = new_emoji or old_emoji

        ranker = EmojiRank()
        rank = ranker.get_rank(emoji) * inverse_multiplier

        message = await get_message_for_given_conversation_from_db(
            message_id=message_reaction.message_id, conversation_id=conversation.id
        )
        message_id = message.id

        # Save the reaction
        # TODO: -1 logic from __get_message_sender_id_from_db__()
        if await save_telegram_reaction(
            user_id=message_reaction.user.id,
            # I do not know why -1 is needed
            message_id=message_id,
            new_emoji=new_emoji,
            old_emoji=old_emoji,
            timestamp=datetime.now(),
            rank=rank,
        ):
            # Identify the other participant in the conversation and set reaction in his/her chat
            partner_id = (
                conversation.user2_id
                if conversation.user1_id == user_id
                else conversation.user1_id
            )
            emoji_reaction = ReactionTypeEmoji(emoji=new_emoji) if new_emoji else None

            await bot_instance.set_message_reaction(
                chat_id=partner_id,
                message_id=message_id,
                reaction=[emoji_reaction] if emoji_reaction else [],
            )

            current_score = await update_user_score_in_conversation(
                state=user_context, delta=rank
            )

            reached_tier = await check_conversation_score_threshold(
                current_score=current_score, state=user_context
            )
            if reached_tier is not False:
                logger.sync_debug(
                    msg=f"Your score is {current_score}. You have reached the {reached_tier} score threshold."
                )
                await send_service_message(
                    message=message_you_have_reached_the_next_tier(
                        current_score=current_score, reached_tier=reached_tier
                    ),
                    chat_id=user_id,
                )

                # TODO: Change all the parameters everywhere for named arguments instead of positional
                await send_tiered_partner_s_message_to_user(
                    bot_instance, user_id, partner_id, reached_tier
                )

                if (
                    reached_tier
                    >= len(
                        profile_disclosure_tiers_score_levels.PROFILE_DISCLOSURE_TIER_LEVELS
                    )
                    - 1
                ):
                    await logger.sync_debug(
                        msg=f"Your score is {current_score}. You have reached the last score threshold."
                    )

                    await send_service_message(
                        message=message_the_last_tier_reached(), chat_id=user_id
                    )

        else:
            # TODO: here and everywhere else: clear states on exceptions!

            logger.error("Failed to save the reaction to the database")
            raise SQLAlchemyError("Failed to save the reaction to the database")

    except Exception as e:
        logger.error(f"An exception occurred while handling the message reaction: {e}")
