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
    'balance': ['💰 Деньги', '$'],
    'energy': ['⚡️ Энергия', '⚡️'],
    'yen': ['💴 Йены', '💴'],
    'exp': ['💡 Опыт', '💡'],
    'ecoins': ['💳 B-coins', '💳'],
    'corn': ['🥜 Зерна', '🥜'],
    'biores': ['☣️ Биоресурсы', '☣️'],
    'matter': ['🌌 Материя', '🌌'],
}

# ==================== FSM СОСТОЯНИЯ ====================
class SetRefSummState(StatesGroup):
    column = State()
    summ = State()

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def settings_kb() -> InlineKeyboardMarkup:
    """Клавиатура настроек реферальной системы"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="✍️ Изменить награду",
        callback_data="ref_edit_prize"
    ))
    return builder.as_markup()

def select_values_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора валюты"""
    builder = InlineKeyboardBuilder()
    buttons = []
    for key, value in CONFIG_VALUES.items():
        buttons.append(InlineKeyboardButton(
            text=value[0],
            callback_data=f"ref_set_prize_{key}"
        ))
    builder.row(*buttons, width=2)
    builder.row(InlineKeyboardButton(
        text="❌ Закрыть",
        callback_data="ref_dell"
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
            summ = 1000000  # 1 миллион стартовая награда
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
        
        # Формируем название валюты
        currency_name = CONFIG_VALUES[column][0] if column in CONFIG_VALUES else "💰 Деньги"
        currency_symbol = CONFIG_VALUES[column][1] if column in CONFIG_VALUES else "$"
        
        text = f'''🔗 <b>Твоя реферальная ссылка:</b>
https://t.me/{cfg.bot_username}?start=r{user.game_id}

<code>·······························</code>
{user.url}, приглашай друзей и получай {tr(int(summ))}{currency_symbol}

👥 <b>Твои рефералы:</b> {data[1]} чел.
💰 <b>Заработано:</b> {tr(int(data[2]))}{currency_symbol}'''
        
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
        currency_name = CONFIG_VALUES[column][0] if column in CONFIG_VALUES else "💰 Деньги"
        currency_symbol = CONFIG_VALUES[column][1] if column in CONFIG_VALUES else "$"
        
        await message.answer(
            f'{user.url}, текущая награда за реферала:\n'
            f'{tr(int(summ))}{currency_symbol} ({currency_name})',
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
        reply_markup=select_values_kb()
    )
    await call.answer()

async def ref_set_prize_callback(call: types.CallbackQuery, state: FSMContext):
    """Выбор конкретной валюты"""
    prize = call.data.split('_')[3]  # ref_set_prize_balance
    currency_name = CONFIG_VALUES[prize][0]
    
    await call.message.edit_text(
        f'👥 Введите сумму награды ({currency_name}):\n\n'
        f'<i>Для отмены введите "-"</i>'
    )
    await state.update_data(column=prize)
    await SetRefSummState.summ.set()
    await call.answer()

# ==================== FSM ОБРАБОТЧИК ====================
async def enter_summ_handler(message: types.Message, state: FSMContext):
    """Ввод суммы награды"""
    if message.text == '-':
        await state.clear()
        await message.answer('❌ Отменено.')
        return

    try:
        summ = int(message.text.replace(' ', ''))
    except:
        await message.answer('❌ Введите целое число.')
        return

    if summ <= 0:
        await message.answer('❌ Сумма должна быть больше 0.')
        return

    data = await state.get_data()
    column = data.get('column', 'balance')
    currency_name = CONFIG_VALUES[column][0]
    currency_symbol = CONFIG_VALUES[column][1]
    
    await db.upd_settings(summ, column)
    await state.clear()
    
    win, lose = BFGconst.emj()
    await message.answer(
        f'{win} Установлена новая награда за реферала:\n'
        f'{tr(summ)}{currency_symbol} ({currency_name})'
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
        
        # Начисляем награду
        if column == 'balance':
            main_cursor.execute(
                'UPDATE users SET balance = balance + ? WHERE user_id = ?', 
                (summ, real_id)
            )
            main_conn.commit()
            
            # Уведомляем
            currency_symbol = CONFIG_VALUES[column][1]
            await bot.send_message(
                real_id,
                f'🥰 <b>По вашей ссылке зарегистрировался новый пользователь!</b>\n'
                f'На ваш баланс зачислено {tr(summ)}{currency_symbol}'
            )

        # Записываем реферала
        await db.new_ref(real_id, summ)

    except Exception as e:
        print('Ошибка в реферальной системе:', e)

# ==================== РЕГИСТРАЦИЯ ====================
def reg(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    # Команды
    dp.message.register(ref_cmd, StartsWith('реф'))
    dp.message.register(ref_cmd, StartsWith('/ref'))
    dp.message.register(ref_settings_cmd, StartsWith('/refsetting'))

    # Колбэки (исправлены callback_data)
    dp.callback_query.register(ref_dell_callback, F.data == 'ref_dell')
    dp.callback_query.register(ref_edit_prize_callback, F.data == 'ref_edit_prize')
    dp.callback_query.register(ref_set_prize_callback, F.data.startswith('ref_set_prize_'))

    # FSM (без антиспама, т.к. это состояние)
    dp.message.register(enter_summ_handler, SetRefSummState.summ)
