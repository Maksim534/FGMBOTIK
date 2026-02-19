from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def bank_actions_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для банковских операций"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки с префиллом команд
    builder.row(InlineKeyboardButton(
        text="💰 Положить в банк", 
        switch_inline_query_current_chat="банк положить "
    ))
    
    builder.row(InlineKeyboardButton(
        text="💸 Снять с банка", 
        switch_inline_query_current_chat="банк снять "
    ))
    
    builder.row(InlineKeyboardButton(
        text="📈 Депозит положить", 
        switch_inline_query_current_chat="депозит положить "
    ))
    
    builder.row(InlineKeyboardButton(
        text="📉 Депозит снять", 
        switch_inline_query_current_chat="депозит снять "
    ))
    
    return builder.as_markup()
