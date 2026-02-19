from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import config as cfg

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import config as cfg

def bank_actions_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для банковских операций"""
    builder = InlineKeyboardBuilder()
    
    # Формируем @username один раз
    bot_mention = f"@{cfg.bot_username}"  # 👈 Здесь добавляется @
    
    builder.row(InlineKeyboardButton(
        text="💰 Положить в банк", 
        switch_inline_query_current_chat=f"{bot_mention} банк положить "  # 👈 И здесь
    ))
    
    # ... остальные кнопки
    
    
    builder.row(InlineKeyboardButton(
        text="💸 Снять с банка", 
        switch_inline_query_current_chat=f"{bot_mention} банк снять "
    ))
    
    builder.row(InlineKeyboardButton(
        text="📈 Депозит положить", 
        switch_inline_query_current_chat=f"{bot_mention} депозит положить "
    ))
    
    builder.row(InlineKeyboardButton(
        text="📉 Депозит снять", 
        switch_inline_query_current_chat=f"{bot_mention} депозит снять "
    ))
    
    return builder.as_markup()
