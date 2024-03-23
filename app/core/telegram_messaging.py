#TODO: move contents of service_message_sender.py to here

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from utils.text_messages import message_this_is_bot_message
import random
from datetime import datetime
from utils.text_messages import message_a_conversation_partner_found, message_you_now_connected_to_the_conversation_partner
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import ReactionTypeEmoji
from core.bot import bot_instance
from sqlalchemy.exc import SQLAlchemyError
# from app.tasks.tasks import celery_app
from database.engine import SessionLocal
from core.dispatcher import  dispatcher
from models import Conversation, Message
from models.user import User
from core.states import  CommonStates, UserStates
from utils.debug import logger
from services.dao import save_telegram_message, save_telegram_reaction
from models.message import MessageSource
from aiogram.methods.set_message_reaction import SetMessageReaction
from services.emoji_rank import EmojiRank
from services.score_tiers import message_tiers_count, profile_disclosure_tiers_score_levels


from utils.text_messages import message_this_is_bot_message, message_the_last_tier_reached
from services.dao import get_currently_active_conversation_for_user_from_db, get_message_for_given_conversation_from_db, get_message_in_inactive_conversations_from_db
from core.states import  access_user_context
from handlers.tg_commands import cmd_start_chatting
from core.states import  initialize_states_for_chatter_to_start_conversation
from core.states import  get_user_context
from services.dao import get_new_partner_for_conversation_for_user_from_db, create_new_conversation_for_users_in_db
from utils.text_messages import message_this_message_is_forwarded
from database.engine import SessionLocal
from aiogram import types
from utils.debug import logger
from models.message import Message
from services.dao import get_tiered_profile_message_from_db


async def send_reconstructed_telegram_message_to_user(message: Message = None, user_id: int = -1):  
        
    if message is not None:

        if message.original_sender_id is not None:
            message_text = message_this_message_is_forwarded(original_sender_username = message.original_sender_username, message_text = message.text)            
            if message.caption is not None:
                caption = message_this_message_is_forwarded(original_sender_username = message.original_sender_username, message_text = message.caption)           
            else:
                caption = message.caption       
        
        media_group = []
        if message.audio is not None:
            media_group.append(types.InputMediaAudio(media=message.audio, caption=caption or None))
        if message.video is not None:
            media_group.append(types.InputMediaVideo(media=message.video, caption=caption or None))
        if message.photo is not None:
            media_group.append(types.InputMediaPhoto(media=message.photo, caption=caption or None))
        if message.voice is not None:
            media_group.append(types.InputMediaAudio(media=message.voice, caption=caption or None))

        if message.animation is not None:
                media_group.append(types.InputMediaVideo(media=message.animation.decode("utf-8"), caption=caption or None))
        if message.video_note is not None:
            media_group.append(types.InputMediaVideo(media=message.video_note, caption=caption or None))  # Assuming video_note behaves like a video

        # Handle non-media types separately
        # These types cannot be part of a media group and should be sent as separate messages            
        if message.sticker is not None:
            await bot_instance.send_sticker(user_id, sticker=message.sticker)    

        #TODO: test polls
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
            await bot_instance.send_document(user_id, document=message.document, caption=caption)
        #If there is only text, send it    
        elif message.text is not None:
            await bot_instance.send_message(
                    chat_id=user_id,
                    text=message_text,
                    entities=message.entities  
                )
            
async def send_service_message(bot_instance: Bot, message: str, state: FSMContext = None, chat_id: int = None):
    if state is not None:
        tg_chat_id = state.key.chat_id
    elif chat_id is not None:
        tg_chat_id = chat_id
    else:
        tg_chat_id = None
        raise ValueError('Either state or chat_id must be provided')
    msg = f'{message_this_is_bot_message()}{message}'         
    await bot_instance.send_message(chat_id=tg_chat_id, text=msg, parse_mode='HTML')

async def send_tiered_parnter_s_message_to_user(bot_instance, user_id: int, partner_id, tier: int):

    try:
        # Query for the message of the given tier
        tiered_message = get_tiered_profile_message_from_db(user_id = partner_id, tier = tier)        
        await send_reconstructed_telegram_message_to_user(message = tiered_message, user_id = partner_id)
    except Exception as e:
        logger.sync_error(msg=f"Error sending tiered profile message: {e}")
        raise e
