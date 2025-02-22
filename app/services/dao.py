import json
import os
import random

from functools import wraps
from typing import Any, Dict, List, Optional, Union

from aiogram import Bot, types
from core.telegram_messaging import send_service_message
from utils.text_messages import message_your_message_is_bad_and_was_not_saved
from config import BOT_TOKEN, DOWNLOAD_PATH
from database.engine import get_session, manage_db_session
from models import Conversation, ProfileData
from models.base import MessageSource
from models.message import Message
from models.reaction import Reaction
from models.user import User
from helpers.serializing_helpers import (
    get_multimedia_paths_from_message,
    link_preview_options_to_dict,
    location_to_dict,
    message_entities_to_dict,
    message_poll_to_dict,
)
from helpers.tg_helpers import download_telegram_file, get_telegram_file
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from utils.debug import logger
from utils.d_debug import d_logger
from datetime import datetime


@manage_db_session
async def save_telegram_message(
    session: AsyncSession = None,
    message: types.Message = None,
    message_source: MessageSource = None,
    tier: int = -1,
    conversation_id: int = None,
    profile_version: int = -1,
    message_id_for_sender: int = None,
) -> Message:
    d_logger.debug("D_logger")
    user_id = message.from_user.id
    message_id_for_receiver = message.message_id

    # Extract the file ID of the largest photo
    # if message.photo:
    #     photo = message.photo[
    #         -1
    #     ].file_id  # Get the file_id of the last (largest) photo size

    from_user_data = vars(message.from_user)
    from_user_json = json.dumps(from_user_data)

    multimedia_list = get_multimedia_paths_from_message(message)
    for key, value in multimedia_list.items():
        if value is not None:
            try:
                downloaded_file = await download_telegram_file(file_id=value)
                if not downloaded_file:
                    return False
                else:
                    multimedia_list[key] = await download_telegram_file(file_id=value)
            except Exception as e:
                logger.sync_error(msg=f"Error downloading multimedia: {e}")
                return False
                # raise e

    if message.forward_date:
        forward_date = message.forward_date
        forward_date_naive = forward_date.replace(tzinfo=None)
    else:
        forward_date_naive = None

    try:
        new_message = Message(
            user_id=user_id,
            tier=tier,
            message_source=message_source,
            tg_message_id_for_receiver=message_id_for_receiver,
            tg_message_id_for_sender=message_id_for_sender,
            conversation_id=conversation_id,
            user_profile_version=profile_version,
            text=message.text or None,
            audio=multimedia_list["audio"],
            video=multimedia_list["video"],
            voice=multimedia_list["voice"],
            video_note=multimedia_list["video_note"],
            image=multimedia_list["photo"],
            document=multimedia_list["document"],
            photo=multimedia_list["photo"],
            author_signature=message.author_signature
            if message.author_signature
            else None,
            caption=message.caption if message.caption else None,
            # caption_entities=message.caption_entities if message.caption_entities else None,
            # entities=message.entities if message.entities else None,
            caption_entities=message_entities_to_dict(message.caption_entities)
            if message.caption_entities
            else None,
            entities=message_entities_to_dict(message.entities)
            if message.entities
            else None,
            contact=message.contact if message.contact else None,
            forward_date=forward_date_naive if message.forward_date else None,
            from_user=from_user_json if from_user_json else None,
            game=message.game if message.game else None,
            dice=message.dice if message.dice else None,
            html_text=message.html_text if message.html_text else None,
            invoice=message.invoice if message.invoice else None,
            location=location_to_dict(message.location) if message.location else None,
            link_preview_options=link_preview_options_to_dict(
                message.link_preview_options
            )
            if message.link_preview_options
            else None,
            md_text=message.md_text if message.md_text else None,
            media_group_id=message.media_group_id if message.media_group_id else None,
            original_sender_id=message.forward_from.id
            if message.forward_from
            else None,
            original_sender_username=message.forward_from.username
            if message.forward_from
            else None,
            poll=message_poll_to_dict(message.poll) if message.poll else None,
            quote=message.quote if message.quote else None,
            story=message.story if message.story else None,
            sender_in_conversation_id=user_id
            if message.from_user
            else None,
            sticker=message.sticker.file_id if message.sticker else None,
            animation=message.animation.file_id if message.animation else None,
        )
        session.add(new_message)
        # session.commit()
    except Exception as e:
        # session.rollback()
        await logger.sync_error(msg=f"Failed to save message: {e}")
        raise e
    # finally:
    #     #session.close()

    return new_message


async def save_tiered_registration_message(
    message: types.Message,
    message_count: int,
    profile_version: int,
) -> bool:
    d_logger.debug("D_logger")
    # tier = message_count - 1
    tier = message_count
    message_source = MessageSource.registration_profile

    user_id = message.from_user.id
    async with get_session() as session:
        reconstructed_message = await save_telegram_message(
            message=message,
            message_source=message_source,
            tier=tier,
            profile_version=profile_version,
        )
        if reconstructed_message:
            user_id = message.from_user.id
            message_id = reconstructed_message.id
            profile_data = ProfileData(user_id=user_id, message_id=message_id, profile_version=profile_version)
            try:
                session.add(profile_data)
                return True
            except Exception as e:
                # session.rollback()
                # Assuming you have a logger configured
                await logger.error(
                    msg=f"Failed to save profile data: {e}", chat_id=user_id
                )
                return False
        else:
            await logger.error(
                msg=f"Failed to save profile data message: {message}", chat_id=user_id
            )
            await send_service_message(
                        message=message_your_message_is_bad_and_was_not_saved(),
                        chat_id=message.from_user.id,)
            return False
            


@manage_db_session
async def save_telegram_reaction(
    user_id: int,
    new_emoji: str,
    old_emoji: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    tg_message_id_for_receiver: int = -1,
    message_id: int = None,
    rank: int = 0,
    session: AsyncSession = None,
) -> bool:
    d_logger.debug("D_logger")
    try:
        # Create a new Reaction instance
        reaction = Reaction(
            user_id=user_id,
            message_id=message_id,
            tg_message_id_for_receiver=tg_message_id_for_receiver,
            new_emoji=new_emoji,
            old_emoji=old_emoji,
            timestamp=timestamp,
            # receiver_message_id=receiver_message_id,
            rank=rank,
        )

        # Add the new reaction to the session and commit
        session.add(reaction)
        logger.sync_debug("Reaction saved.")
        return True

    except SQLAlchemyError as e:
        # Handle any database errors
        await logger.error(
            msg=f"SQLAlchemy error saving reaction: {e}", chat_id=user_id, exc_info=True
        )
        # session.rollback()
        raise
    except Exception as e:
        # Handle any other exceptions
        await logger.error(
            msg=f"Error saving reaction: {e}", chat_id=user_id, exc_info=True
        )
        raise e


@manage_db_session
async def get_message_for_given_conversation_from_db_by_receiver_id(
    message_id: int, conversation_id: int, session: AsyncSession = None
) -> Message:
    d_logger.debug("D_logger")
    try:
        result = await session.execute(
            select(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(
                Message.tg_message_id_for_receiver == message_id,
                Conversation.id == conversation_id,
            )
        )
        message = result.scalars().first()

        if message:
            return message
        else:
            raise ValueError(
                f"No message found with ID {message_id} and conversation ID {conversation_id}"
            )
    except Exception as e:
        await logger.error(
            msg=f"Failed to retrieve message: {e}", chat_id=None
        )  # TODO: Replace None with actual chat_id if available
        return None




@manage_db_session
async def get_message_for_given_conversation_from_db_by_sender_id(
    message_id: int, conversation_id: int, session: AsyncSession = None
) -> Message:
    d_logger.debug("D_logger")
    try:
        result = await session.execute(
            select(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(
                Message.tg_message_id_for_sender == message_id,
                Conversation.id == conversation_id,
            )
        )
        message = result.scalars().first()


        # # DIRTY DIRTY HACK DO NOT USE
        # if not message:
        #     result = await session.execute(
        #     select(Message)
        #     .join(Conversation, Message.conversation_id == Conversation.id)
        #     .filter(
        #         Message.tg_message_id_for_receiver == message_id,
        #         Conversation.id == conversation_id,
        #     )
        # )
        # message = result.scalars().first()

        if message:
            return message
        else:
            return None
    except Exception as e:
        logger.sync_debug(
            msg=f"Failed to retrieve message: {e}", chat_id=None
        )  # TODO: Replace None with actual chat_id if available
        raise e


@manage_db_session
async def get_currently_active_conversation_for_user_from_db(
    user_id: int, session: AsyncSession = None
) -> Conversation | None:
    d_logger.debug("D_logger")
    try:
        result = await session.execute(
            select(Conversation).filter(
                (
                    (Conversation.user1_id == user_id)
                    | (Conversation.user2_id == user_id)
                ),
                Conversation.is_active.is_(True),  # Use is_() for NULL-safe comparison
            )
        )
        conversation = result.scalars().first()

    except SQLAlchemyError as e:
        # session.rollback()
        await logger.error(
            msg=f"SQLAlchemy error getting currently active conversation: {e}",
            user_id=user_id,
        )
        conversation = None

    except Exception as e:
        await logger.error(
            msg=f"Error getting currently active conversation for user_id {user_id}: {e}",
            chat_id=user_id,
        )
        conversation = None
    # finally:
    #     #session.close()
    return conversation


@manage_db_session
async def get_message_in_inactive_conversations_from_db(
    message_id: int, session: AsyncSession = None
) -> Message:
    d_logger.debug("D_logger")
    try:
        result = await session.execute(
            select(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .filter(Message.id == message_id, Conversation.is_active.is_(False))
        )
        message = result.scalars().first()
        return message
    except Exception as e:
        await logger.error(
            msg=f"Failed to retrieve message {message_id} from the database: {e}"
        )
        raise e


# TODO: naming: get, set, check
async def get_conversation_partner_id_from_db(
    user_id: int = 0,
    conversation: Optional[Conversation] = None,
    session: AsyncSession = None,
) -> int:
    d_logger.debug("D_logger")
    if not conversation:
        conversation = await get_currently_active_conversation_for_user_from_db(
            user_id=user_id, session=session
        )
        if not conversation:
            return None

    if conversation.user1_id == user_id:
        return conversation.user2_id
    elif conversation.user2_id == user_id:
        return conversation.user1_id
    else:
        return None


@manage_db_session
async def is_conversation_active(
    conversation_id: int, session: AsyncSession = None
) -> bool:
    d_logger.debug("D_logger")
    try:
        # Asynchronously query the conversation by ID
        result = await session.execute(
            select(Conversation).filter(Conversation.id == conversation_id)
        )
        conversation = result.scalars().first()
        # Return the is_active status if the conversation is found
        return conversation.is_active if conversation else False
    except SQLAlchemyError as e:
        logger.sync_error(
            msg=f"SQLAlchemy error checking if conversation is active: {e}"
        )
    except Exception as e:
        logger.sync_error(msg=f"Error checking if conversation is active: {e}")
        raise e


@manage_db_session
async def set_conversation_inactive(
    conversation_id: int, session: AsyncSession = None
) -> None:
    d_logger.debug("D_logger")
    try:
        result = await session.execute(
            select(Conversation).filter(Conversation.id == conversation_id)
        )
        conversation = result.scalars().first()
        if conversation:
            conversation.is_active = False
            conversation.end_time = datetime.now()
            # session.commit()
        else:
            raise ValueError(f"No conversation found with ID {conversation_id}")
    except SQLAlchemyError as e:
        logger.sync_error(msg=f"SQLAlchemy error setting conversation inactive: {e}")
        raise e
    except Exception as e:
        logger.sync_error(msg=f"Error setting conversation inactive: {e}")
        raise e
        # finally:
        #     #session.close()


@manage_db_session
async def get_new_partner_for_conversation_for_user_from_db(
    user_id: int, session: AsyncSession = None
) -> User | None:
    # d_logger.debug("D_logger")
    # subquery1 = select(Conversation.user1_id).filter(Conversation.user1_id == user_id)
    # subquery2 = select(Conversation.user2_id).filter(Conversation.user2_id == user_id)
    # subquery = subquery1.union(subquery2)

    # try:
    #     result = await session.execute(
    #         select(User).filter(
    #             User.is_ready_to_chat.is_(True),
    #             User.id != user_id,
    #             ~User.id.in_(subquery),
    #         )
    #     )
    #     potential_partners = result.scalars().all()

    #     if potential_partners:
    #         partner = random.choice(potential_partners)
    #         return partner
    #     else:
    #         return None
    # except SQLAlchemyError as e:
    #     await logger.error(
    #         msg=f"SQLAlchemy error getting new partner for conversation: {e}",
    #         chat_id=user_id,
    #     )
    #     raise e
    # except Exception as e:
    #     await logger.error(
    #         msg=f"Error getting new partner for conversation: {e}", chat_id=user_id
    #     )
    #     raise e
    d_logger.debug("D_logger")
    # Query to find all user IDs with whom the current user has had a conversation
    subquery = select(Conversation.user2_id).where(Conversation.user1_id == user_id)
    subquery = subquery.union(select(Conversation.user1_id).where(Conversation.user2_id == user_id))

    try:
        # Get all users who are ready to chat and have not had a conversation with the current user
        result = await session.execute(
            select(User).filter(
                User.is_ready_to_chat.is_(True),
                User.id != user_id,
                ~User.id.in_(subquery),
            )
        )
        potential_partners = result.scalars().all()

        if potential_partners:
            partner = random.choice(potential_partners)
            return partner
        else:
            return None
    except SQLAlchemyError as e:
        await logger.error(
            msg=f"SQLAlchemy error getting new partner for conversation: {e}",
            chat_id=user_id,
        )
        raise e
    except Exception as e:
        await logger.error(
            msg=f"Error getting new partner for conversation: {e}", chat_id=user_id
        )
        raise e


@manage_db_session
async def get_user_is_active_status_from_db(
    user_id: int, session: AsyncSession = None
) -> bool:
    d_logger.debug("D_logger")
    try:
        result = await session.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        return user.is_active if user else False
    except SQLAlchemyError as e:
        await logger.error(
            msg=f"SQLAlchemy error getting user active status: {e}", chat_id=user_id
        )
        return False


@manage_db_session
async def set_user_profile_version_in_db(
    user_id: int, profile_version: int, session: AsyncSession = None
) -> bool:
    d_logger.debug("D_logger")
    try:
        # Asynchronously get the user by ID
        result = await session.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()

        if user:
            # Set the new profile version
            user.profile_version = profile_version

            # Commit the changes
            await session.commit()
            return True
        else:
            # No user found, nothing to update
            return False
    except SQLAlchemyError as e:
        await logger.error(
            msg=f"SQLAlchemy error setting user profile version: {e}", chat_id=user_id
        )
        return False
    except Exception as e:
        await logger.error(
            msg=f"Unexpected error setting user profile version: {e}", chat_id=user_id
        )
        raise e


@manage_db_session
async def create_new_conversation_for_users_in_db(
    user_id: int,
    user_profile_version: int,
    partner_id: int,
    partner_profile_version: int,
    session: AsyncSession = None,
) -> Conversation | None:
    d_logger.debug("D_logger")
    try:
        # Create a new Conversation instance
        conversation = Conversation(
            user1_id=user_id,
            user1_profile_version=user_profile_version,
            user2_id=partner_id,
            user2_profile_version=partner_profile_version,
            start_time=datetime.now(),
            is_active=True,
        )
        session.add(conversation)
        await session.commit()  # Commit the changes

        # Return the new conversation ID
        return conversation
    except SQLAlchemyError as e:
        await session.rollback()  # Rollback in case of an exception
        await logger.error(
            msg=f"SQLAlchemy error creating new conversation: {e}", chat_id=user_id
        )
        raise e


@manage_db_session
async def get_tiered_profile_message_from_db(
    user_id: int = -1,
    tier: int = -1,
    profile_version: int = -1,
    session: AsyncSession = None,
) -> Message:
    d_logger.debug("D_logger")
    try:
        result = await session.execute(
            select(Message)
            .filter(
                Message.user_id == user_id,
                Message.tier == tier,
                Message.user_profile_version == profile_version,
            )
            .order_by(Message.timestamp.desc())
        )
        tiered_message = result.scalars().first()
        return tiered_message
    except SQLAlchemyError as e:
        await logger.error(msg=f"SQLAlchemy error getting tiered profile message: {e}")
        raise e
    except Exception as e:
        await logger.error(msg=f"Error getting tiered profile message: {e}")
        raise e


@manage_db_session
async def save_user_to_db(user: User = None, session: AsyncSession = None) -> bool:
    d_logger.debug("D_logger")
    try:
        session.add(user)
        await session.commit()
        return True
    except SQLAlchemyError as e:
        await logger.error(msg=f"SQLAlchemy error saving user: {e}")
        raise e


@manage_db_session
async def get_user_from_db(user_id: int = -1, session: AsyncSession = None) -> User:
    d_logger.debug("D_logger")
    try:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()
        return user
    except SQLAlchemyError as e:
        await logger.error(msg=f"SQLAlchemy error getting user: {e}")
        raise


@manage_db_session
async def set_is_active_flag_for_user_in_db(
    user_id: int, is_active: bool, session: AsyncSession
) -> bool:
    d_logger.debug("D_logger")
    try:
        result = await session.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if user:
            user.is_active = is_active
            await session.commit()
            return True
        else:
            return False
    except Exception as e:
        await session.rollback()
        raise e


@manage_db_session
async def set_is_ready_to_chat_flag_for_user_in_db(
    user_id: int, is_ready_to_chat: bool, session: AsyncSession = None
) -> bool:
    d_logger.debug("D_logger")
    try:
        result = await session.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if user:
            user.is_ready_to_chat = is_ready_to_chat
            await session.commit()
            return True
        else:
            raise ValueError(
                f"No user found with ID during set_is_ready_to_chat_flag_for_user_in_db: {user_id}"
            )
    except SQLAlchemyError as e:
        await session.rollback()
        await logger.error(
            msg=f"SQLAlchemy error during set_is_ready_to_chat_flag_for_user_in_db: {e}",
            chat_id=user_id,
        )
        return False
    except Exception as e:
        await session.rollback()
        await logger.error(
            msg=f"Error during set_is_ready_to_chat_flag_for_user_in_db: {e}",
            chat_id=user_id,
        )
        raise e


@manage_db_session
async def mark_user_as_inactive_in_db(user_id: int, session: AsyncSession) -> bool:
    d_logger.debug("D_logger")
    user = await get_user_from_db(user_id)
    if not user:
        return False
    else:
        if not user.is_active:
            return False
        await set_is_active_flag_for_user_in_db(
            user_id=user_id, is_active=False, session=session
        )
        return True


@manage_db_session
async def delete_user_profile_from_db(user_id: int, session: AsyncSession) -> bool:
    d_logger.debug("D_logger")
    try:
        result = await session.execute(select(User).filter_by(id=user_id))
        user_profile = result.scalars().first()

        if user_profile:
            # If user profile exists, delete it
            await session.delete(user_profile)
            await session.commit()
            return True
        else:
            return False
    except Exception as e:
        await logger.error(msg=f"Unregistration failed: {str(e)}", chat_id=user_id)
        raise e


@manage_db_session
async def get_max_profile_version_of_user_from_db(
    user_id: int, session: AsyncSession = None
) -> int:
    d_logger.debug("D_logger")
    try:
        max_user1_profile_version_stmt = select(
            func.max(Conversation.user1_profile_version)
        ).where(Conversation.user1_id == user_id)
        max_user1_profile_version_result = await session.execute(
            max_user1_profile_version_stmt
        )
        max_user1_profile_version = max_user1_profile_version_result.scalar() or 0

        max_user2_profile_version_stmt = select(
            func.max(Conversation.user2_profile_version)
        ).where(Conversation.user2_id == user_id)
        max_user2_profile_version_result = await session.execute(
            max_user2_profile_version_stmt
        )
        max_user2_profile_version = max_user2_profile_version_result.scalar() or 0

        user_profile_version_stmt = select(User.profile_version).where(
            User.id == user_id
        )
        user_profile_version_result = await session.execute(user_profile_version_stmt)
        user_profile_version = user_profile_version_result.scalar() or 0

        profile_version = max(
            max_user1_profile_version, max_user2_profile_version, user_profile_version
        )

        return profile_version
    except SQLAlchemyError as e:
        await logger.error(
            msg=f"SQLAlchemy error getting max profile version: {e}", chat_id=user_id
        )
        raise e


@manage_db_session
async def save_file_and_store_path_in_db(
    file_id: str, file_type: str, session: AsyncSession
) -> str:
    d_logger.debug("D_logger")
    try:
        # Get the file path from Telegram
        file = get_telegram_file(file_id=file_id)
        file_path = file.file_path

        # Define the directory to save files based on their type
        save_directory = f"saved_files/{file_type}"
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Full path where the file will be saved
        save_path = os.path.join(save_directory, file_id)

        # Download and save the file
        await download_telegram_file(file_path, save_path)

        # Return the path where the file was saved
        return save_path

    except Exception as e:
        logger.sync_error(msg=f"Error saving file: {e}")
        await session.rollback()


@manage_db_session
async def set_telegram_ids_for_stored_message(
    message_id: int = -1,
    tg_message_id_for_receiver: int = None,
    tg_message_id_for_sender: int = None,
    session: AsyncSession = None,
) -> bool:
    d_logger.debug("D_logger")
    try:
        result = await session.execute(select(Message).filter(Message.id == message_id))
        message =  result.scalars().first()
        if message:
            if tg_message_id_for_receiver is not None:
                message.tg_message_id_for_receiver = tg_message_id_for_receiver
            if tg_message_id_for_sender is not None:
                message.tg_message_id_for_sender = tg_message_id_for_sender

            return True
        else:
            raise ValueError(
                f"No message found with ID during set_telegram_ids_for_stored_message: {message_id}"
            )
    except SQLAlchemyError as e:
        session.rollback()
        logger.sync_error(
            msg=f"SQLAlchemy error during set_telegram_ids_for_stored_message: {e}"
        )
    except Exception as e:
        logger.sync_error(msg=f"Error during set_telegram_ids_for_stored_message: {e}")
        session.rollback()
    return False
