from aiogram import types
from aiogram.filters.base import Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from app.utils.debug import logger

class InStateFilter(Filter):
    # Initialize with the state you want to check
    def __init__(self, state: State):
        self.state = state

    # The check method will be called for each message
    async def check(self, message: types.Message, state: FSMContext) -> bool:
        # Get the current state of the user
        user_state = await state.get_state()
        # Check if the user's state matches the one we're looking for
        return user_state == self.state.state
