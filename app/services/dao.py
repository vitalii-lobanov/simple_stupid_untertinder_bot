import random
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from aiogram import types
from database.engine import SessionLocal
from models import Conversation, ProfileData
from models.base import MessageSource
from models.message import Message
from models.reaction import Reaction
from models.user import User
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from utils.debug import logger


def __message_entities_to_dict__(
    entities: List[types.MessageEntity],
) -> Optional[List[Dict[str, Union[str, int, Optional[Dict[str, Any]]]]]]:
    return (
        [
            {
                "type": entity.type,
                "offset": entity.offset,
                "length": entity.length,
                "url": entity.url,
                "user": entity.user.to_dict() if entity.user else None,
                "language": entity.language,
            }
            for entity in entities
        ]
        if entities
        else None
    )


def __link_preview_options_to_dict__(
    link_preview_options: Optional[types.LinkPreviewOptions],
) -> Optional[Dict[str, Union[bool, str, None]]]:
    if link_preview_options is not None:
        is_disabled = (
            link_preview_options.is_disabled
            if isinstance(link_preview_options.is_disabled, bool)
            else False
        )
        return {
            "is_disabled": is_disabled,
            "url": link_preview_options.url
            if isinstance(link_preview_options.url, str)
            else None,
        }
    return None


22

# TODO: handle other media types. Especially message_source (enum from base(?))


async def save_telegram_message(
    message: types.Message,
    message_source: MessageSource = None,
    tier: int = -1,
    conversation_id: int = None,
) -> Message:
    user_id = message.from_user.id
    message_id = message.message_id
    session = SessionLocal()
    photo = None

    # Extract the file ID of the largest photo
    if message.photo:
        photo = message.photo[
            -1
        ].file_id  # Get the file_id of the last (largest) photo size

    try:
        new_message = Message(
            user_id=user_id,
            tier=tier,
            message_source=message_source,
            message_id=message_id,
            conversation_id=conversation_id,
            text=message.text or None,
            audio=message.audio.file_id if message.audio else None,
            video=message.video.file_id if message.video else None,
            document=message.document.file_id if message.document else None,
            animation=message.animation.file_id if message.animation else None,
            sticker=message.sticker.file_id if message.sticker else None,
            author_signature=message.author_signature
            if message.author_signature
            else None,
            caption=message.caption if message.caption else None,
            # caption_entities=message.caption_entities if message.caption_entities else None,
            # entities=message.entities if message.entities else None,
            caption_entities=__message_entities_to_dict__(message.caption_entities)
            if message.caption_entities
            else None,
            entities=__message_entities_to_dict__(message.entities)
            if message.entities
            else None,
            contact=message.contact if message.contact else None,
            forward_date=message.forward_date if message.forward_date else None,
            from_user=str(message.from_user).encode() if message.from_user else None,
            game=message.game if message.game else None,
            dice=message.dice if message.dice else None,
            html_text=message.html_text if message.html_text else None,
            invoice=message.invoice if message.invoice else None,
            location=message.location if message.location else None,
            link_preview_options=__link_preview_options_to_dict__(
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
            photo=photo if photo else None,
            poll=message.poll if message.poll else None,
            quote=message.quote if message.quote else None,
            story=message.story if message.story else None,
            voice=message.voice if message.voice else None,
            video_note=message.video_note if message.video_note else None,
            sender_in_conversation_id=message.from_user.id
            if message.from_user
            else None,
        )
        session.add(new_message)
        session.commit()
    except Exception as e:
        session.rollback()
        await logger.error(msg=f"Failed to save message: {e}", chat_id=user_id)
    finally:
        session.close()

    if message_source == MessageSource.registration_profile:
        profile_data = ProfileData(user_id=user_id, message_id=message_id)
        session = SessionLocal()
        try:
            session.add(profile_data)
            session.commit()
        except Exception as e:
            session.rollback()
            # Assuming you have a logger configured
            await logger.error(msg=f"Failed to save profile data: {e}", chat_id=user_id)
        finally:
            session.close()

    return new_message


async def save_tiered_registration_message(
    message: types.Message, message_count: int
) -> None:
    tier = message_count - 1
    message_source = MessageSource.registration_profile
    await save_telegram_message(message, message_source, tier)


async def save_telegram_reaction(
    user_id: int,
    new_emoji: str,
    old_emoji: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    receiver_message_id: Optional[int] = None,
    message_id: int = None,
    rank: int = 0,
) -> bool:
    try:
        # Create a new database session
        session = SessionLocal()

        # Create a new Reaction instance
        reaction = Reaction(
            user_id=user_id,
            message_id=message_id,
            new_emoji=new_emoji,
            old_emoji=old_emoji,
            timestamp=timestamp,
            receiver_message_id=receiver_message_id,
            rank=rank,
        )

        # Add the new reaction to the session and commit
        session.add(reaction)
        session.commit()
        logger.sync_debug(f"Reaction saved: {reaction.id}")
        return True

    except SQLAlchemyError as e:
        # Handle any database errors
        await logger.error(
            msg=f"SQLAlchemy error saving reaction: {e}", chat_id=user_id
        )
        session.rollback()
        raise
    except Exception as e:
        # Handle any other exceptions
        await logger.error(msg=f"Error saving reaction: {e}", chat_id=user_id)
        session.rollback()
        raise
    finally:
        # Close the session
        session.close()


async def get_message_for_given_conversation_from_db(
    message_id: int, conversation_id: int
) -> Message:
    session = SessionLocal()

    # TODO: check if this is correct, very dirty hack
    id_to_find = message_id - 1

    # TODO: check if this is correct, very dirty hack
    # TODO: if correct, create a separate function for this
    message = (
        session.query(Message)
        .filter_by(message_id=id_to_find, conversation_id=conversation_id)
        .first()
        or session.query(Message)
        .filter_by(message_id=message_id, conversation_id=conversation_id)
        .first()
    )
    session.close()

    # Return the sender_in_conversation_id if the message is found
    if message:
        return message
    else:
        # Handle the case where the message is not found, e.g., return None or raise an exception
        # raise SQLAlchemyError(f"Failed to find the message {message_id} in the database for {conversation_id} conversation.")
        return None


async def get_currently_active_conversation_for_user_from_db(
    user_id: int,
) -> Conversation:
    session = SessionLocal()
    try:
        conversation = (
            session.query(Conversation)
            .filter(
                (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id),
                Conversation.is_active is True,
            )
            .first()
        )
    except SQLAlchemyError as e:
        session.rollback()
        await logger.error(
            msg=f"SQLAlchemy error getting currently active conversation: {e}",
            user_id=user_id,
        )
        conversation = None
    finally:
        session.close()
        return conversation


# TODO: make all these __db__ functions async
def get_message_in_inactive_conversations_from_db(message_id: int) -> Message:
    session = SessionLocal()
    message = (
        session.query(Message)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .filter(Message.id == message_id, Conversation.is_active is False)
        .first()
    )
    session.close()
    return message


# TODO: naming: get, set, check
async def get_conversation_partner_id_from_db(user_id: int = 0) -> int:
    conversation = await get_currently_active_conversation_for_user_from_db(
        user_id=user_id
    )
    if not conversation:
        return None
    partner_id = (
        conversation.user2_id
        if conversation.user1_id == user_id
        else conversation.user1_id
    )
    return partner_id


async def is_conversation_active(conversation_id: int) -> bool:
    session = SessionLocal()
    try:
        # Query the conversation by ID
        conversation = (
            session.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )
        # Return the is_active status if the conversation is found
        return conversation.is_active if conversation else False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


async def set_conversation_inactive(conversation_id: int) -> None:
    session = SessionLocal()
    try:
        conversation = (
            session.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )
        if conversation:
            conversation.is_active = False
            session.commit()
        else:
            raise ValueError(f"No conversation found with ID {conversation_id}")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# TODO: externalize database work in dao.py


async def get_new_partner_for_conversation_for_user_from_db(user_id):
    session = SessionLocal()
    # Step 1: Find a chat partner
    # Query for users who are ready to chat and whom the current user has never chatted with before
    potential_partners = (
        session.query(User)
        .filter(
            User.is_ready_to_chat is True,
            User.id != user_id,  # Exclude the current user from the results
            ~session.query(Conversation)
            .filter(
                (Conversation.user1_id == user_id) & (Conversation.user2_id == User.id)
                | (Conversation.user2_id == user_id)
                & (Conversation.user1_id == User.id)
            )
            .exists(),
        )
        .all()
    )

    session.close()
    # Step 2: Choose a chat partner
    if potential_partners:
        partner = random.choice(potential_partners)
        return partner
    else:
        return None


async def create_new_conversation_for_users_in_db(
    user_id: int,
    user_profile_version: int,
    partner_id: int,
    patner_profile_version: int,
) -> Conversation:
    session = SessionLocal()
    conversation = None
    try:
        conversation = Conversation(
            user1_id=user_id,
            user2_id=partner_id,
            start_time=datetime.now(),
            is_active=True,
        )
        session.add(conversation)
        session.commit()

    except SQLAlchemyError as e:
        session.rollback()
        await logger.error(
            msg=f"SQLAlchemy error creating new conversation: {e}", chat_id=user_id
        )
        await logger.error(
            msg=f"SQLAlchemy error creating new conversation: {e}", chat_id=partner_id
        )
        raise e
    finally:
        session.close()
        return conversation


async def get_tiered_profile_message_from_db(
    user_id: int = -1, tier: int = -1, profile_version: int = -1
) -> Message:
    session = SessionLocal()
    try:
        # Query for the message of the given tier
        tiered_message = (
            session.query(Message)
            .filter_by(user_id=user_id, tier=tier, profile_version=profile_version)
            .first()
        )
    except SQLAlchemyError as e:
        session.rollback()
        await logger.error(msg=f"SQLAlchemy error getting tiered profile message: {e}")
        raise e
    except Exception as e:
        session.rollback()
        await logger.error(msg=f"Error getting tiered profile message: {e}")
        raise e
    finally:
        session.close()
    return tiered_message if tiered_message else None


async def save_user_to_db(user: User):
    session = SessionLocal()
    try:
        session.add(user)
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        await logger.error(msg=f"SQLAlchemy error saving user: {e}")
        raise e
    finally:
        session.close()
    return True


async def get_user_from_db(user_id: int) -> User:
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
    except SQLAlchemyError as e:
        session.rollback()
        await logger.error(msg=f"SQLAlchemy error getting user: {e}")
        raise e
    finally:
        session.close()
    return user if user else None


async def set_is_active_flag_for_user_in_db(user_id: int, is_active: bool) -> bool:
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = is_active
            session.commit()
        else:
            raise ValueError(
                f"No user found with ID during set_is_active_flag_for_user_in_db: {user_id}"
            )
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    return True


# TODO: implement all exception hangling like here:
async def set_is_ready_to_chat_flag_for_user_in_db(
    user_id: int, is_ready_to_chat: bool
) -> bool:
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.is_ready_to_chat = is_ready_to_chat
            session.commit()
        else:
            raise ValueError(
                f"No user found with ID during set_is_ready_to_chat_flag_for_user_in_db: {user_id}"
            )
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    return True


# TODO: implement versioning!
async def mark_user_as_inactive_in_db(user_id: int) -> bool:
    session = SessionLocal()
    try:
        existing_user = session.query(User).filter_by(id=user_id).first()
        if existing_user and existing_user.is_active:
            # Mark the user as inactive instead of deleting
            existing_user.is_active = False
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False
    except Exception as e:
        session.rollback()
        await logger.error(msg=f"Unregistration failed: {str(e)}", chat_id=user_id)
        raise e


# TODO: implement versioning!
async def delete_user_profile_from_db(user_id: int) -> bool:
    # Create a new database session
    session = SessionLocal()
    try:
        user_profile = session.query(User).filter_by(id=user_id).first()
        if user_profile:
            # TODO: add versioning
            session.delete(user_profile)
            session.commit()
            session.close()
            return True
        else:
            return False
    except Exception as e:
        session.rollback()
        session.close()
        await logger.error(msg=f"Unregistration failed: {str(e)}", chat_id=user_id)
        raise e


async def get_max_profile_version_of_user_from_db(user_id: int) -> int:
    session = SessionLocal()
    try:
        max_user1_profile_version = (
            session.query(func.max(Conversation.user1_profile_version))
            .filter(Conversation.user1_id == user_id)
            .scalar()
        )
        max_user2_profile_version = (
            session.query(func.max(Conversation.user2_profile_version))
            .filter(Conversation.user2_id == user_id)
            .scalar()
        )

        max_user1_profile_version = (
            max_user1_profile_version if max_user1_profile_version is not None else 0
        )
        max_user2_profile_version = (
            max_user2_profile_version if max_user2_profile_version is not None else 0
        )

        profile_version = max(max_user1_profile_version, max_user2_profile_version)

        return profile_version
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
