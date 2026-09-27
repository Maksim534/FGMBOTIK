from aiogram.filters import BaseFilter
from aiogram.types import Message
import config as cfg

class HasBotMention(BaseFilter):
    """Фильтр для проверки, упомянут ли бот в начале сообщения"""
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        
        # Проверяем, начинается ли сообщение с @username_бота
        # или содержит упоминание бота в начале
        text = message.text.lower()
        bot_username = f"@{cfg.bot_username.lower()}"
        
        # Если сообщение начинается с @username_бота
        if text.startswith(bot_username):
            return True
        
        return False
