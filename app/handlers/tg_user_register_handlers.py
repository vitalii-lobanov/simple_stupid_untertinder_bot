
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
    await logger.error(msg=f'Failed to complete registration. Exception: {str(exception)}', state=state)


async def increment_message_count(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    message_count = user_data.get('message_count', 0) + 1
    await state.update_data(message_count=message_count)
    return message_count


async def check_message_threshold(message: types.Message, state: FSMContext, message_count: int):
    if message_count < message_tiers_count.MESSAGE_TIERS_COUNT:
        await message.answer(f"Message {message_count} received. {message_tiers_count.MESSAGE_TIERS_COUNT - message_count} messages left.")
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
    await logger.error(msg=f'Failed to complete registration: {str(exception)}', state=state)  # Log the exception
    await state.set_state(CommonStates.default)
    session.close()


# This function will set the FSM state to RegistrationStates.receiving_messages to start receiving messages from the user.
async def ask_user_to_send_messages_to_fill_profile(message: types.Message, state: FSMContext):
    await state.set_state(RegistrationStates.receiving_messages)
    await state.update_data(message_count=0)
    logger.sync_debug(f"User {message.from_user.id} has started registration.")
    await message.answer(f"Please send {message_tiers_count.MESSAGE_TIERS_COUNT} messages to complete your registration.")


async def receiving_messages_on_registration_handler(message: types.Message, state: FSMContext):
    if state is RegistrationStates.receiving_messages or RegistrationStates.starting or RegistrationStates.completed:
        message_count = await increment_message_count(message, state)
        await save_tiered_registration_message(message, message_count)
        await check_message_threshold(message, state, message_count)
    else:
        await logger.error(msg = f"Unexpected state encountered while receiving messages on registration: {state}", state=state)




