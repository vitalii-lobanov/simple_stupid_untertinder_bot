# states.py
from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    starting = State()
    receiving_messages = State()
    completed = State()