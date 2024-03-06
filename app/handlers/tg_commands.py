from aiogram import Bot, Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.services.user_service import add_user_to_database, get_user_status, update_user_status
from aiogram import types
from app.database.engine import SessionLocal
from app.models.user import User


# Define user status constants
USER_STATUS_READY_TO_CHAT = "ready_to_chat"
USER_STATUS_NOT_READY_TO_CHAT = "not_ready_to_chat"


# Define states for registration
class RegistrationStates(StatesGroup):
    waiting_for_messages = State()


async def handle_user_messages(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    message_count = user_data.get('message_count', 0)
    message_count += 1

    # TODO: Save the message to the database here

    if message_count < 10:
        await message.answer(f"Thanks, please send the {10 - message_count} remaining messages.")
        await state.update_data(message_count=message_count)
    else:
        await message.answer("Thank you for sending 10 messages. You are now registered.")
        # TODO: Update the user's registration status in the database here
        await state.clear()


# Handler for user to set status to ready to chat
async def set_ready_to_chat(message: types.Message):
    user_id = message.from_user.id
    await update_user_status(user_id, USER_STATUS_READY_TO_CHAT)
    await message.answer("You are now ready to chat.")


# Handler for user to set status to not ready to chat

async def set_not_ready_to_chat(message: types.Message):
    user_id = message.from_user.id
    await update_user_status(user_id, USER_STATUS_NOT_READY_TO_CHAT)
    await message.answer("You are now set to not ready to chat.")


# Registration command handler

#TODO: Maybe move somewhere else
async def cmd_register(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    session = SessionLocal()
    try:
        existing_user = session.query(User).filter_by(id=user_id).first()
        if existing_user:
            if not existing_user.is_active:
                # Reactivate the user
                existing_user.is_active = True
                session.commit()
                await message.answer("You have been re-registered successfully.")
            else:
                await message.answer("You are already registered.")
        else:
            # Create a new user instance
            new_user = User(id=user_id, username=username, is_active=True)
            session.add(new_user)
            session.commit()
            await message.answer("You have been registered successfully.")
    except Exception as e:
        session.rollback()
        await message.answer("Registration failed.")
        print(str(e))
        # Log the exception or handle it as necessary
    finally:
        session.close()


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
        print(str(e))
        # Log the exception or handle it as necessary
    finally:
        session.close()

async def cmd_hard_unregister(message: types.Message):

    user_id = message.from_user.id
    print(f"Trying to unregister user: {user_id}")
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

async def cmd_start(message: types.Message):
    await message.answer("Welcome! Use /register to sign up and /start_chatting to begin chatting with someone.")

async def  message_reaction_handler(message_reaction: types.MessageReactionUpdated):
    #TODO: store all the messages sent by bot in DB, check whether this message is in DB to determine the sender: user or bot
    try:
        print("Emoji: ", message_reaction.new_reaction[0].emoji)
    except:
        print("Emoji: ", message_reaction.new_reaction.emoji)
