from typing import Union
import config as cfg
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

# 👇 СТАРЫЙ КЛАСС TextIn (работает и с сообщениями, и с колбэками)
class TextIn(BaseFilter):
    def __init__(self, *values: str) -> None:
        self.values = [v.lower() for v in values]

    async def __call__(self, obj: Union[Message, CallbackQuery]) -> bool:
        text = None
        if isinstance(obj, Message):
            text = obj.text
        elif isinstance(obj, CallbackQuery):
            text = obj.data
        return text and text.lower() in self.values


class TextInMessage(BaseFilter):
    def __init__(self, *values: str) -> None:
        self.values = [v.lower() for v in values]

    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        return message.text.lower() in self.values


class TextInCallback(BaseFilter):
    def __init__(self, *values: str) -> None:
        self.values = [v.lower() for v in values]

    async def __call__(self, call: CallbackQuery) -> bool:
        if not call.data:
            return False
        return call.data.lower() in self.values


class StartsWith(BaseFilter):
    def __init__(self, *prefixes: str):
        self.prefixes = [p.lower() for p in prefixes]

    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        
        original_text = message.text
        text = original_text.lower()
        bot_username = f"@{cfg.bot_username.lower()}"
        
        # Если текст начинается с @бота, то для проверки используем текст без него
        if text.startswith(bot_username):
            # Убираем @username и следующий пробел для проверки, НО НЕ МЕНЯЕМ message.text
            text_to_check = original_text[len(bot_username):].lstrip().lower()
        else:
            text_to_check = text
        
        # Проверяем все префиксы
        for prefix in self.prefixes:
            if text_to_check.startswith(prefix.lower()):
                return True
        return False
