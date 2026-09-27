from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

class CallbackStartsWith(BaseFilter):
    def __init__(self, *prefixes: str):
        self.prefixes = [p.lower() for p in prefixes]

    async def __call__(self, call: CallbackQuery) -> bool:
        if not call.data:
            return False
        return any(call.data.lower().startswith(p) for p in self.prefixes)
