import random
import asyncio
import time
from decimal import Decimal
from aiogram import types, Dispatcher, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import bot
from assets.transform import transform_int as tr
from commands.games.db import gXX
from assets.antispam import antispam, antispam_earning, new_earning_msg
from assets.gettime import gametime
from filters.custom import StartsWith
from user import BFGuser, BFGconst

# ==================== КОНФИГУРАЦИЯ ====================
# Размеры поля
ROWS = 5
COLS = 5
TOTAL_CELLS = ROWS * COLS

# Множители выигрыша в зависимости от количества мин
MULTIPLIERS = {
    1: 1.5,   # 1 мина
    2: 2.0,   # 2 мины
    3: 2.5,   # 3 мины
    4: 3.0,   # 4 мины
    5: 4.0,   # 5 мин
    6: 5.0,   # 6 мин
    7: 6.5,   # 7 мин
    8: 8.0,   # 8 мин
}

# Словарь для хранения активных игр
games = {}

# ==================== ОСНОВНОЙ КЛАСС ИГРЫ ====================
class MinesGame:
    """Класс игры Мины"""
    
    def __init__(self, chat_id: int, user_id: int, summ: int, mines_count: int):
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_id = 0
        self.summ = summ
        self.mines_count = mines_count
        self.multiplier = MULTIPLIERS.get(mines_count, 2.0)
        
        # Создаем поле
        self.field = [['❓' for _ in range(COLS)] for _ in range(ROWS)]
        self.mines = [[False for _ in range(COLS)] for _ in range(ROWS)]
        self.opened = [[False for _ in range(COLS)] for _ in range(ROWS)]
        
        # Размещаем мины случайно
        self._place_mines()
        
        # Первый ход всегда безопасный - открываем центральную клетку
        self.first_move_done = False
        self.game_over = False
        self.won = False
        self.last_time = time.time()
        
        # Счетчик открытых безопасных клеток
        self.safe_opened = 0
        self.total_safe = TOTAL_CELLS - mines_count
    
    def _place_mines(self):
        """Размещает мины на поле"""
        positions = list(range(TOTAL_CELLS))
        random.shuffle(positions)
        
        for i in range(self.mines_count):
            pos = positions[i]
            row = pos // COLS
            col = pos % COLS
            self.mines[row][col] = True
    
    def get_cell_text(self, row: int, col: int, show_all: bool = False) -> str:
        """Возвращает текст для ячейки"""
        if show_all:
            return '💣' if self.mines[row][col] else '💎'
        
        if self.opened[row][col]:
            return '💎'  # Открытая безопасная клетка
        else:
            return '❓'  # Закрытая клетка
    
    def get_field_keyboard(self, show_all: bool = False) -> InlineKeyboardMarkup:
        """Создает клавиатуру с игровым полем"""
        builder = InlineKeyboardBuilder()
        
        # Строки поля
        for row in range(ROWS):
            row_buttons = []
            for col in range(COLS):
                if self.opened[row][col] or show_all:
                    # Если клетка открыта или показываем все
                    text = '💣' if self.mines[row][col] else '💎'
                    callback = "ignore"
                else:
                    text = '❓'
                    callback = f"mines_open_{row}_{col}|{self.user_id}"
                
                row_buttons.append(
                    InlineKeyboardButton(text=text, callback_data=callback)
                )
            builder.row(*row_buttons)
        
        # Нижняя панель с информацией
        info_row = []
        
        # Кнопка "Забрать"
        if not self.game_over and not self.won:
            info_row.append(
                InlineKeyboardButton(
                    text=f"💰 Забрать {tr(int(self.summ * self.multiplier))}$",
                    callback_data=f"mines_take|{self.user_id}"
                )
            )
        
        builder.row(*info_row)
        
        return builder.as_markup()
    
    def open_cell(self, row: int, col: int) -> dict:
        """Открывает клетку и возвращает результат"""
        result = {
            'status': 'continue',
            'message': ''
        }
        
        if self.opened[row][col] or self.game_over or self.won:
            result['status'] = 'invalid'
            return result
        
        # Открываем клетку
        self.opened[row][col] = True
        
        # Проверяем мину
        if self.mines[row][col]:
            self.game_over = True
            result['status'] = 'lose'
            result['message'] = '💥 Вы подорвались на мине!'
            return result
        
        # Увеличиваем счетчик открытых безопасных
        self.safe_opened += 1
        
        # Проверяем победу (открыты все безопасные)
        if self.safe_opened == self.total_safe:
            self.won = True
            result['status'] = 'win'
            result['message'] = '🎉 Поздравляем! Вы открыли все безопасные клетки!'
            return result
        
        result['status'] = 'continue'
        return result
    
    async def take_win(self) -> int:
        """Забирает выигрыш"""
        win_sum = int(self.summ * self.multiplier)
        # Добавляем чистый выигрыш (выигрыш минус ставка)
        await gXX(self.user_id, win_sum - self.summ, 1)
        return win_sum
    
    def get_status_text(self) -> str:
        """Возвращает текст статуса игры"""
        if self.game_over:
            return "💥 ИГРА ОКОНЧЕНА - ВЫ ПРОИГРАЛИ"
        if self.won:
            return f"🎉 ПОБЕДА! Выигрыш: {tr(int(self.summ * self.multiplier))}$"
        
        opened = self.safe_opened
        total = self.total_safe
        percent = (opened / total) * 100 if total > 0 else 0
        
        return (f"⚡️ Открыто: {opened}/{total} ({percent:.1f}%)\n"
                f"💰 Текущий множитель: x{self.multiplier}\n"
                f"💎 Возможный выигрыш: {tr(int(self.summ * self.multiplier))}$")

# ==================== ФУНКЦИЯ ВЫБОРА КОЛИЧЕСТВА МИН ====================
def get_mines_count_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для выбора количества мин"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки выбора количества мин (1-8)
    buttons = []
    for mines in range(1, 9):
        mult = MULTIPLIERS.get(mines, 2.0)
        buttons.append(
            InlineKeyboardButton(
                text=f"{mines} 💣 (x{mult})",
                callback_data=f"mines_choose_{mines}|{user_id}"
            )
        )
    
    # Располагаем по 2 кнопки в ряд
    builder.row(*buttons[:2])
    builder.row(*buttons[2:4])
    builder.row(*buttons[4:6])
    builder.row(*buttons[6:8])
    
    builder.row(InlineKeyboardButton(
        text="❌ Отмена",
        callback_data=f"mines_cancel|{user_id}"
    ))
    
    return builder.as_markup()

# ==================== ОБРАБОТЧИКИ КОМАНД ====================
@antispam
async def mines_cmd(message: types.Message, user: BFGuser):
    """Команда /mines или 'мины' - начать игру"""
    win, lose = BFGconst.emj()
    
    # Проверяем, нет ли уже активной игры
    if user.user_id in games:
        await message.answer(f'{user.url}, у вас уже есть активная игра {lose}')
        return
    
    # Проверяем ставку
    summ = await game_check(message, user, index=1)
    if not summ:
        return
    
    # Сохраняем ставку во временные данные
    games[f"temp_{user.user_id}"] = {
        'summ': summ,
        'chat_id': message.chat.id
    }
    
    # Предлагаем выбрать количество мин
    await message.answer(
        f"{user.url}, выберите количество мин на поле:\n\n"
        f"💣 Чем больше мин, тем выше множитель!\n"
        f"💰 Ваша ставка: {tr(summ)}$",
        reply_markup=get_mines_count_keyboard(user.user_id)
    )

# ==================== ФУНКЦИЯ ПРОВЕРКИ СТАВКИ ====================
async def game_check(message: types.Message, user: BFGuser, index=1) -> int | None:
    """Проверка ставки для игры"""
    win, lose = BFGconst.emj()

    try:
        # Парсим ставку
        parts = message.text.split()
        if len(parts) <= index:
            await message.answer(f'{user.url}, вы не ввели ставку для игры {lose}')
            return None
        
        if parts[index].lower() in ['все', 'всё']:
            summ = int(user.balance)
        else:
            summ = int(float(parts[index].replace('е', 'e')))
    except:
        await message.answer(f'{user.url}, вы не ввели ставку для игры {lose}')
        return None

    if int(user.balance) < summ:
        await message.answer(f'{user.url}, ваша ставка не может быть больше вашего баланса {lose}')
        return None

    if summ < 10:
        await message.answer(f'{user.url}, минимальная ставка - 10$ {lose}')
        return None

    gt = await gametime(user.id)
    if gt == 1:
        await message.answer(f'{user.url}, играть можно каждые 5 секунд. Подождите немного {lose}')
        return None

    return summ

# ==================== ОБРАБОТЧИКИ КОЛБЭКОВ ====================
@antispam_earning
async def mines_choose_callback(call: types.CallbackQuery, user: BFGuser):
    """Выбор количества мин"""
    user_id = call.from_user.id
    
    # Получаем временные данные
    temp_key = f"temp_{user_id}"
    if temp_key not in games:
        await call.answer('❌ Игра не найдена. Начните заново.')
        return
    
    temp_data = games[temp_key]
    mines_count = int(call.data.split('_')[2].split('|')[0])
    summ = temp_data['summ']
    chat_id = temp_data['chat_id']
    
    # Удаляем временные данные
    del games[temp_key]
    
    # Создаем игру
    game = MinesGame(chat_id, user_id, summ, mines_count)
    games[user_id] = game
    
    # Списываем ставку
    await gXX(user_id, summ, 0)
    
    # Первый ход - открываем центральную клетку (2,2)
    first_row = 2
    first_col = 2
    game.open_cell(first_row, first_col)
    
    # Отправляем сообщение с игрой
    text = (f"{user.url}, игра МИНЫ началась!\n\n"
            f"💰 Ставка: {tr(summ)}$\n"
            f"💣 Мин на поле: {mines_count}\n"
            f"✨ Первая клетка уже открыта!\n\n"
            f"{game.get_status_text()}")
    
    msg = await call.message.edit_text(
        text,
        reply_markup=game.get_field_keyboard()
    )
    
    await new_earning_msg(msg.chat.id, msg.message_id)
    game.message_id = msg.message_id
    await call.answer()

@antispam_earning
async def mines_open_callback(call: types.CallbackQuery, user: BFGuser):
    """Открытие клетки"""
    user_id = call.from_user.id
    game = games.get(user_id, None)
    
    if not game or game.user_id != user_id:
        await call.answer('🐸 Игра не найдена.')
        return
    
    if game.game_over or game.won:
        await call.answer('Игра уже завершена!')
        return
    
    # Получаем координаты
    data = call.data.split('_')
    row = int(data[2])
    col = int(data[3].split('|')[0])
    
    # Открываем клетку
    result = game.open_cell(row, col)
    
    if result['status'] == 'lose':
        # Проигрыш - показываем все мины
        await call.message.edit_text(
            f"{user.url}, {result['message']}\n\n"
            f"💰 Ставка: {tr(game.summ)}$ проиграна.",
            reply_markup=game.get_field_keyboard(show_all=True)
        )
        games.pop(user_id, None)
        
    elif result['status'] == 'win':
        # Победа - начисляем выигрыш
        win_sum = await game.take_win()
        await call.message.edit_text(
            f"{user.url}, {result['message']}\n\n"
            f"💰 Ваш выигрыш: {tr(win_sum)}$",
            reply_markup=game.get_field_keyboard(show_all=True)
        )
        games.pop(user_id, None)
        
    else:
        # Продолжаем игру
        text = (f"{user.url}, игра продолжается!\n\n"
                f"💰 Ставка: {tr(game.summ)}$\n"
                f"💣 Мин на поле: {game.mines_count}\n\n"
                f"{game.get_status_text()}")
        
        await call.message.edit_text(
            text,
            reply_markup=game.get_field_keyboard()
        )
    
    await call.answer()

@antispam_earning
async def mines_take_callback(call: types.CallbackQuery, user: BFGuser):
    """Забрать выигрыш досрочно"""
    user_id = call.from_user.id
    game = games.get(user_id, None)
    
    if not game or game.user_id != user_id:
        await call.answer('🐸 Игра не найдена.')
        return
    
    if game.game_over or game.won:
        await call.answer('Игра уже завершена!')
        return
    
    win, lose = BFGconst.emj()
    win_sum = await game.take_win()
    
    await call.message.edit_text(
        f"{user.url}, вы забрали выигрыш досрочно!\n\n"
        f"💰 Ваш выигрыш: {tr(win_sum)}$\n"
        f"💣 Открыто клеток: {game.safe_opened}/{game.total_safe}",
        reply_markup=game.get_field_keyboard(show_all=True)
    )
    
    games.pop(user_id, None)
    await call.answer()

@antispam_earning
async def mines_cancel_callback(call: types.CallbackQuery, user: BFGuser):
    """Отмена выбора мин"""
    user_id = call.from_user.id
    temp_key = f"temp_{user_id}"
    
    if temp_key in games:
        del games[temp_key]
    
    await call.message.edit_text(f"{user.url}, выбор отменён.")
    await call.answer()

async def mines_ignore_callback(call: types.CallbackQuery):
    """Игнорирование нажатий на открытые клетки"""
    await call.answer()

# ==================== ПРОВЕРКА НЕАКТИВНЫХ ИГР ====================
async def check_mines_games():
    """Проверка неактивных игр (каждые 30 секунд)"""
    while True:
        current_time = time.time()
        to_remove = []
        
        for user_id, game in list(games.items()):
            # Пропускаем временные данные
            if isinstance(user_id, str) and user_id.startswith('temp_'):
                if current_time > game.get('time', 0) + 120:  # 2 минуты
                    to_remove.append(user_id)
                continue
            
            # Проверяем активные игры
            if current_time > game.last_time + 180:  # 3 минуты бездействия
                to_remove.append(user_id)
                try:
                    # Возвращаем ставку
                    await gXX(user_id, game.summ, 1)
                    await bot.send_message(
                        game.chat_id,
                        f'⚠️ <b>Игра отменена из-за бездействия!</b>\n'
                        f'💰 Ваша ставка {tr(game.summ)}$ возвращена.',
                        reply_to_message_id=game.message_id
                    )
                except:
                    pass
        
        for user_id in to_remove:
            games.pop(user_id, None)
        
        await asyncio.sleep(30)

# Запуск фоновой проверки
loop = asyncio.get_event_loop()
if not loop.is_running():
    loop.create_task(check_mines_games())
else:
    asyncio.create_task(check_mines_games())

# ==================== РЕГИСТРАЦИЯ ХЭНДЛЕРОВ ====================
def reg(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    # Команды
    dp.message.register(mines_cmd, StartsWith('мины'))
    dp.message.register(mines_cmd, StartsWith('/mines'))
    
    # Колбэки выбора мин
    dp.callback_query.register(mines_choose_callback, F.data.startswith('mines_choose_'))
    dp.callback_query.register(mines_cancel_callback, F.data.startswith('mines_cancel'))
    
    # Игровые колбэки
    dp.callback_query.register(mines_open_callback, F.data.startswith('mines_open_'))
    dp.callback_query.register(mines_take_callback, F.data.startswith('mines_take'))
    dp.callback_query.register(mines_ignore_callback, F.data == 'ignore')

