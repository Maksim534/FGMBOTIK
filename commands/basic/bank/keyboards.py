from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import config as cfg

def bank_actions_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для банковских операций с вставкой команды"""
    builder = InlineKeyboardBuilder()
    
    bot_mention = f"@{cfg.bot_username}"
    
    # Первый ряд: кнопки для пополнения (слева и справа)
    builder.row(
        InlineKeyboardButton(
            text="💰 Банк положить",
            switch_inline_query_current_chat=f"{bot_mention} банк положить "
        ),
        InlineKeyboardButton(
            text="💸 Банк снять",
            switch_inline_query_current_chat=f"{bot_mention} банк снять "
        ),
        width=2
    )
    
    # Второй ряд: кнопки для депозита
    builder.row(
        InlineKeyboardButton(
            text="📈 Депозит положить",
            switch_inline_query_current_chat=f"{bot_mention} депозит положить "
        ),
        InlineKeyboardButton(
            text="📉 Депозит снять",
            switch_inline_query_current_chat=f"{bot_mention} депозит снять "
        ),
        width=2
    )
    
    return builder.as_markup()
