from aiogram.fsm.context import FSMContext
from app.database.engine import SessionLocal
from app.states import RegistrationStates
from app.models.user import User
from aiogram import types
from app.states import CommonStates
from app.utils.debug import logger


# This function will create a new user instance in the database and initiate the message receiving state.
async def create_new_registration(message: types.Message, state: FSMContext, user_id: int, username: str):
    session = SessionLocal()
    new_user = User(id=user_id, username=username, is_active=False)
    session.add(new_user)
    session.commit()
    await ask_user_to_send_messages_to_fill_profile(message, state)


# This function will handle any exceptions that occur during the registration process.
async def registration_failed(message: types.Message, state: FSMContext, exception: Exception):
    await state.set_state(CommonStates.default)
    await message.answer("Registration failed.")
    logger.critical(str(exception))


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
    logger.critical(str(exception))  # Log the exception
    await state.set_state(CommonStates.default)
    session.close()


# This function will set the FSM state to RegistrationStates.receiving_messages to start receiving messages from the user.
async def ask_user_to_send_messages_to_fill_profile(message: types.Message, state: FSMContext):
    await state.set_state(RegistrationStates.receiving_messages)
    await state.update_data(message_count=0)
    logger.debug(f"User {message.from_user.id} has started registration.")
    await message.answer("Please send 10 messages to complete your registration.")


async def receiving_messages_on_registration_handler(message: types.Message, state: FSMContext):
    message_count = await increment_message_count(message, state)
    await check_message_threshold(message, state, message_count)


# This function will check if the user is already registered or not and initiate the registration process if necessary.
async def start_registration_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    session = SessionLocal()
    try:
        existing_user = session.query(User).filter_by(id=user_id).first()
        if existing_user and not existing_user.is_active:
            await ask_user_to_send_messages_to_fill_profile(message, state)
        elif existing_user:
            await message.answer("You are already registered.")
        else:
            await create_new_registration(message, state, user_id, message.from_user.username)
    except Exception as e:
        await registration_failed(message, state, e)
    finally:
        session.close()
