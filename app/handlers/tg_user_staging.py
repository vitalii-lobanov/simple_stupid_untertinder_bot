from database.engine import SessionLocal
from aiogram import types
from utils.debug import logger
from models.message import Message


#TODO: move this function to the service
#TODO: combine this function with send_telegram_message!!!
async def send_tiered_message_to_user(bot_instance, user_id: int, partner_id, tier: int):
    session = SessionLocal()
    try:
        # Query for the message of the given tier
        tiered_message = session.query(Message).filter_by(user_id=partner_id, tier=tier).first()
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
            # if tiered_message.sticker is not None:
            #     await bot_instance.send_sticker(user_id, sticker=tiered_message.sticker)
                
            if tiered_message.sticker is not None:
                if tiered_message.original_sender_id is not None:
                    message_text = f"Forwarded from @{tiered_message.original_sender_username}"
                    await bot_instance.send_message(chat_id=user_id, text=message_text)
                await bot_instance.send_sticker(user_id, sticker=tiered_message.sticker)    

            if tiered_message.poll is not None:
                await bot_instance.send_poll(user_id, **tiered_message.poll)  # Assuming poll is a dict with poll options

            # If there's a media group, send it
            if media_group:
                await bot_instance.send_media_group(user_id, media_group)           
            elif tiered_message.photo is not None:
                await bot_instance.send_photo(user_id, photo=tiered_message.photo, caption=caption)
            elif tiered_message.video is not None:
                    await bot_instance.send_video(user_id, video=tiered_message.video, caption=caption)
            elif tiered_message.document is not None:
                message_caption = tiered_message.caption
                if tiered_message.original_sender_id is not None:
                    message_caption = f"Forwarded from @{tiered_message.original_sender_username}\n\n{message_caption}"
                await bot_instance.send_document(user_id, document=tiered_message.document, caption=message_caption)
                    
#                    await bot_instance.send_document(user_id, document=tiered_message.document, caption=caption)                        
            elif tiered_message.text:
                #We send forwarded message
                if tiered_message.original_sender_id is not None:
                    message_text = f"Forwarded from @{tiered_message.original_sender_username}\n\n{tiered_message.text}"
                    await bot_instance.send_message(
                        chat_id=user_id,
                        text=message_text,
                        entities=tiered_message.entities  
                    )
                else:
                    
                    await bot_instance.send_message(
                        chat_id=user_id,
                        text=tiered_message.text,
                        entities=tiered_message.entities  
                )

        else:
            await bot_instance.send_message(user_id, "No message found for the specified tier.")
    except Exception as e:
        await logger.error(msg=f"Failed to send {user_id}'s tiered message to user {partner_id}: {e}")
    finally:
        session.close()
