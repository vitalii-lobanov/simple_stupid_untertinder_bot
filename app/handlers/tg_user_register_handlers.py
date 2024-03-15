
from aiogram.fsm.context import FSMContext
from database.engine import SessionLocal
from states import RegistrationStates
from models.user import User
from aiogram import types
from states import CommonStates
from utils.debug import logger
from models.message import Message
from models.base import MessageSource
from services.dao import save_telegram_message, save_tiered_registration_message

#from app.tasks.tasks import celery_app

# This function will create a new user instance in the database and initiate the message receiving state.
async def create_new_registration(message: types.Message, state: FSMContext, user_id: int, username: str):
    session = SessionLocal()
    new_user = User(id=user_id, username=username, is_active=False, is_ready_to_chat=False)
    session.add(new_user)
    session.commit()
    await ask_user_to_send_messages_to_fill_profile(message, state)


# This function will handle any exceptions that occur during the registration process.
async def registration_failed(message: types.Message, state: FSMContext, exception: Exception):
    await state.set_state(CommonStates.default)
    await message.answer("Registration failed.")
    logger.error(str(exception))


async def increment_message_count(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    message_count = user_data.get('message_count', 0) + 1
    await state.update_data(message_count=message_count)
    return message_count


async def check_message_threshold(message: types.Message, state: FSMContext, message_count: int):
    if message_count < 10:
        await message.answer(f"Message {message_count} received. {10 - message_count} messages left.")
    else:
        await complete_registration(message, state)


async def complete_registration(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    session = SessionLocal()
    try:
        existing_user = session.query(User).filter_by(id=user_id).first()
        if existing_user and not existing_user.is_active:
            existing_user.is_active = True
            session.commit()
            await message.answer("Congratulations, your registration is now complete!")
        else:
            await message.answer("Unexpected error during registration completion. Please contact support.")
    except Exception as e:
        await handle_registration_error(message, state, e)
    finally:
        session.close()
        await state.set_state(CommonStates.default)


async def handle_registration_error(message: types.Message, state: FSMContext, exception: Exception):
    session = SessionLocal()
    session.rollback()
    await message.answer("Failed to complete registration.")
    logger.error(str(exception))  # Log the exception
    await state.set_state(CommonStates.default)
    session.close()


# This function will set the FSM state to RegistrationStates.receiving_messages to start receiving messages from the user.
async def ask_user_to_send_messages_to_fill_profile(message: types.Message, state: FSMContext):
    await state.set_state(RegistrationStates.receiving_messages)
    await state.update_data(message_count=0)
    logger.debug(f"User {message.from_user.id} has started registration.")
    await message.answer("Please send 10 messages to complete your registration.")


async def receiving_messages_on_registration_handler(message: types.Message, state: FSMContext):
    if state is RegistrationStates.receiving_messages or RegistrationStates.starting or RegistrationStates.completed:
        message_count = await increment_message_count(message, state)
        await save_tiered_registration_message(message, message_count)
        await check_message_threshold(message, state, message_count)
    else:
        logger.error(f"Unexpected state encountered while receiving messages on registration: {state}")





# This function will check if the user is already registered or not and initiate the registration process if necessary.
# async def start_registration_handler(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     session = SessionLocal()
#     try:
#         existing_user = session.query(User).filter_by(id=user_id).first()
#
#         if existing_user and not existing_user.is_active:
#             await ask_user_to_send_messages_to_fill_profile(message, state)
#         elif existing_user:
#             await message.answer("You are already registered.")
#         else:
#             await create_new_registration(message, state, user_id, message.from_user.username)
#     except Exception as e:
#         await registration_failed(message, state, e)
#     finally:
#         session.close()




async def start_registration_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    with SessionLocal() as session:
        try:
            existing_user = session.query(User).filter_by(id=user_id).first()
            # Check if user is already registered
            if existing_user:
                # Check if the user has the required number of profile messages
                profile_messages_count = session.query(Message).filter_by(user_id=user_id).count()

                if existing_user.is_active and profile_messages_count == 10:
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
                    # The user is active but doesn't have 10 messages, proceed with message collection
                    await ask_user_to_send_messages_to_fill_profile(message, state)
            else:
                # User is not registered, start new registration
                await create_new_registration(message, state, user_id, (message.from_user.username or f"{message.from_user.first_name} {message.from_user.last_name}"))

        except Exception as e:
            await registration_failed(message, state, e)
        finally:
            session.close()
