import sqlite3
import os
from decimal import Decimal
from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import bot
from assets.antispam import antispam, admin_only, antispam_earning
from assets.transform import transform_int as tr
from commands.db import cursor as main_cursor, conn as main_conn
from user import BFGuser
import config as cfg
import assets.keyboards as kb  # Импортируем общие клавиатуры

# ==================== КОНФИГУРАЦИЯ ====================
# Добавляем команду в help (если у вас есть такая система)
# from commands.help import CONFIG
# CONFIG['help_osn'] = CONFIG.get('help_osn', '') + '\n   👥 Реф'

# Словарь доступных валют для награды
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

def settings_kb(top: int) -> InlineKeyboardMarkup:
    """Клавиатура настроек реферальной системы"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="✍️ Изменить награду",
        callback_data="ref-edit-prize"
    ))
    txt = '➕ Добавить топ рефаводов' if top == 0 else '❌ Удалить топ рефаводов'
    builder.row(InlineKeyboardButton(
        text=txt,
        callback_data="ref-edit-top"
    ))
    return builder.as_markup()

def select_values() -> InlineKeyboardMarkup:
    """Клавиатура выбора валюты для награды"""
    builder = InlineKeyboardBuilder()
    buttons = []
    for key, value in CONFIG_VALUES.items():
        buttons.append(InlineKeyboardButton(
            text=value[3],
            callback_data=f'ref-set-prize_{key}'
        ))
    builder.row(*buttons, width=3)
    builder.row(InlineKeyboardButton(
        text="❌ Закрыть",
        callback_data="ref-dell"
    ))
    return builder.as_markup()

def top_substitution_kb(user_id: int, tab: str) -> InlineKeyboardMarkup:
    """Замена для стандартной топ-клавиатуры"""
    builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton("👑 Топ рейтинга", callback_data=f"top-rating|{user_id}|{tab}"),
        InlineKeyboardButton("💰 Топ денег", callback_data=f"top-balance|{user_id}|{tab}"),
        InlineKeyboardButton("🧰 Топ ферм", callback_data=f"top-cards|{user_id}|{tab}"),
        InlineKeyboardButton("🗄 Топ бизнесов", callback_data=f"top-bsterritory|{user_id}|{tab}"),
        InlineKeyboardButton("🏆 Топ опыта", callback_data=f"top-exp|{user_id}|{tab}"),
        InlineKeyboardButton("💴 Топ йен", callback_data=f"top-yen|{user_id}|{tab}"),
        InlineKeyboardButton("📦 Топ обычных кейсов", callback_data=f"top-case1|{user_id}|{tab}"),
        InlineKeyboardButton("🏵 Топ золотых кейсов", callback_data=f"top-case2|{user_id}|{tab}"),
        InlineKeyboardButton("🏺 Топ рудных кейсов", callback_data=f"top-case3|{user_id}|{tab}"),
        InlineKeyboardButton("🌌 Топ материальных кейсов", callback_data=f"top-case4|{user_id}|{tab}"),
        InlineKeyboardButton("👥 Топ рефаводов", callback_data=f"ref-top|{user_id}|{tab}"),
    ]
    builder.row(*buttons, width=2)
    return builder.as_markup()

# ==================== РАБОТА С БАЗОЙ ДАННЫХ ====================
class Database:
    def __init__(self):
        # Создаём папку для базы данных, если её нет
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
                column TEXT,
                rtop INTEGER DEFAULT 1
            )''')

        # Проверяем, есть ли настройки, если нет — создаём
        rtop_row = self.cursor.execute('SELECT rtop FROM settings').fetchone()
        if not rtop_row:
            summ = 100_000_000
            self.cursor.execute('INSERT INTO settings (summ, column, rtop) VALUES (?, ?, ?)',
                              (summ, 'balance', 1))
            self.conn.commit()
            rtop = 1
        else:
            rtop = rtop_row[0]

        # Обновляем глобальную клавиатуру (сохраняем оригинал)
        global original_kb
        original_kb = kb.top
        self.upd_keyboards(rtop)

    def upd_keyboards(self, rtop: int) -> None:
        """Обновляет глобальную топ-клавиатуру"""
        if rtop == 0:
            kb.top = original_kb
        else:
            # Временно, пока не передадим user_id и tab
            kb.top = lambda user_id, tab: top_substitution_kb(user_id, tab)

    async def upd_settings(self, summ: int, column: str) -> None:
        self.cursor.execute('UPDATE settings SET summ = ?, column = ?', (summ, column))
        self.cursor.execute('UPDATE users SET balance = 0')  # Обнуляем баланс рефералов
        self.conn.commit()

    async def upd_rtop(self, rtop: int) -> None:
        self.cursor.execute('UPDATE settings SET rtop = ?', (rtop,))
        self.conn.commit()
        self.upd_keyboards(rtop)

    async def get_rtop(self) -> int:
        return self.cursor.execute('SELECT rtop FROM settings').fetchone()[0]

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

    async def upd_summ(self, summ: int) -> None:
        summ = "{:.0f}".format(summ)
        self.cursor.execute('UPDATE settings SET summ = ?', (summ,))
        self.conn.commit()

    async def new_ref(self, user_id: int, summ: int) -> None:
        await self.reg_user(user_id)
        rbalance = self.cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]

        new_rbalance = Decimal(str(rbalance)) + Decimal(str(summ))
        new_rbalance = "{:.0f}".format(new_rbalance)

        self.cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (new_rbalance, user_id))
        self.cursor.execute('UPDATE users SET ref = ref + 1 WHERE user_id = ?', (user_id,))
        self.conn.commit()

    async def get_top(self) -> list:
        data = self.cursor.execute('SELECT user_id, ref FROM users ORDER BY ref DESC LIMIT 10').fetchall()
        users = []
        for user_id, ref in data:
            name = main_cursor.execute("SELECT name FROM users WHERE user_id = ?", (user_id,)).fetchone()
            if name:
                users.append((user_id, ref, name[0]))
        return users

# Инициализация базы данных
db = Database()
original_kb = None  # Будет заполнено в create_tables

# ==================== ОБРАБОТЧИКИ КОМАНД ====================
@antispam
async def ref_cmd(message: types.Message, user: BFGuser):
    """Команда /ref или 'реф' - показать реферальную ссылку"""
    summ, column = await db.get_summ()
    data = await db.get_info(user.id)
    text = f'''https://t.me/{cfg.bot_username}?start=r{user.game_id}
<code>·······························</code>
{user.url}, твоя реферальная ссылка, можешь поделиться и получить {freward(column, summ)}

👥 <i>Твои рефералы</i>
<b>• {data[1]} чел.</b>
✨ <i>Заработано с рефералов:</i>
<b>• {freward(column, data[2])}</b>'''
    await message.answer(text)

@antispam
@admin_only(private=True)
async def ref_settings_cmd(message: types.Message, user: BFGuser):
    """Команда /refsetting для администраторов"""
    summ, column = await db.get_summ()
    top = await db.get_rtop()
    await message.answer(
        f'{user.url}, текущая награда за реферала - {freward(column, summ)}',
        reply_markup=settings_kb(top)
    )

# ==================== ОБРАБОТЧИКИ КОЛБЭКОВ ====================
async def ref_dell_callback(call: types.CallbackQuery):
    """Удаление сообщения с настройками"""
    try:
        await call.message.delete()
    except Exception:
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
    """Выбор конкретной валюты и запрос суммы"""
    prize = call.data.split('_')[1]
    await call.message.edit_text(
        f'👥 Введите сумму награды ({CONFIG_VALUES[prize][3]}):\n\n<i>Для отмены введите "-"</i>'
    )
    await state.update_data(column=prize)
    await SetRefSummState.summ.set()
    await call.answer()

async def enter_summ_handler(message: types.Message, state: FSMContext):
    """Ввод суммы награды"""
    if message.text == '-':
        await state.clear()
        await message.answer('Отменено.')
        return

    try:
        summ = int(message.text)
    except ValueError:
        await message.answer('Введите целое число.')
        return

    if summ <= 0:
        await message.answer('Ты серьёзно?')
        return

    data = await state.get_data()
    await db.upd_settings(summ, data['column'])
    await state.clear()
    await message.answer(
        f'✅ Установлена новая награда за реферала: {freward(data["column"], summ)}'
    )

async def ref_edit_top_callback(call: types.CallbackQuery):
    """Включение/выключение топа рефералов в основной топ-клавиатуре"""
    top = await db.get_rtop()
    new_top = 1 if top == 0 else 0
    await db.upd_rtop(new_top)
    await call.message.edit_reply_markup(reply_markup=settings_kb(new_top))
    await call.answer()

@antispam_earning
async def ref_top_callback(call: types.CallbackQuery, user: BFGuser):
    """Показ топа рефералов"""
    top = await db.get_top()
    tab = call.data.split('|')[2]

    if tab == 'ref':
        return

    text = f"{user.url}, топ 10 игроков бота по рефералам:\n"
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "1️⃣0️⃣"]

    for i, player in enumerate(top[:10], start=1):
        emj = emojis[i - 1]
        text += f"{emj} {player[2]} — {player[1]}👥\n"

    await call.message.edit_text(
        text=text,
        reply_markup=kb.top(user.id, 'ref'),
        disable_web_page_preview=True
    )
    await call.answer()

# ==================== ОБРАБОТЧИК СОБЫТИЯ СТАРТА ====================
async def on_start_event(event_data: dict):
    """Обработчик события запуска бота для проверки реферальных ссылок"""
    try:
        message = event_data['message']
        user_id = message.from_user.id
        text = message.text

        if not text or not text.startswith('/start r'):
            return

        r_id = int(text.split('/start r')[1])
        summ, column = await db.get_summ()

        # Проверяем, что реферал не пригласил сам себя
        if user_id == r_id:
            return

        # Проверяем, существует ли пригласивший
        real_id_row = main_cursor.execute('SELECT user_id FROM users WHERE game_id = ?', (r_id,)).fetchone()
        if not real_id_row:
            return

        # Проверяем, что приглашённый ещё не зарегистрирован
        user_exists = main_cursor.execute('SELECT game_id FROM users WHERE user_id = ?', (user_id,)).fetchone()
        if user_exists:
            return

        # Начисляем награду пригласившему
        real_id = real_id_row[0]
        referrer = BFGuser(not_class=real_id)
        await referrer.update()

        # Обновляем баланс пригласившего (eval осторожно, но в исходном коде так)
        # В реальном проекте лучше использовать прямые функции
        await eval(CONFIG_VALUES[column][0]).upd(summ, '+')

        # Записываем реферала в нашу базу
        await db.new_ref(real_id, summ)

        # Уведомляем пригласившего
        await bot.send_message(
            real_id,
            f'🥰 <b>Спасибо за приглашение!</b>\nНа ваш баланс зачислено {freward(column, summ)}'
        )
    except Exception as e:
        print('Ошибка в реферальной системе:', e)

# ==================== РЕГИСТРАЦИЯ ХЭНДЛЕРОВ ====================
def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков для aiogram 3.x"""
    # Команды
    dp.message.register(ref_cmd, F.text.lower().in_(['реф', '/ref']))
    dp.message.register(ref_settings_cmd, F.text == '/refsetting')

    # Колбэки настроек
    dp.callback_query.register(ref_dell_callback, F.data == 'ref-dell')
    dp.callback_query.register(ref_edit_prize_callback, F.data == 'ref-edit-prize')
    dp.callback_query.register(ref_set_prize_callback, F.data.startswith('ref-set-prize_'))
    dp.callback_query.register(ref_edit_top_callback, F.data.startswith('ref-edit-top'))
    dp.callback_query.register(ref_top_callback, F.data.startswith('ref-top'))
    # FSM обработчик
    dp.message.register(enter_summ_handler, SetRefSummState.summ)

