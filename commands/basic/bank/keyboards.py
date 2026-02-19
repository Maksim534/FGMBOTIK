from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import config as cfg

def bank_actions_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для банковских операций"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="💰 Банк положить",
            switch_inline_query_current_chat="банк положить "  # 👈 Без @
        ),
        InlineKeyboardButton(
            text="💸 Банк снять",
            switch_inline_query_current_chat="банк снять "  # 👈 Без @
        ),
        width=2
    )
    
    builder.row(
        InlineKeyboardButton(
            text="📈 Депозит положить",
            switch_inline_query_current_chat="депозит положить "  # 👈 Без @
        ),
        InlineKeyboardButton(
            text="📉 Депозит снять",
            switch_inline_query_current_chat="депозит снять "  # 👈 Без @
        ),
        width=2
    )
    
    return builder.as_markup()
