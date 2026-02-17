import sqlite3
import os
from decimal import Decimal
from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import bot
from assets.antispam import antispam, admin_only
from assets.transform import transform_int as tr
from commands.db import cursor as main_cursor, conn as main_conn
from user import BFGuser, BFGconst
import config as cfg
from filters.custom import StartsWith

# ==================== КОНФИГУРАЦИЯ ====================
CONFIG_VALUES = {
    'balance': ['user.balance', '$', ['', '', ''], '💰 Деньги'],
    'energy': ['user.energy', '⚡️', ['энергия', 'энергии', 'энергий'], '⚡️ Энергия'],
    'yen': ['user.yen', '💴', ['йена', 'йены', 'йен'], '💴 Йены'],
    'exp': ['user.exp', '💡', ['опыт', 'опыта', 'опытов'], '💡 Опыт'],
    'ecoins': ['user.bcoins', '💳', ['B-coin', 'B-coins', 'B-coins'], '💳 B-coins'],
    'corn': ['user.corn', '🥜', ['зерно', 'зерна', 'зёрен'], '🥜 Зерна'],
    'biores': ['user.biores', '☣️', ['биоресурс', 'биоресурса', 'биоресурсов'], '☣️ Биоресурсы'],
    'matter': ['user.mine.matter', '🌌', ['материя', 'материи', 'материй'], '🌌 Материя'],
}

# ==================== FSM СОСТОЯНИЯ ====================
class SetRefSummState(StatesGroup):
    column = State()
    summ = State()

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def get_form(number: int, forms: list[str]) -> str:
    """Склонение слов после чисел"""
    number = abs(int(number)) % 100
    if 11 <= number <= 19:
        return forms[2]
    last_digit = number % 10
    if last_digit == 1:
        return forms[0]
    if 2 <= last_digit <= 4:
        return forms[1]
    return forms[2]

def freward(key: str, amount: int) -> str:
    """Форматирование награды с валютой"""
    config = CONFIG_VALUES[key]
    symbol = config[1]
    forms = config[2]
    word_form = get_form(amount, forms)
    return f"{tr(amount)}{symbol} {word_form}"

def settings_kb() -> InlineKeyboardMarkup:
    """Клавиатура настроек реферальной системы"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="✍️ Изменить награду",
        callback_data="ref-edit-prize"
    ))
    return builder.as_markup()

def select_values() -> InlineKeyboardMarkup:
    """Клавиатура выбора валюты"""
    builder = InlineKeyboardBuilder()
    buttons = []
    for key, value in CONFIG_VALUES.items():
        buttons.append(InlineKeyboardButton(
            text=value[3],
            callback_data=f"ref-set-prize_{key}"
        ))
    builder.row(*buttons, width=3)
    builder.row(InlineKeyboardButton(
        text="❌ Закрыть",
        callback_data="ref-dell"
    ))
    return builder.as_markup()

# ==================== РАБОТА С БАЗОЙ ДАННЫХ ====================
class Database:
    def __init__(self):
        os.makedirs('modules/temp', exist_ok=True)
        self.conn = sqlite3.connect('modules/temp/referrals.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self) -> None:
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                ref INTEGER DEFAULT 0,
                balance TEXT DEFAULT '0'
            )''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                summ TEXT,
                column TEXT
            )''')

        settings = self.cursor.execute('SELECT * FROM settings').fetchone()
        if not settings:
            summ = 1_000_000_000_000_000  # Стартовая награда как в оригинале
            self.cursor.execute('INSERT INTO settings (summ, column) VALUES (?, ?)',
                              (summ, 'balance'))
            self.conn.commit()

    async def upd_settings(self, summ: int, column: str) -> None:
        self.cursor.execute('UPDATE settings SET summ = ?, column = ?', (summ, column))
        self.cursor.execute('UPDATE users SET balance = 0')
        self.conn.commit()

    async def reg_user(self, user_id: int) -> None:
        ex = self.cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,)).fetchone()
        if not ex:
            self.cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
            self.conn.commit()

    async def get_info(self, user_id: int) -> tuple:
        await self.reg_user(user_id)
        return self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()

    async def get_summ(self) -> tuple:
        return self.cursor.execute('SELECT summ, column FROM settings').fetchone()

    async def new_ref(self, user_id: int, summ: int) -> None:
        await self.reg_user(user_id)
        rbalance = self.cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]
        
        new_rbalance = Decimal(str(rbalance)) + Decimal(str(summ))
        new_rbalance = "{:.0f}".format(new_rbalance)
        
        self.cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_rbalance, user_id))
        self.cursor.execute('UPDATE users SET ref = ref + 1 WHERE user_id = ?', (user_id,))
        self.conn.commit()

db = Database()

# ==================== ОБРАБОТЧИКИ КОМАНД ====================
@antispam
async def ref_cmd(message: types.Message, user: BFGuser):
    """Команда реф - показать реферальную ссылку"""
    win, lose = BFGconst.emj()
    
    try:
        summ, column = await db.get_summ()
        data = await db.get_info(user.id)
        
        text = f'''https://t.me/{cfg.bot_username}?start=r{user.game_id}
<code>·······························</code>
{user.url}, твоя реферальная ссылка, можешь поделиться и получить {freward(column, int(summ))}

👥 <i>Твои рефералы</i>
<b>• {data[1]} чел.</b>
✨ <i>Заработано с рефералов:</i>
<b>• {freward(column, int(data[2]))}</b>'''
        
        await message.answer(text)
    except Exception as e:
        print(f"Ошибка в ref_cmd: {e}")
        await message.answer(f"{user.url}, произошла ошибка {lose}")

@antispam
@admin_only(private=True)
async def ref_settings_cmd(message: types.Message, user: BFGuser):
    """Команда /refsetting для администраторов"""
    win, lose = BFGconst.emj()
    
    try:
        summ, column = await db.get_summ()
        await message.answer(
            f'{user.url}, текущая награда за реферала - {freward(column, int(summ))}',
            reply_markup=settings_kb()
        )
    except Exception as e:
        print(f"Ошибка в ref_settings_cmd: {e}")
        await message.answer(f"{user.url}, произошла ошибка {lose}")

# ==================== ОБРАБОТЧИКИ КОЛБЭКОВ ====================
async def ref_dell_callback(call: types.CallbackQuery):
    """Закрыть меню настроек"""
    try:
        await call.message.delete()
    except:
        pass
    await call.answer()

async def ref_edit_prize_callback(call: types.CallbackQuery):
    """Выбор валюты для награды"""
    await call.message.edit_text(
        '👥 <b>Выберите валюту для награды:</b>',
        reply_markup=select_values()
    )
    await call.answer()

async def ref_set_prize_callback(call: types.CallbackQuery, state: FSMContext):
    """Выбор конкретной валюты"""
    prize = call.data.split('_')[1]  # ref-set-prize_balance
    await call.message.edit_text(
        f'👥 Введите сумму награды ({CONFIG_VALUES[prize][3]}):\n\n'
        f'<i>Для отмены введите "-"</i>'
    )
    await state.update_data(column=prize)
    await SetRefSummState.summ.set()
    await call.answer()

async def enter_summ_handler(message: types.Message, state: FSMContext):
    """Ввод суммы награды"""
    if message.text == '-':
        await state.clear()
        await message.answer('❌ Отменено.')
        return

    try:
        summ = int(message.text)
    except:
        await message.answer('❌ Введите целое число.')
        return

    if summ <= 0:
        await message.answer('❌ Ты серьёзно?')
        return

    data = await state.get_data()
    await db.upd_settings(summ, data['column'])
    await state.clear()
    
    win, lose = BFGconst.emj()
    await message.answer(
        f'{win} Установлена новая награда за реферала: {freward(data["column"], summ)}'
    )

# ==================== ОБРАБОТЧИК СОБЫТИЯ СТАРТА ====================
async def on_start_event(event_data: dict):
    """Обработчик реферальных ссылок"""
    try:
        message = event_data['message']
        user_id = message.from_user.id
        text = message.text

        if not text or not text.startswith('/start r'):
            return

        r_id = int(text.split('/start r')[1])
        summ, column = await db.get_summ()

        # Проверки
        if user_id == r_id:
            return

        real_id_row = main_cursor.execute(
            'SELECT user_id FROM users WHERE game_id = ?', 
            (r_id,)
        ).fetchone()
        
        if not real_id_row:
            return

        user_exists = main_cursor.execute(
            'SELECT user_id FROM users WHERE user_id = ?', 
            (user_id,)
        ).fetchone()
        
        if user_exists:
            return

        real_id = real_id_row[0]
        
        # Начисляем награду как в оригинале
        user = BFGuser(not_class=real_id)
        await user.update()
        
        # Используем eval как в оригинале для совместимости
        await eval(CONFIG_VALUES[column][0]).upd(summ, '+')
        
        # Записываем реферала
        await db.new_ref(real_id, summ)

        # Уведомляем
        await bot.send_message(
            real_id,
            f'🥰 <b>Спасибо за приглашение!</b>\nНа ваш баланс зачислено {freward(column, summ)}'
        )

    except Exception as e:
        print('Ошибка в реферальной системе:', e)

# ==================== РЕГИСТРАЦИЯ ====================
def reg(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    # Команды
    dp.message.register(ref_cmd, StartsWith('реф'))
    dp.message.register(ref_cmd, StartsWith('/ref'))
    dp.message.register(ref_settings_cmd, StartsWith('/refsetting'))

    # Колбэки (callback_data как в оригинале)
    dp.callback_query.register(ref_dell_callback, F.data == 'ref-dell')
    dp.callback_query.register(ref_edit_prize_callback, F.data == 'ref-edit-prize')
    dp.callback_query.register(ref_set_prize_callback, F.data.startswith('ref-set-prize_'))

    # FSM
    dp.message.register(enter_summ_handler, SetRefSummState.summ)

