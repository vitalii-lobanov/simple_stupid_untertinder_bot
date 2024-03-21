import random
from datetime import datetime
from utils.text_messages import message_a_conversation_partner_found, message_you_now_connected_to_the_conversation_partner
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import ReactionTypeEmoji
from bot import bot_instance
from sqlalchemy.exc import SQLAlchemyError
# from app.tasks.tasks import celery_app
from database.engine import SessionLocal
from dispatcher import dispatcher
from models import Conversation, Message
from models.user import User
from states import CommonStates, UserStates
from utils.debug import logger
from services.dao import save_telegram_message, save_telegram_reaction
from models.message import MessageSource
from aiogram.methods.set_message_reaction import SetMessageReaction
from services.emoji_rank import EmojiRank
from services.score_tiers import message_tiers_count, profile_disclosure_tiers_score_levels
from handlers.tg_user_staging import send_tiered_message_to_user


async def __initialize_states_for_chatter__(state: FSMContext):
        await state.update_data(current_score=0)
        await state.update_data(message_count=0)
        await state.update_data(disclosure_level=-1)        


async def __set_disclosure_level__(state: FSMContext, level: int):
    await state.update_data(disclosure_level=level)

async def __get_disclosure_level__(state: FSMContext):
    disclosure_level_data= await state.get_data()
    disclosure_level = disclosure_level_data['disclosure_level'] 
    return disclosure_level
        
            
# TODO: возможно, во всех случаях Exceptions ставить default_state, причём не только тут.

async def one_more_user_is_ready_to_chat(user_id: int, user_state: FSMContext):
    session = SessionLocal()
    try:
        current_user_id = user_id

        # Step 1: Find a chat partner
        # Query for users who are ready to chat and whom the current user has never chatted with before
        potential_partners = (
            session.query(User)
            .filter(
                User.is_ready_to_chat == True,
                User.id != current_user_id,  # Exclude the current user from the results
                ~session.query(Conversation)
                .filter(
                    (Conversation.user1_id == current_user_id)
                    & (Conversation.user2_id == User.id)
                    | (Conversation.user2_id == current_user_id)
                    & (Conversation.user1_id == User.id)
                )
                .exists(),
            )
            .all()
        )

        # Step 2: Choose a chat partner
        if potential_partners:
            partner = random.choice(potential_partners)

            # Step 3: Create a new Conversation instance
            conversation = Conversation(user1_id=current_user_id, user2_id=partner.id,start_time=datetime.now(),is_active=True)
            session.add(conversation)
            session.commit()

            # Typically, in Telegram bots, the chat ID is the same as the user ID for private chats.
            partner_chat_id = partner.id

            # Update the state for both users
            await user_state.set_state(
                UserStates.chatting_in_progress
            )  # You'll need to define this state
            partner_context = FSMContext(
                dispatcher.storage,
                StorageKey(
                    chat_id=partner_chat_id, user_id=partner.id, bot_id=bot_instance.id
                ),
            )
            await partner_context.set_state(UserStates.chatting_in_progress)
            
            await __initialize_states_for_chatter__(user_state)
            await __initialize_states_for_chatter__(partner_context)

            # Step 4: Inform both users
            await bot_instance.send_message(
                chat_id=current_user_id,
                text=message_you_now_connected_to_the_conversation_partner(),
            )
            await bot_instance.send_message(
                chat_id=partner.id, text=message_a_conversation_partner_found()
            )

        else:
            await bot_instance.send_message(
                chat_id=current_user_id,
                text="No chat partners available right now. We will iform you when one is available.",
            )
            await user_state.set_state(UserStates.ready_to_chat)

    except Exception as e:
        session.rollback()
        await bot_instance.send_message(
            chat_id=current_user_id,
            text=f"An error occurred in state_user_is_ready_to_chat_handler. Error: {str(e)}",
        )
        logger.error(
            f"Caught exception in state_user_is_ready_to_chat_handler: {str(e)}"
        )
        await user_state.set_state(CommonStates.default)

    finally:
        session.close()


async def user_start_chatting(message: types.Message, state: FSMContext):
    session = SessionLocal()
    user_id = message.from_user.id
    try:
        user = session.query(User).filter(User.id == user_id).one_or_none()

        if user is None:
            # Handle the case where no user was found
            logger.error("No user found with ID {}".format(user_id))
            await message.answer("Your user account was not found.")
            return

        user.is_ready_to_chat = (
            True  # Assuming there is a field like this in your User model
        )
        session.commit()
        await state.set_state(UserStates.ready_to_chat)
        logger.debug(
            f"User {user_id} is ready to chat and user's state is set to {UserStates.ready_to_chat}"
        )
        await message.answer(
            "You are now ready to chat with someone. Please wait for a partner to connect."
        )

        # Trying to find a chat partner
        await one_more_user_is_ready_to_chat(user_id, state)
    except Exception as e:
        session.rollback()
        logger.error(f"Caught exception in user_start_chatting: {str(e)}")
    finally:
        session.close()


# async def state_user_is_ready_to_chat_handler(message: types.Message, state: FSMContext):
#     session = SessionLocal()
#     try:
#         # Step 1: Find a chat partner
#         current_user_id = message.from_user.id

#         # Query for users who are ready to chat and whom the current user has never chatted with before
#         potential_partners = session.query(User).filter(
#             User.is_ready_to_chat == True,
#             User.id != current_user_id,  # Exclude the current user from the results
#             ~session.query(Conversation).filter(
#                 (Conversation.user1_id == current_user_id) & (Conversation.user2_id == User.id) |
#                 (Conversation.user2_id == current_user_id) & (Conversation.user1_id == User.id)
#             ).exists()
#         ).all()

#         # Step 2: Choose a chat partner
#         if potential_partners:
#             partner = random.choice(potential_partners)

#             # Step 3: Create a new Conversation instance
#             conversation = Conversation(user1_id=current_user_id, user2_id=partner.id)
#             session.add(conversation)
#             session.commit()

#             #Typically, in Telegram bots, the chat ID is the same as the user ID for private chats.
#             partner_chat_id = partner.id

#             #Trying to update partner's state
#             partner_context = FSMContext(dispatcher.storage, partner.id, partner_chat_id)
#             await partner_context.set_state(UserStates.chatting_in_progress)

#             # Step 4: Inform both users
#             await message.answer("You are now connected with a chat partner!")
#             await bot_instance.send_message(chat_id=partner.id, text="Someone became your chat partner!")

#             # Update the state for both users
#             await state.set_state(UserStates.chatting_in_progress)  # You'll need to define this state
#             await state.storage.set_state(partner.id, state=UserStates.chatting_in_progress)  # And for the partner
#         else:
#             await message.answer("No chat partners available right now. We will iform you when one is available.")
#             await state.set_state(UserStates.ready_to_chat)

#     except Exception as e:
#         session.rollback()
#         await message.answer(f"An error occurred in state_user_is_ready_to_chat_handler. Error: {str(e)}")
#         await state.set_state(CommonStates.default)
#         # Log the error
#     finally:
#         session.close()


async def state_user_is_in_chatting_progress_handler(
    message: types.Message, state: FSMContext
):
    user_id = message.from_user.id
    session = SessionLocal()

    try:
        # Query for the active conversation that the user is a part of
        conversation = (
            session.query(Conversation)
            .filter(
                Conversation.is_active == True,
                (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id),
            )
            .first()
        )

        if conversation:
            # Determine the partner's user ID
            partner_id = (
                conversation.user2_id
                if user_id == conversation.user1_id
                else conversation.user1_id
            )

            await save_telegram_message(message=message, message_source=MessageSource.conversation, conversation_id=conversation.id)

            # Construct new Telegram message object(?)_
            await bot_instance.send_message(chat_id=partner_id, text=message.text)
            # ... Add handling for other message types (photos, videos, etc.)
        else:
            await message.answer(
                "You are not currently in an active conversation. Please contact support."
            )

    except Exception as e:
        session.rollback()
        logger.error(f"Caught exception in state_user_is_in_chatting_progress: {str(e)}")
        # Handle the exception, possibly sending a message back to the user
    finally:
        session.close()


async def stop_chatting_command_handler(
    message: types.Message, state: FSMContext, hard_type: bool = False
):
    user_id = message.from_user.id
    session = SessionLocal()

    # Check if the user is in chatting_in_progress state
    current_state = await state.get_state()
    if current_state != UserStates.chatting_in_progress:
        await message.answer(
            "You are not currently in a conversation. You can use '/start_chatting' to start one."
        )
        return

    try:
        # Query for the active conversation for the user
        conversation = (
            session.query(Conversation)
            .filter(
                Conversation.is_active == True,
                (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id),
            )
            .first()
        )

        if conversation:
            # Retrieve the partner's user ID before setting is_active to False or deleting
            partner_id = (
                conversation.user2_id
                if user_id == conversation.user1_id
                else conversation.user1_id
            )

            # Set 'is_active' attribute to False or delete if hard_type is True
            if hard_type:
                session.delete(conversation)
            else:
                conversation.is_active = False

            session.commit()

            # Notify both users that the conversation has ended
            await message.answer("The conversation has been finished.")
            await bot_instance.send_message(
                chat_id=partner_id, text="Your partner has stopped the conversation."
            )

            await state.set_state(UserStates.not_ready_to_chat)
            current_user = session.query(User).filter(User.id == user_id).first()
            if current_user:
                current_user.is_ready_to_chat = False
                session.commit()
            else:
                session.rollback()
                await message.answer("Failed to update user status in the database.")
                return

            # Update the state for the partner
            partner_state = dispatcher.current_state(chat=partner_id, user=partner_id)
            await partner_state.set_state(UserStates.not_ready_to_chat)

            partner_user = session.query(User).filter(User.id == partner_id).first()
            if partner_user:
                partner_user.is_ready_to_chat = False
                session.commit()
            else:
                session.rollback()
                await message.answer(
                    "Failed to update partner's status in the database."
                )
                return

        else:
            await message.answer("You are not currently in an active conversation.")

    except Exception as e:
        session.rollback()
        # Handle the exception
        await message.answer(
            f"An error occurred while stopping the conversation: {str(e)}"
        )
    finally:
        session.close()


async def update_user_score_in_conversation(state: FSMContext, delta: float):    
    score_data= await state.get_data()
    new_score = score_data['current_score'] + delta
    await state.update_data(current_score=new_score) 
    return new_score


async def check_conversation_score_threshold(current_score: int, state: FSMContext):
    current_disclosure_level = await __get_disclosure_level__(state)
    for index, tier_threshold in enumerate(reversed(profile_disclosure_tiers_score_levels.PROFILE_DISCLOSURE_TIER_LEVELS)):
        reversed_index = len(profile_disclosure_tiers_score_levels.PROFILE_DISCLOSURE_TIER_LEVELS) - 1 - index
        if (current_score >= tier_threshold) and (current_disclosure_level < reversed_index):
            await __set_disclosure_level__(state, reversed_index)
            logger.debug(f"Your score is {current_score}. You have reached the {tier_threshold} score threshold at index {index}.")
            return reversed_index
    
    logger.debug(f"Your score is {current_score}. You have not reached the {tier_threshold} score threshold at index {index}.")
    return False


async def access_user_context(chat_id: int, user_id: int, bot_id: int):
        user_context = FSMContext(
        dispatcher.storage,
        StorageKey(
            chat_id=chat_id, user_id=user_id, bot_id=bot_id
        ),
            )
        return user_context


#TODO: check session.close() for all the open sessions


def __get_message__from_db__(message_id: int, conversation_id: int) -> Message:
    session = SessionLocal()   
 
    # messages = session.query(Message)
    # message = messages.filter_by(message_id = 4687).first()
    # message = messages.filter_by(id=4687).first()

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

#TODO: handle changing or removing the reactions
async def message_reaction_handler(message_reaction: types.MessageReactionUpdated, user_context: FSMContext):

    user_id = message_reaction.user.id

   #TODO: forbid to like bot's service messages (not redirected from the chat partner)

    # Find the conversation where the message was sent
    session = SessionLocal()     
    conversation = session.query(Conversation).filter(
        (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id),
        Conversation.is_active == True
        ).first()
    
    if not conversation:
        logger.error("Failed to find the conversation where the message was sent")
        raise SQLAlchemyError ("Failed to find the conversation where the message was sent")  
        return
    
    #Users should not react to their own messages    
    message_from_db = __get_message__from_db__(message_id=message_reaction.message_id, conversation_id=conversation.id)
    message_sender = message_from_db.sender_in_conversation_id

    # TODO:
        #А вот тут посмотреть, что делать. None может быть разным: 
        # 1 — когда юзер лайкнул что-то из предыдущей беседы
        # 2 — когда юзер лайкнул сервисное сообщение бота
        # 3 — реальная ошибка логики / бота
        # В первом случае надо ему послать сообщение о том, что не надо лайкать предыдущее
        # Во втором надо сказать, что бота лайкать не нужно (и не продолжать логику исполнения)
        # В третьем — кинуть не только исключение, но и сообщение юзеру — полезно на тест. 

    if message_sender is None:
        pass

    if user_id == message_sender:
        #TODO: add more user messages text for this (i.e. narcissism)
        await bot_instance.send_message(chat_id=user_id, text="You should not react to your own messages.")
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

        # Save the reaction
        # TODO: -1 logic from __get_message_sender_id_from_db__()
        if save_telegram_reaction(
            user_id=message_reaction.user.id,  
            # I do not know why -1 is needed
            message_id=message_reaction.message_id - 1,  
            new_emoji=new_emoji,
            old_emoji=old_emoji,
            timestamp=datetime.now(),    
            rank=rank,    
        ):
            
   
                # Identify the other participant in the conversation
            partner_id = conversation.user2_id if conversation.user1_id == user_id else conversation.user1_id
            emoji_reaction = ReactionTypeEmoji(emoji = new_emoji) if new_emoji else None

            await bot_instance.set_message_reaction(
                chat_id=partner_id,
                message_id=message_reaction.message_id-1,
                reaction=[emoji_reaction] if emoji_reaction else []
            )             

              
            

                

            #TODO: change any other context access to call custom get context — access_user_context

            #user_context = await access_user_context(chat_id=chat_id, user_id=user_id, bot_id=bot_instance.id)
          
            current_score = await update_user_score_in_conversation(
                state = user_context,
                delta=rank
            )
            
            reached_tier = await check_conversation_score_threshold(current_score=current_score, state=user_context)
            if reached_tier is not False:
                logger.debug(f"Your score is {current_score}. You have reached the {reached_tier} score threshold.")
                await bot_instance.send_message(chat_id=user_id, text=f"""Your score is {current_score}. You have reached the {reached_tier} score threshold. 
                                                Now you can see a part of your partner's profile.""")
                
                #TODO: Change all the parameters everywhere for named arguments instead of positional
                await send_tiered_message_to_user(bot_instance, user_id, partner_id, reached_tier)

                if reached_tier >= len (profile_disclosure_tiers_score_levels.PROFILE_DISCLOSURE_TIER_LEVELS) - 1:
                    logger.debug(f"Your score is {current_score}. You have reached the last score threshold.")
                    await bot_instance.send_message(chat_id=user_id, text="You have reached the last score threshold. Now you can see your partner's profile.")
                    #TODO: handle last tier
                

                
        else:
            #TODO: here and everywhere else: clear states on exceptions!

            logger.error("Failed to save the reaction to the database")
            raise SQLAlchemyError ("Failed to save the reaction to the database")
                
    except Exception as e:
        logger.error(f"An exception occurred while handling the message reaction: {e}")