from aiogram import Bot, Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from models import add_user_to_database, get_user_status, update_user_status

# Define user status constants
USER_STATUS_READY_TO_CHAT = "ready_to_chat"
USER_STATUS_NOT_READY_TO_CHAT = "not_ready_to_chat"


# Define states for registration
class RegistrationStates(StatesGroup):
    waiting_for_messages = State()


# Initialize router
router = Router()


# Registration command handler


# Handler for subsequent messages during the registration process
@router.message(StateFilter(RegistrationStates.waiting_for_messages))
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


async def add_user_to_database(user_id: int, status: str):
    # Your code to add the user to the database with the given status
    print(f"Adding user {user_id} to the database")
    pass


async def get_user_status(user_id: int) -> str:
    # Your code to get the user status from the database
    print(f"Getting user {user_id} status from the database")
    pass


async def update_user_status(user_id: int, status: str):
    # Your code to update the user status in the database
    print(f"Updating user {user_id} status in the database")
    pass


# Handler for user to set status to ready to chat
@router.message(Command(commands=['ready']))
async def set_ready_to_chat(message: types.Message):
    user_id = message.from_user.id
    await update_user_status(user_id, USER_STATUS_READY_TO_CHAT)
    await message.answer("You are now ready to chat.")


# Handler for user to set status to not ready to chat
@router.message(Command(commands=['notready']))
async def set_not_ready_to_chat(message: types.Message):
    user_id = message.from_user.id
    await update_user_status(user_id, USER_STATUS_NOT_READY_TO_CHAT)
    await message.answer("You are now set to not ready to chat.")


# Registration command handler
@router.message(Command(commands=['register']))
async def cmd_register(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    # Check if the user is already registered and get their status
    existing_status = await get_user_status(user_id)
    if existing_status:
        await message.answer("You are already registered.")
    else:
        # Register the new user with status "not_ready_to_chat"
        await add_user_to_database(user_id, USER_STATUS_NOT_READY_TO_CHAT)
        await message.answer("Welcome new user! Please send 10 messages.")
        await state.set_state(RegistrationStates.waiting_for_messages)
        await state.update_data(message_count=0)


# Handler for user to set status to ready to chat
@router.message(Command(commands=['ready']))
async def set_ready_to_chat(message: types.Message):
    user_id = message.from_user.id
    await update_user_status(user_id, USER_STATUS_READY_TO_CHAT)
    await message.answer("You are now ready to chat.")


# Handler for user to set status to not ready to chat
@router.message(Command(commands=['notready']))
async def set_not_ready_to_chat(message: types.Message):
    user_id = message.from_user.id
    await update_user_status(user_id, USER_STATUS_NOT_READY_TO_CHAT)
    await message.answer("You are now set to not ready to chat.")


@router.message(Command(commands=['start']))
async def cmd_start(message: types.Message):
    await message.answer("Welcome! Use /register to sign up and /start_chatting to begin chatting with someone.")
