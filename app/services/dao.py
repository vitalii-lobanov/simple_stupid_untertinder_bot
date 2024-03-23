from database.engine import SessionLocal
from aiogram import types
from utils.debug import logger
from models.message import Message
from models.base import MessageSource
from models.reaction import Reaction
from sqlalchemy.exc import SQLAlchemyError
from models import ProfileData
from models import Conversation, Message


def message_entities_to_dict(entities):
    return [
        {
            'type': entity.type,
            'offset': entity.offset,
            'length': entity.length,
            'url': entity.url,
            'user': entity.user.to_dict() if entity.user else None,
            'language': entity.language,          
        }
        for entity in entities
    ] if entities else None

def link_preview_options_to_dict(link_preview_options):
    if link_preview_options is not None:
        # Ensure that is_disabled is assigned a boolean value, not an instance of `Default`
        is_disabled = link_preview_options.is_disabled if isinstance(link_preview_options.is_disabled, bool) else False
        # Ensure that all other fields are also handled similarly and assigned non-Default values
        return {
            'is_disabled': is_disabled,
            'url': link_preview_options.url if isinstance(link_preview_options.url, str) else None,
            # ... include other fields that you want to store, with similar checks
        }
    return 



#TODO: handle other media types. Especially message_source (enum from base(?))

async def save_telegram_message(message: types.Message, message_source: MessageSource = None, tier: int = -1, conversation_id: int = None):
    user_id = message.from_user.id
    message_id = message.message_id
    session = SessionLocal()
    photo = None
    video = None

    # Extract the file ID of the largest photo
    if message.photo:
        photo = message.photo[-1].file_id  # Get the file_id of the last (largest) photo size

    try:
        new_message = Message(
            user_id=user_id,
            tier=tier,
            message_source=message_source,
            message_id=message_id,
            conversation_id=conversation_id,
            text=message.text or None,
            audio=message.audio.file_id if message.audio else None,
            video= message.video.file_id if message.video else None, 
            document=message.document.file_id if message.document else None,
            animation=message.animation.file_id if message.animation else None,
            sticker=message.sticker.file_id if message.sticker else None,
            author_signature=message.author_signature if message.author_signature else None,
            caption=message.caption if message.caption else None,
            #caption_entities=message.caption_entities if message.caption_entities else None,
            #entities=message.entities if message.entities else None,
            caption_entities=message_entities_to_dict(message.caption_entities) if message.caption_entities else None,
            entities=message_entities_to_dict(message.entities) if message.entities else None,
            contact=message.contact if message.contact else None,
            forward_date=message.forward_date if message.forward_date else None,
            from_user= str(message.from_user).encode() if message.from_user else None,
            game=message.game if message.game else None,
            dice=message.dice if message.dice else None,
            html_text=message.html_text if  message.html_text else None,
            invoice=message.invoice if message.invoice else None,
            location=message.location if message.location else None,
            link_preview_options=link_preview_options_to_dict(message.link_preview_options) if message.link_preview_options else None,
            md_text=message.md_text if message.md_text else None,
            media_group_id=message.media_group_id if message.media_group_id else None,
            original_sender_id=message.forward_from.id if message.forward_from else None,
            original_sender_username=message.forward_from.username if message.forward_from else None,
            photo=photo if photo else None, 
            poll=message.poll  if message.poll else None,
            quote=message.quote if message.quote else None,          
            story=message.story if message.story else None,
            voice=message.voice if message.voice else None,
            video_note=message.video_note if message.video_note else None,
            sender_in_conversation_id = message.from_user.id if message.from_user else None,
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
            await logger.error(msg = f"Failed to save profile data: {e}", chat_id=user_id)
        finally:
            session.close()

        


async def save_tiered_registration_message(message: types.Message, message_count: int):
    tier = message_count - 1
    message_source = MessageSource.registration_profile
    await save_telegram_message(message, message_source, tier)


async def save_telegram_reaction(user_id, new_emoji, old_emoji=None, timestamp=None, receiver_message_id=None, message_id=None, rank=0):
    try:
        # Create a new database session
        session = SessionLocal()
        
        # Create a new Reaction instance
        reaction = Reaction(
            user_id=user_id,
            message_id=message_id,
            #sender_message_id=sender_message_id,
            new_emoji=new_emoji,
            old_emoji=old_emoji,
            timestamp=timestamp,
            receiver_message_id=receiver_message_id,
            rank = rank,
        )
        
        # Add the new reaction to the session and commit
        session.add(reaction)
        session.commit()
        logger.sync_debug(f"Reaction saved: {reaction.id}")
        return True
        # Return the created reaction
        return reaction
    except SQLAlchemyError as e:
        # Handle any database errors
        await logger.error(msg=f"SQLAlchemy error saving reaction: {e}", chat_id=user_id)
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

#TODO: check session.close() for all the open sessions

#TODO: move all the __db__ functions to .services or .database
def get_message_for_given_conversation_from_db(message_id: int, conversation_id: int) -> Message:
    session = SessionLocal()   

    #TODO: check if this is correct, very dirty hack
    id_to_find = message_id - 1

    #TODO: check if this is correct, very dirty hack
    #TODO: if correct, create a separate function for this
    message = session.query(Message).filter_by(
        message_id = id_to_find, 
        conversation_id = conversation_id
    ).first() or session.query(Message).filter_by(
        message_id = message_id, 
        conversation_id = conversation_id
    ).first()
    session.close()   
    
    # Return the sender_in_conversation_id if the message is found
    if message:
        return message
    else:
        # Handle the case where the message is not found, e.g., return None or raise an exception
        #raise SQLAlchemyError(f"Failed to find the message {message_id} in the database for {conversation_id} conversation.")
        return None
    

def get_currently_active_conversation_for_user_from_db(user_id: int) -> Conversation:
    session = SessionLocal()     
    conversation = session.query(Conversation).filter(
        (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id),
        Conversation.is_active == True
        ).first()
    session.close()
    return conversation



#TODO: make all these __db__ functions async
def get_message_in_inactive_conversations_from_db(message_id: int) -> Message:    
    session = SessionLocal()    
    message = (
    session.query(Message)
    .join(Conversation, Message.conversation_id == Conversation.id)
    .filter(
        Message.id == message_id,
        Conversation.is_active is False
    ).first())
    session.close()
    return message


#TODO: naming: get, set, check
def get_conversation_partner_from_db(user_id: int = 0):
    conversation = get_currently_active_conversation_for_user_from_db(user_id = user_id)    
    if not conversation:
        return None
    partner_id = conversation.user2_id if conversation.user1_id == user_id else conversation.user1_id
    return partner_id


def is_conversation_active(conversation_id: int) -> bool:
    session = SessionLocal()
    try:
        # Query the conversation by ID
        conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
        # Return the is_active status if the conversation is found
        return conversation.is_active if conversation else False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def set_conversation_inactive(conversation_id: int) -> None:
    session = SessionLocal()
    try:
        conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
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