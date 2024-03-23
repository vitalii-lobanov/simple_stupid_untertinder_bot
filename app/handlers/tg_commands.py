from aiogram import Bot, Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from services.user_service import add_user_to_database, get_user_status, update_user_status
from aiogram import types
from database.engine import SessionLocal
from core.states import  RegistrationStates
from models.user import User
from utils.debug import logger
from aiogram import types
from core.states import  CommonStates, UserStates
from aiogram.types import ReactionTypeEmoji
from models.base import MessageSource
from services.dao import save_telegram_message

from aiogram.fsm.context import FSMContext
from database.engine import SessionLocal
from core.states import  RegistrationStates
from models.user import User
from aiogram import types
from core.states import  CommonStates
from utils.debug import logger
from models.message import Message
from models.base import MessageSource
from services.dao import save_telegram_message, save_tiered_registration_message
from services.score_tiers import message_tiers_count
from handlers.tg_user_register_handlers import ask_user_to_send_messages_to_fill_profile, create_new_registration, registration_failed
from handlers.tg_chatting_handlers import one_more_user_is_ready_to_chat


#TODO: all the cmd_ functions from handlers should be here

async def cmd_start(message: types.Message, state: FSMContext):
    #await save_telegram_message(message=message, message_source=MessageSource.command_received)
    await state.set_state(CommonStates.default)
    await message.answer("Welcome! Use /register to sign up and /start_chatting to begin chatting with someone.")


async def cmd_unregister(message: types.Message):
    user_id = message.from_user.id

    session = SessionLocal()
    try:
        existing_user = session.query(User).filter_by(id=user_id).first()
        if existing_user and existing_user.is_active:
            # Mark the user as inactive instead of deleting
            existing_user.is_active = False
            session.commit()
            await message.answer("You have been unregistered successfully.")
        else:
            # The user is not registered or already inactive
            await message.answer("You are not registered or already unregistered.")
    except Exception as e:
        session.rollback()
        await message.answer("Unregistration failed.")
        await logger.error(msg=f"Unregistration failed: {str(e)}", chat_id=user_id)
        # Log the exception or handle it as necessary
    finally:
        session.close()


async def cmd_hard_unregister(message: types.Message):
    user_id = message.from_user.id
    logger.sync_debug(f"Trying to unregister user: {user_id}")
    # Create a new database session
    session = SessionLocal()
    try:
        # Retrieve the user profile
        user_profile = session.query(User).filter_by(id=user_id).first()
        if user_profile:
            # Delete any related data here, for example, user messages, settings, etc.
            # session.query(RelatedModel).filter_by(user_id=user_id).delete()

            # Delete the user profile
            session.delete(user_profile)
            session.commit()
            await message.answer("Your profile and all associated data have been permanently deleted.")
        else:
            await message.answer("You do not have a profile to delete.")
    except Exception as e:
        session.rollback()
        await message.answer("Failed to unregister. Please try again later.")
        print(str(e))
        # Log the exception or handle it as necessary
    finally:
        session.close()


async def cmd_register(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    with SessionLocal() as session:
        try:
            existing_user = session.query(User).filter_by(id=user_id).first()
            # Check if user is already registered
            if existing_user:
                # Check if the user has the required number of profile messages
                profile_messages_count = session.query(Message).filter_by(user_id=user_id).count()

                if existing_user.is_active and profile_messages_count == message_tiers_count.MESSAGE_TIERS_COUNT:
                    # Notify the active user with the complete profile that their existing messages will be used
                    await message.answer(
                        "You have already created a profile and your existing messages will be used. "
                        "If you want to create a new profile, please use /hard_unregister command."
                    )
                elif not existing_user.is_active:
                    # Handle reactivation or continuation of registration for inactive users
                    # await ask_user_to_send_messages_to_fill_profile(message, state)
                    # Or reactivate the user and notify them accordingly
                    existing_user.is_active = True
                    session.commit()
                    await message.answer("Your profile has been reactivated.")
                else:
                    # The user is active but doesn't have message_tiers_count.MESSAGE_TIERS_COUNT messages, proceed with message collection
                    await ask_user_to_send_messages_to_fill_profile(message, state)
            else:
                # User is not registered, start new registration
                await create_new_registration(message, state, user_id, (message.from_user.username or f"{message.from_user.first_name} {message.from_user.last_name}"))

        except Exception as e:
            await registration_failed(message, state, e)
        finally:
            session.close()

async def cmd_start_chatting(message: types.Message, state: FSMContext):
    session = SessionLocal()
    user_id = message.from_user.id
    try:
        user = session.query(User).filter(User.id == user_id).one_or_none()

        if user is None:
            # Handle the case where no user was found
            await logger.error(msg="No user found with ID {}".format(user_id), state=state)
            await message.answer("Your user account was not found.")
            return

        user.is_ready_to_chat = (
            True  # Assuming there is a field like this in your User model
        )
        session.commit()
        await state.set_state(UserStates.ready_to_chat)
        await logger.debug(
            msg=f"User {user_id} is ready to chat and user's state is set to {UserStates.ready_to_chat}", 
            state=state)
        await message.answer(
            "You are now ready to chat with someone. Please wait for a partner to connect."
        )

        # Trying to find a chat partner
        await one_more_user_is_ready_to_chat(user_id, state)
    except Exception as e:
        session.rollback()
        await logger.error(msg=f"Caught exception in cmd_start_chatting: {str(e)}", state=state)
    finally:
        session.close()