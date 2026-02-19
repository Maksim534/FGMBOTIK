from typing import Union
import config as cfg

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


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



class StartsWith(BaseFilter):
    def __init__(self, *prefixes: str):
        self.prefixes = [p.lower() for p in prefixes]

    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        
        text = message.text.lower()
        bot_username = f"@{cfg.bot_username.lower()}"
        
        # Если сообщение начинается с @бота, убираем его
        if text.startswith(bot_username):
            text = text[len(bot_username):].strip()
            # Обновляем текст сообщения для дальнейшей обработки
            message.text = message.text[len(bot_username):].strip()
        
        # Проверяем все префиксы
        for prefix in self.prefixes:
            if text.startswith(prefix):
                return True
        return False
