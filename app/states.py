# states.py
from aiogram.fsm.state import State, StatesGroup
from app.utils.debug import logger
class RegistrationStates(StatesGroup):
    starting = State()
    receiving_messages = State()
    completed = State()