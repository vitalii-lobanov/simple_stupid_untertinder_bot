# states.py
from aiogram.fsm.state import State, StatesGroup
from utils.debug import logger
class RegistrationStates(StatesGroup):
    starting = State()
    receiving_messages = State()
    completed = State()

class CommonStates(StatesGroup):
    default = State()  # The default state for general bot interactions

class UserStates(StatesGroup):
    not_ready_to_chat = State()
    ready_to_chat = State()
    chatting_in_progress= State()