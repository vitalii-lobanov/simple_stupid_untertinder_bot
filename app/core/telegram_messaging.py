# TODO: move contents of service_message_sender.py to here

from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from core.bot import bot_instance

# from app.tasks.tasks import celery_app
from models import Message
from services.dao import (
    get_max_profile_version_of_user_from_db,
    get_tiered_profile_message_from_db,
)
from utils.debug import logger
from utils.text_messages import (
    message_this_is_bot_message,
    message_this_message_is_forwarded,
)


async def send_reconstructed_telegram_message_to_user(
    message: Message, user_id: int
) -> None:
    if message is not None:
        if message.original_sender_id is not None:
            message_text = message_this_message_is_forwarded(
                original_sender_username=message.original_sender_username,
                message_text=message.text,
            )
            if message.caption is not None:
                caption = message_this_message_is_forwarded(
                    original_sender_username=message.original_sender_username,
                    message_text=message.caption,
                )
            else:
                caption = message.caption

        media_group = []
        if message.audio is not None:
            media_group.append(
                types.InputMediaAudio(media=message.audio, caption=caption or None)
            )
        if message.video is not None:
            media_group.append(
                types.InputMediaVideo(media=message.video, caption=caption or None)
            )
        if message.photo is not None:
            media_group.append(
                types.InputMediaPhoto(media=message.photo, caption=caption or None)
            )
        if message.voice is not None:
            media_group.append(
                types.InputMediaAudio(media=message.voice, caption=caption or None)
            )

        if message.animation is not None:
            media_group.append(
                types.InputMediaVideo(
                    media=message.animation.decode("utf-8"), caption=caption or None
                )
            )
        if message.video_note is not None:
            media_group.append(
                types.InputMediaVideo(media=message.video_note, caption=caption or None)
            )  # Assuming video_note behaves like a video

        # Handle non-media types separately
        # These types cannot be part of a media group and should be sent as separate messages
        if message.sticker is not None:
            await bot_instance.send_sticker(user_id, sticker=message.sticker)

        # TODO: test polls
        if message.poll is not None:
            await bot_instance.send_poll(user_id, **message.poll)

        # If there's a media group or other attachments, send them
        if media_group:
            await bot_instance.send_media_group(user_id, media_group)
        elif message.photo is not None:
            await bot_instance.send_photo(user_id, photo=message.photo, caption=caption)
        elif message.video is not None:
            await bot_instance.send_video(user_id, video=message.video, caption=caption)
        elif message.document is not None:
            await bot_instance.send_document(
                user_id, document=message.document, caption=caption
            )
        # If there is only text, send it
        elif message.text is not None:
            await bot_instance.send_message(
                chat_id=user_id, text=message_text, entities=message.entities
            )


async def send_service_message(
    bot_instance: Bot, message: str, state: FSMContext = None, chat_id: int = None
) -> None:
    if state is not None:
        tg_chat_id = state.key.chat_id
    elif chat_id is not None:
        tg_chat_id = chat_id
    else:
        tg_chat_id = None
        raise ValueError("Either state or chat_id must be provided")
    msg = f"{message_this_is_bot_message()}{message}"
    await bot_instance.send_message(chat_id=tg_chat_id, text=msg, parse_mode="HTML")


async def send_tiered_partner_s_message_to_user(
    user_id: int,
    partner_id: int,
    tier: int,
) -> None:
    try:
        current_partner_profile_version: int = (
            await get_max_profile_version_of_user_from_db(user_id=partner_id)
        )
        tiered_message: types.Message = await get_tiered_profile_message_from_db(
            user_id=partner_id,
            tier=tier,
            profile_version=current_partner_profile_version,
        )
        await send_reconstructed_telegram_message_to_user(
            message=tiered_message, user_id=user_id
        )
    except Exception as e:
        logger.sync_error(msg=f"Error sending tiered profile message: {e}")
        raise e
