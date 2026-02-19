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
        
        original_text = message.text
        text = original_text.lower()
        bot_username = f"@{cfg.bot_username.lower()}"
        
        # Если сообщение начинается с @бота, убираем его из проверки, НО НЕ МЕНЯЕМ message.text
        if text.startswith(bot_username):
            # Просто проверяем текст после упоминания
            text_without_mention = original_text[len(bot_username):].lstrip().lower()
        else:
            text_without_mention = text
        
        # Проверяем все префиксы
        for prefix in self.prefixes:
            if text_without_mention.startswith(prefix.lower()):
                return True
        return False
