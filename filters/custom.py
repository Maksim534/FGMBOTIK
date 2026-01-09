from typing import Union

from aiogram.types import Message, CallbackQuery



class StartsWith(BaseFilter):
    def __init__(self, *prefixes: str) -> None:
        self.prefixes = [p.lower() for p in prefixes]

    async def __call__(self, obj: Union[Message, CallbackQuery]) -> bool:
        text = None

        if isinstance(obj, Message):
            text = obj.text
        elif isinstance(obj, CallbackQuery):
            text = obj.data

        if not text:
            return False

        return any(text.lower().startswith(prefix) for prefix in self.prefixes)
