from aiogram.fsm.context import FSMContext
from database.engine import SessionLocal
from states import RegistrationStates
from models.user import User
from aiogram import types
from states import CommonStates
from utils.debug import logger
from models import ProfileDataTieredMessage
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaDocument


async def send_tiered_message_to_user(bot_instance, user_id: int, tier: int):
    session = SessionLocal()
    try:
        # Query for the message of the given tier
        tiered_message = session.query(ProfileDataTieredMessage).filter_by(user_id=user_id, tier=tier).first()
        caption = tiered_message.caption
        if tiered_message:
            media_group = []
            if tiered_message.audio is not None:
                media_group.append(types.InputMediaAudio(media=tiered_message.audio, caption=caption or None))
            if tiered_message.video is not None:
                media_group.append(types.InputMediaVideo(media=tiered_message.video, caption=caption or None))
            if tiered_message.photo is not None:
                media_group.append(types.InputMediaPhoto(media=tiered_message.photo, caption=caption or None))
            if tiered_message.voice is not None:
                media_group.append(types.InputMediaAudio(media=tiered_message.voice, caption=caption or None))

            if tiered_message.animation is not None:
                 media_group.append(types.InputMediaVideo(media=tiered_message.animation.decode("utf-8"), caption=caption or None))
            if tiered_message.video_note is not None:
                media_group.append(types.InputMediaVideo(media=tiered_message.video_note, caption=caption or None))  # Assuming video_note behaves like a video

            # Handle non-media types separately
            # These types cannot be part of a media group and should be sent as separate messages
            if tiered_message.sticker is not None:
                await bot_instance.send_sticker(user_id, sticker=tiered_message.sticker)
            if tiered_message.poll is not None:
                await bot_instance.send_poll(user_id, **tiered_message.poll)  # Assuming poll is a dict with poll options

            # If there's a media group, send it
            if media_group:
                await bot_instance.send_media_group(user_id, media_group)
            elif tiered_message.document is not None:
                await bot_instance.send_document(user_id, document=tiered_message.document)
            elif tiered_message.text:
                # If there's only text, send a text message
                await bot_instance.send_message(user_id, tiered_message.text)

        else:
            await bot_instance.send_message(user_id, "No message found for the specified tier.")
    except Exception as e:
        logger.critical(f"Failed to send tiered message: {e}")
    finally:
        session.close()
