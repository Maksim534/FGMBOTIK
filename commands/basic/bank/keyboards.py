from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def bank_actions_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для банковских операций"""
    builder = InlineKeyboardBuilder()

    # Первый ряд: две кнопки (положить)
    builder.row(
        InlineKeyboardButton(
            text="💰 Положить в банк",
            callback_data=f"bank_put_{user_id}"
        ),
        InlineKeyboardButton(
            text="📈 Депозит положить",
            callback_data=f"deposit_put_{user_id}"
        ),
        width=2
    )

    # Второй ряд: две кнопки (снять)
    builder.row(
        InlineKeyboardButton(
            text="💸 Снять с банка",
            callback_data=f"bank_take_{user_id}"
        ),
        InlineKeyboardButton(
            text="📉 Депозит снять",
            callback_data=f"deposit_take_{user_id}"
        ),
        width=2
    )

    return builder.as_markup()
