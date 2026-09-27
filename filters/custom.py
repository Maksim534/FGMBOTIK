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

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        # Определяем тип события и получаем текст/данные
        if isinstance(event, Message):
            if not event.text:
                return False
            text = event.text
            # Для сообщений также обрабатываем упоминания
            bot_username = f"@{cfg.bot_username.lower()}"
            if text.lower().startswith(bot_username):
                text = text[len(bot_username):].lstrip()
        elif isinstance(event, CallbackQuery):
            if not event.data:
                return False
            text = event.data  # Для колбэков используем data, а не text
        else:
            return False

        text = text.lower()
        
        # Проверяем все префиксы
        for prefix in self.prefixes:
            if text.startswith(prefix.lower()):
                return True
        return False
