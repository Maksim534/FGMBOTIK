from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def miracles_menu(user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="🎲 Случайное (всё)", callback_data=f"miracles-start_random|{user_id}"),
        InlineKeyboardButton(text="👤 Человек", callback_data=f"miracles-start_people|{user_id}"),
    )
    keyboard.row(
        InlineKeyboardButton(text="🏠 Быт", callback_data=f"miracles-start_life|{user_id}"),
        InlineKeyboardButton(text="🌏 Мир", callback_data=f"miracles-start_world|{user_id}"),
    )
    keyboard.row(
        InlineKeyboardButton(text="🎮 Развлечения", callback_data=f"miracles-start_attractions|{user_id}"),
        InlineKeyboardButton(text="🧪 Наука", callback_data=f"miracles-start_science|{user_id}"),
    )
    return keyboard.as_markup()


def miracles_start() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="🔁 Сменить категорию", callback_data=f"miracles-change-category"),
        InlineKeyboardButton(text="🛑 Завершить игру", callback_data=f"miracles-stop"),
    )
    return keyboard.as_markup()


def kwak_game(user_id: int, player_row: int = 4) -> InlineKeyboardMarkup:
    """Клавиатура для игры Квак
    player_row: текущий ряд игрока (4 - начало, 0 - финиш)
    """
    keyboard = InlineKeyboardBuilder()
    
    # Первый ряд - кнопки выбора кувшинок (всегда доступны, пока игра идёт)
    buttons = []
    for i in range(5):
        buttons.append(
            InlineKeyboardButton(
                text="🍀",
                callback_data=f"kwak_{i}|{user_id}"
            )
        )
    keyboard.row(*buttons)
    
    # Второй ряд - динамическая кнопка
    if player_row == 4:  # Начальный ряд
        btn_text = "❌ Отменить игру"
        btn_callback = f"kwak-stop|{user_id}"
    elif player_row == 0:  # Финальный ряд - можно только забрать
        btn_text = "💰 Забрать выигрыш"
        btn_callback = f"kwak-stop|{user_id}"
    else:  # Промежуточные ряды
        btn_text = "💰 Забрать"
        btn_callback = f"kwak-stop|{user_id}"
    
    keyboard.row(InlineKeyboardButton(text=btn_text, callback_data=btn_callback))
    
    return keyboard.as_markup()
