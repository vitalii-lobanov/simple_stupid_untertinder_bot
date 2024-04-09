from typing import Any, Awaitable, Dict, Union

from aiogram.filters.base import Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State


class InStateFilter(Filter):
    def __init__(self, state: State) -> None:
        
        super().__init__()
        self.state = state

    async def __call__(self, *args: Any, **kwargs: Any) -> Union[bool, Dict[str, Any]]:
        # Extract `FSMContext` from `kwargs` as it should be provided to the filter
        # by aiogram when the filter is applied to a handler
        state: FSMContext = kwargs.get("state")

        # If `state` is not present in `kwargs`, we cannot proceed
        if not state:
            raise ValueError("FSMContext not provided to InStateFilter.")

        # Get the current state of the user
        user_state = await state.get_state()

        # Check if the user's state matches the one we're looking for
        return user_state == self.state.state
