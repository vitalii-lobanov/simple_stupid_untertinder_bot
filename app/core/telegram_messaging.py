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
from utils.d_debug import d_logger
import bleach

from sqlalchemy.ext.asyncio import AsyncSession
from helpers.serializing_helpers import extract_file_id_from_path
from utils.text_messages import message_this_message_is_forwarded
from helpers.serializing_helpers import message_entities_to_dict

from utils.text_messages import message_media_group_not_supported
async def check_message_is_part_of_mediagroup_and_notify_user(message: types.Message) -> bool:
    if message.media_group_id:
        await bot_instance.delete_message(message.chat.id, message.message_id)
        await send_service_message(
            message=message_media_group_not_supported(),
            chat_id=message.chat.id,
        )
        return True
    else:
        return False
    
async def send_reconstructed_telegram_message_to_user(
    message: Message = None, 
    user_id: int = -1
) -> None:
    d_logger.debug("D_logger")
    caption = None

    if message is not None:

        if message.original_sender_id is not None:
            if message.caption is not None:
                msg_cpt = message.caption 
            else:
                msg_cpt = ""

            if message.text is not None:
                msg_txt = msg_cpt + message.text
            else:
                msg_txt = msg_cpt

            caption = message_this_message_is_forwarded(
                original_sender_username=message.original_sender_username,
                message_text=msg_txt,
            )

        else:
            caption = message.caption

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
            res_message = await bot_instance.send_sticker(user_id, sticker=message.sticker)


        # We do not need to process animationn separately, it can be handled as a document
       

        if message.location is not None:
            res_message = await bot_instance.send_location(
                user_id,
                latitude=message.location['latitude'],
                longitude=message.location['longitude'],
            )

        if message.poll is not None:
            res_message = await bot_instance.send_poll(
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
            res_message = await bot_instance.send_media_group(user_id, media_group)
        elif message.photo is not None:
            res_message = await bot_instance.send_photo(user_id, photo=extract_file_id_from_path(message.photo), caption=caption)
        elif message.video is not None:
            res_message = await bot_instance.send_video(user_id, video=extract_file_id_from_path(message.video), caption=caption)
        elif message.document is not None:
            res_message =  await bot_instance.send_document(
                user_id, document=extract_file_id_from_path(message.document), caption=caption
            )
        # If there is only text, send it
        elif message.text is not None:            
            if caption is not None:
                text = caption
            else:
                text = message.text
            res_message = await bot_instance.send_message(
                chat_id=user_id, text=text,  entities=message.entities
            )

        return res_message


async def send_service_message(message: str, state: FSMContext = None, chat_id: int = None
) -> None:
    d_logger.debug("D_logger")
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

async def reply_to_telegram_message(message: types.Message, text: str) -> None:
    d_logger.debug("D_logger")
    await message.reply(text)