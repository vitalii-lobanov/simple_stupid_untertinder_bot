from aiogram import Bot, Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter

# Define states for registration
class RegistrationStates(StatesGroup):
    waiting_for_messages = State()

# Initialize router
router = Router()

# Registration command handler
@router.message(Command(commands=['register']))
async def cmd_register(message: types.Message, state: FSMContext):
    await message.answer("Welcome new user! Please send 10 messages.")
    await state.set_state(RegistrationStates.waiting_for_messages)
    await state.update_data(message_count=0)

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


def register_handlers(router: Router):
    @router.message(Command(commands=['start']))
    async def cmd_start(message: types.Message):
        await message.answer("Welcome! Use /register to sign up and /start_chatting to begin chatting with someone.")

    @router.message(Command(commands=['register']))
    async def cmd_register(message: types.Message, state: FSMContext):
        await message.answer("Welcome new user! Please send 10 messages.")
        # Set the initial user state
        await state.set_state(RegistrationStates.waiting_for_messages)
        # Initialize the message count
        await state.update_data(message_count=0)
