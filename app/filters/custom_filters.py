
from typing import Any, Awaitable, Dict, Union, List

from aiogram.filters.base import Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

class InStateFilter(Filter):
    def __init__(self, states: List[State]) -> None:
        super().__init__()
        self.states = states

    async def __call__(self, *args: Any, **kwargs: Any) -> Union[bool, Dict[str, Any]]:
        state: FSMContext = kwargs.get("state")
        if not state:
            raise ValueError("FSMContext not provided to InStateFilter.")

        user_state = await state.get_state()
        return user_state in (state.state for state in self.states)