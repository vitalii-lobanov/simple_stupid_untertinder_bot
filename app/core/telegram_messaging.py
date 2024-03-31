# TODO: move contents of service_message_sender.py to here

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from utils.text_messages import message_this_is_bot_message
from aiogram import types
from core.bot import bot_instance
from sqlalchemy.orm import Session
from database.engine import get_session
# from app.tasks.tasks import celery_app
from models import Message
from utils.debug import logger
import bleach
from database.engine import manage_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from services.serializing_helpers import extract_file_id_from_path
from utils.text_messages import message_this_message_is_forwarded
from services.dao import (
    get_tiered_profile_message_from_db,
    get_max_profile_version_of_user_from_db,
)
from services.serializing_helpers import message_entities_to_dict


async def send_reconstructed_telegram_message_to_user(
    message: Message = None, 
    user_id: int = -1
) -> None:
    
    caption = None

    if message is not None:

        if message.original_sender_id is not None:
            caption = message_this_message_is_forwarded(
                original_sender_username=message.original_sender_username,
                message_text=message.text,
            )

            #message_text = message_this_message_is_forwarded(
            #     original_sender_username=message.original_sender_username,
            #     message_text=message.text,
            # )
            # if message.caption is not None:
            #     caption = message_this_message_is_forwarded(
            #         original_sender_username=message.original_sender_username,
            #         message_text=message.caption + "\n\n" + message.text,
            #     )
            # else:
            #     caption = message.caption

        media_group = []
        if message.audio is not None:
            media_group.append(
                types.InputMediaAudio(media=extract_file_id_from_path(message.audio), caption=caption or None)
            )
        if message.video is not None:
            media_group.append(
                types.InputMediaVideo(media=extract_file_id_from_path(message.video), caption=caption or None)
            )
        if message.photo is not None:
            media_group.append(
                types.InputMediaPhoto(media=extract_file_id_from_path(message.photo), caption=caption or None)
            )
        if message.voice is not None:
            media_group.append(
                types.InputMediaAudio(media=extract_file_id_from_path(message.voice), caption=caption or None)
            )

        if message.video_note is not None:
            media_group.append(
                types.InputMediaVideo(media=extract_file_id_from_path(message.video_note), caption=caption or None)
            ) 

        # Handle non-media types separately
        # These types cannot be part of a media group and should be sent as separate messages
        if message.sticker is not None:
            await bot_instance.send_sticker(user_id, sticker=message.sticker)


        # We do not need to process animationn separately, it can be handled as a document
        # if message.animation is not None:
        #     await bot_instance.send_animation(user_id, animation=message.animation)

        if message.location is not None:
            await bot_instance.send_location(
                user_id,
                latitude=message.location['latitude'],
                longitude=message.location['longitude'],
            )

        if message.poll is not None:
            await bot_instance.send_poll(
                user_id,
                question=message.poll['question'],
                options=[option['text'] for option in message.poll['options']],
                is_anonymous=message.poll['is_anonymous'],
                allows_multiple_answers=message.poll['allows_multiple_answers'],
                is_closed=message.poll['is_closed'],
                explanation=message.poll['explanation'],
                explanation_entities=message_entities_to_dict(message.poll['explanation_entities']),
                open_period=message.poll['open_period'],
                close_date=message.poll['close_date'],
                # Add any other relevant fields required for sending a poll
        )    

        # If there's a media group or other attachments, send them
        if media_group:
            await bot_instance.send_media_group(user_id, media_group)
        elif message.photo is not None:
            await bot_instance.send_photo(user_id, photo=extract_file_id_from_path(message.photo), caption=caption)
        elif message.video is not None:
            await bot_instance.send_video(user_id, video=extract_file_id_from_path(message.video), caption=caption)
        elif message.document is not None:
            await bot_instance.send_document(
                user_id, document=extract_file_id_from_path(message.document), caption=caption
            )
        # If there is only text, send it
        elif message.text is not None:            
            if caption is not None:
                text = caption
            else:
                text = message.text
            await bot_instance.send_message(
                chat_id=user_id, text=text,  entities=message.entities
            )


async def send_service_message(message: str, state: FSMContext = None, chat_id: int = None
) -> None:
    if state is not None:
        tg_chat_id = state.key.chat_id
    elif chat_id is not None:
        tg_chat_id = chat_id
    else:
        tg_chat_id = None
        raise ValueError("Either state or chat_id must be provided")
    msg = f"{message_this_is_bot_message()}{message}"
    msg = bleach.clean(msg)
    await bot_instance.send_message(chat_id=tg_chat_id, text=msg, parse_mode="HTML")


@manage_db_session
async def send_tiered_partner_s_message_to_user(        
    user_id: int = 0,
    partner_id: int = 0,
    tier: int = -1,
    session: AsyncSession = None,
) -> None:
    try:        
        current_partner_profile_version = await get_max_profile_version_of_user_from_db(
            user_id=partner_id
        )
        #TODO: WTF? How id related to current_partner_profile_version???
        if current_partner_profile_version == 0:
            id = user_id            
        else:
            id = partner_id
        profile_version = current_partner_profile_version
        
        tiered_message = await get_tiered_profile_message_from_db(
            session=session,
            user_id=id,
            tier=tier,
            profile_version=profile_version,            
        )

        await send_reconstructed_telegram_message_to_user(
            message=tiered_message, user_id=partner_id
        )
    except Exception as e:
        logger.sync_error(msg=f"Error sending tiered profile message: {e}")
        raise e
