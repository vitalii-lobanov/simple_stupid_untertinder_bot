
from aiogram.fsm.context import FSMContext
from database.engine import SessionLocal
from states import RegistrationStates
from models.user import User
from aiogram import types
from states import CommonStates, UserStates
from utils.debug import logger
from models import ProfileDataTieredMessage
from tasks import celery_app
from database.engine import SessionLocal
from models.user import User
from models.conversation import Conversation
from sqlalchemy.orm import aliased
from aiogram import types
import random
from models import Message, Conversation


global bot_instance

async def user_start_chatting(message: types.Message, state: FSMContext):
    session = SessionLocal()
    user_id = message.from_user.id
    try:
        user = session.query(User).filter(User.id == user_id).one()
        user.is_ready_to_chat = True  # Assuming there is a field like this in your User model
        session.commit()
        await state.set_state(UserStates.ready_to_chat)
        await message.answer("You are now ready to chat with someone.")
    except Exception as e:
        session.rollback()
        logger.critical(f'Caught exception in user_start_chatting: str(e)')
    finally:
        session.close()


async def state_user_is_ready_to_chat_handler(message: types.Message, state: FSMContext):
    session = SessionLocal()
    try:
        # Step 1: Find a chat partner
        current_user_id = message.from_user.id

        # Using aliased to avoid self-join conflicts
        UserAlias = aliased(User)

        # Query for users who are ready to chat and whom the current user has never chatted with before
        potential_partners = session.query(User).filter(
            User.is_ready_to_chat == True,
            ~session.query(Conversation).filter(
                (Conversation.user1_id == current_user_id) & (Conversation.user2_id == User.id) |
                (Conversation.user2_id == current_user_id) & (Conversation.user1_id == User.id)
            ).exists()
        ).all()

        # Step 2: Choose a chat partner
        if potential_partners:
            partner = random.choice(potential_partners) 

            # Step 3: Create a new Conversation instance
            conversation = Conversation(user1_id=current_user_id, user2_id=partner.id)
            session.add(conversation)
            session.commit()

            # Step 4: Inform both users
            await message.answer("You are now connected with a chat partner!")
            await bot_instance.send_message(partner.id, "You are now connected with a chat partner!")

            # Update the state for both users
            await state.set_state(UserStates.chatting_in_progress)  # You'll need to define this state
            await state.storage.set_state(partner.id, state=UserStates.chatting_in_progress)  # And for the partner
        else:
            await message.answer("No chat partners available right now. We will iform you when one is available.")
            await state.set_state(UserStates.ready_to_chat)

    except Exception as e:
        session.rollback()
        await message.answer("An error occurred. Please try again.")
        # Log the error
    finally:
        session.close()

async def state_user_is_in_chatting_progress(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    session = SessionLocal()

    try:
        # Query for the active conversation that the user is a part of
        conversation = (
            session.query(Conversation)
            .filter(
                Conversation.is_active == True,
                (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)
            )
            .first()
        )

        if conversation:
            # Determine the partner's user ID
            partner_id = conversation.user2_id if user_id == conversation.user1_id else conversation.user1_id

            # Step 2: Save the message to the database with the determined conversation_id
            new_message = Message(
                sender_id=user_id,
                conversation_id=conversation.id,
                text=message.text,  
            )
            session.add(new_message)
            session.commit()

            # Now send the message to the partner
            await bot_instance.send_message(partner_id, message.text)
            # ... Add handling for other message types (photos, videos, etc.)
        else:
            await message.answer("You are not currently in an active conversation. Please contact support.")

    except Exception as e:
        session.rollback()
        logger.debug(f'Caught exception in state_user_is_in_chatting_progress: str(e)')
        # Handle the exception, possibly sending a message back to the user
    finally:
        session.close()