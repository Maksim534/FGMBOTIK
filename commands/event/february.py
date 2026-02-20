import asyncio
import random
import sqlite3
import time
from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import bot
from assets.antispam import antispam, antispam_earning, new_earning_msg
from assets.gettime import gametime  # Или check_time, если она у вас есть. В исходном коде была check_time, но в вашем проекте я вижу gametime. Уточните, какая функция используется.
from commands.db import cursor, get_name # get_name может быть из commands.db
import config as cfg
from user import BFGuser

VALENTINE_PHOTO = 'https://i.ibb.co/q3c9hfZM/photo-2025-02-17-14-17-28.jpg'

# Словари для временных ограничений
get_valentine_time = {}
give_valentine_time = {}
active_date = {}
date_time = {}

class ValentineState(StatesGroup):
    recipient_id = State()
    anonymous = State()
    message = State()

# ==================== КЛАВИАТУРЫ ====================
def select_mod(recipient_id: int) -> InlineKeyboardMarkup:
    """Клавиатура выбора режима отправки"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='🥷 Инкогнито', callback_data=f'send_valentine_{recipient_id}_1'),
        InlineKeyboardButton(text='😍 Признаться открыто', callback_data=f'send_valentine_{recipient_id}_0'),
    )
    return builder.as_markup()

def valentine_menu(user_id: int) -> InlineKeyboardMarkup:
    """Главное меню валентинок"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='📊 Топ Валентинок', callback_data=f'valentine_top_{user_id}'),
        InlineKeyboardButton(text='💝 Мои Валентинки', callback_data=f'my_valentine_list_1_{user_id}'),
    )
    return builder.as_markup()

def my_valentine_pagination_kb(user_id: int, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Клавиатура пагинации для списка полученных валентинок"""
    builder = InlineKeyboardBuilder()
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text='‹', callback_data=f'my_valentine_list_{page-1}_{user_id}'))
    else:
        nav_buttons.append(InlineKeyboardButton(text='•', callback_data='ignore'))
    
    nav_buttons.append(InlineKeyboardButton(text=f'{page}/{total_pages}', callback_data='ignore'))
    
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text='›', callback_data=f'my_valentine_list_{page+1}_{user_id}'))
    else:
        nav_buttons.append(InlineKeyboardButton(text='•', callback_data='ignore'))
    
    builder.row(*nav_buttons)
    builder.row(InlineKeyboardButton(text='🔝 В начало', callback_data=f'my_valentine_menu_{user_id}'))
    return builder.as_markup()

def back_to_menu_kb(user_id: int) -> InlineKeyboardMarkup:
    """Кнопка возврата в меню"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='🔙 Назад', callback_data=f'my_valentine_menu_{user_id}'))
    return builder.as_markup()

def invite_to_date_kb(user_id: int, recipient_id: int) -> InlineKeyboardMarkup:
    """Клавиатура приглашения на свидание"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='✅ Да', callback_data=f'event_date_yes_{user_id}_{recipient_id}'),
        InlineKeyboardButton(text='❌ Нет', callback_data=f'event_date_no_{user_id}_{recipient_id}'),
    )
    return builder.as_markup()

# ==================== РАБОТА С БАЗОЙ ДАННЫХ ====================
async def check_user_by_game_id(game_id: int) -> int | None:
    """Проверка существования пользователя по game_id, возвращает user_id"""
    result = cursor.execute('SELECT user_id FROM users WHERE game_id = ?', (game_id,)).fetchone()
    return result[0] if result else None

class Database:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('modules/temp/14_february.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self) -> None:
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                valentine INTEGER DEFAULT 0,
                sent_valentines INTEGER DEFAULT 0,
                obtained_valentines INTEGER DEFAULT 0,
                lucky_dates INTEGER DEFAULT 0,
                unlucky_dates INTEGER DEFAULT 0
        )''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS valentine (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender INTEGER,
                receiver INTEGER,
                anonymous INTEGER,
                message TEXT
        )''')
        self.conn.commit()

    async def register_user(self, user_id: int) -> None:
        if not self.cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,)).fetchone():
            self.cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
            self.conn.commit()

    async def get_info(self, user_id: int) -> tuple:
        await self.register_user(user_id)
        return self.cursor.execute('SELECT valentine, sent_valentines, obtained_valentines, lucky_dates, unlucky_dates FROM users WHERE user_id = ?', (user_id,)).fetchone()

    async def issue_valentine(self, user_id: int, amount: int = 1) -> None:
        await self.register_user(user_id)
        self.cursor.execute('UPDATE users SET valentine = valentine + ? WHERE user_id = ?', (amount, user_id))
        self.conn.commit()

    async def new_valentine(self, user_id: int, recipient_id: int, anonymous: int, message: str) -> None:
        await self.register_user(recipient_id)
        self.cursor.execute('INSERT INTO valentine (sender, receiver, anonymous, message) VALUES (?, ?, ?, ?)', (user_id, recipient_id, anonymous, message))
        self.cursor.execute('UPDATE users SET obtained_valentines = obtained_valentines + 1 WHERE user_id = ?', (recipient_id,))
        self.cursor.execute('UPDATE users SET sent_valentines = sent_valentines + 1 WHERE user_id = ?', (user_id,))
        self.cursor.execute('UPDATE users SET valentine = valentine - 1 WHERE user_id = ?', (user_id,))
        self.conn.commit()

    async def get_user_valentines(self, user_id: int) -> list:
        return self.cursor.execute('SELECT sender, anonymous, message FROM valentine WHERE receiver = ?', (user_id,)).fetchall()

    async def get_top_valentine(self) -> list:
        # Исправлено: ORDER BY obtained_valentines DESC
        return self.cursor.execute('SELECT user_id, obtained_valentines FROM users ORDER BY obtained_valentines DESC LIMIT 10').fetchall()

    async def update_date_info(self, user_id: int, success: bool) -> None:
        if success:
            self.cursor.execute('UPDATE users SET lucky_dates = lucky_dates + 1 WHERE user_id = ?', (user_id,))
        else:
            self.cursor.execute('UPDATE users SET unlucky_dates = unlucky_dates + 1 WHERE user_id = ?', (user_id,))
        self.conn.commit()

db = Database()

# ==================== ОБРАБОТЧИКИ КОМАНД ====================

@antispam_earning
async def my_valentine_menu_callback(call: types.CallbackQuery, user: BFGuser):
    """Возврат в главное меню валентинок"""
    text = await get_my_valentine_text(user.id)
    await call.message.edit_caption(caption=text, reply_markup=valentine_menu(user.id))
    await call.answer()

@antispam_earning
async def my_valentine_list_callback(call: types.CallbackQuery, user: BFGuser):
    """Просмотр списка полученных валентинок"""
    data_parts = call.data.split('_')
    page = int(data_parts[3])
    valentines = await db.get_user_valentines(user.id)

    if not valentines:
        await call.message.edit_caption(
            caption='💔 У вас пока нет полученных валентинок.',
            reply_markup=back_to_menu_kb(user.id)
        )
        await call.answer()
        return

    total_pages = (len(valentines) + 4) // 5
    if page < 1 or page > total_pages:
        page = 1

    v = valentines[page - 1]
    sender_id, anonymous, msg_text = v
    sender_name = "Аноним" if anonymous else f"ID {sender_id}"  # Здесь можно использовать get_name

    text = f'''<b>💌 Валентинка #{page}</b>\n\n<b>От:</b> {sender_name}\n<b>Сообщение:</b> "{msg_text}"'''
    await call.message.edit_caption(
        caption=text,
        reply_markup=my_valentine_pagination_kb(user.id, page, total_pages)
    )
    await call.answer()

@antispam_earning
async def valentine_top_callback(call: types.CallbackQuery, user: BFGuser):
    """Топ полученных валентинок"""
    top_users = await db.get_top_valentine()
    if not top_users:
        await call.message.edit_caption(caption='📊 Топ пока пуст.', reply_markup=back_to_menu_kb(user.id))
        await call.answer()
        return

    text = "🏆 <b>Топ полученных валентинок</b>\n\n"
    emojis = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i, (uid, count) in enumerate(top_users[:10]):
        text += f"{emojis[i]} ID {uid} — {count} 💌\n"

    await call.message.edit_caption(caption=text, reply_markup=back_to_menu_kb(user.id))
    await call.answer()



@antispam
async def valentine_cmd(message: types.Message, user: BFGuser):
    """Главное меню праздника"""
    await message.answer('''💘 <b>Добро пожаловать в мир романтики и сюрпризов!</b> 💘

✨ В честь <b>Дня Святого Валентина</b> мы подготовили для вас увлекательные события, мини-игры и возможность выразить свои чувства особенным образом.

❤️ <b>Что вас ждет?</b>

💌 <b>Подарить валентинку</b> – Сделайте день особенным для друга, отправив ему теплые слова!
📭 <b>Получить валентинку</b> – Бесплатно получайте <b>1 пустую валентинку</b> раз в <b>30 минут</b>.
📜 <b>Мой Валентин</b> – Просмотрите свою статистику: полученные и отправленные валентинки, а также итоги свиданий!
🏆 <b>Топ Валентинок</b> – Узнайте, кто получил больше всех валентинок и стал главным романтиком.
🎲 <b>Мини-игра "Свидание"</b> – Проверьте свою удачу! Играйте с друзьями, находите совпадения и зарабатывайте дополнительные пустые валентинки.
💖 <b>Пригласить на свидание</b> – Бросьте вызов другому игроку! Сможете ли вы удачно завершить свидание?

✨ <b>Дополнительная информация:</b>
🏹 <b>Получить валентинку</b> – Каждые <b>30 минут</b> можно бесплатно получить <b>1 пустую валентинку</b>.
💘 <b>Свидания</b> – Открывайте эмодзи в мини-игре, чтобы получить дополнительные валентинки!
⏳ <b>Ограничения:</b>
- Повторное приглашение на свидание – раз в <b>15 минут</b>.
- Отправка валентинок – раз в <b>10 минут</b>.

🌟 <b>Станьте самым романтичным игроком, отправляя и получая валентинки!</b> 💖''')

@antispam
async def get_valentine_cmd(message: types.Message, user: BFGuser):
    """Получение бесплатной валентинки"""
    # Использую вашу функцию gametime. Она должна работать так же, как check_time.
    # Если нет, нужно будет адаптировать.
    last_time = get_valentine_time.get(user.id, 0)
    time_diff = int(time.time()) - last_time
    cooldown = 1800  # 30 минут в секундах

    if time_diff < cooldown:
        wait_minutes = (cooldown - time_diff) // 60
        await message.answer(f'⏳ Вы недавно получали бесплатную валентинку! Подождите ещё {wait_minutes} мин.')
        return

    await db.issue_valentine(user.id)
    get_valentine_time[user.id] = int(time.time())
    await message.answer('🎉 Вы получили 1 пустую валентинку! Используйте её, чтобы отправить другому игроку 💌')

@antispam
async def give_valentine_cmd(message: types.Message, user: BFGuser):
    """Начало процесса отправки валентинки"""
    data = await db.get_info(user.id)

    if message.chat.type != 'private':
        await message.answer('❓ Отправить валентинку можно только в личных сообщениях с ботом.')
        return

    if data[0] <= 0:
        await message.answer('📭 У вас нет пустых валентинок!\nЗаработайте их в мини-игре.')
        return

    try:
        # Ожидаем формат: /send_valentine 123
        game_id = int(message.text.split()[1])
    except (IndexError, ValueError):
        await message.answer('❌ Используйте: /send_valentine [игровой ID]')
        return

    recipient_user_id = await check_user_by_game_id(game_id)

    if not recipient_user_id:
        await message.answer('❌ Данного игрока не существует. Перепроверьте указанный <b>игровой ID</b>')
        return

    if user.id == recipient_user_id:
        await message.answer('❌ Нельзя отправить валентинку самому себе.')
        return

    # Проверка времени отправки
    last_send = give_valentine_time.get(user.id, 0)
    time_diff = int(time.time()) - last_send
    cooldown = 600  # 10 минут

    if time_diff < cooldown:
        wait_minutes = (cooldown - time_diff) // 60
        await message.answer(f'⏳ Вы недавно отправляли валентинку! Подождите ещё {wait_minutes} мин.')
        return

    txt = '''💌 <b>Выберите режим отправки:</b>

🥷 <b>Инкогнито</b> — получатель не узнает, кто отправил.
😍 <b>Признаться открыто</b> — ваш ник будет указан.'''

    await message.answer(text=txt, reply_markup=select_mod(recipient_user_id))

@antispam_earning
async def send_valentine_callback(call: types.CallbackQuery, state: FSMContext):
    """Обработка выбора режима отправки валентинки"""
    await call.message.delete()  # Удаляем сообщение с кнопками
    
    data_parts = call.data.split('_')
    recipient_id = int(data_parts[2])
    anonymous = int(data_parts[3])
    
    await call.message.answer(
        '<b>💌 Введите текст валентинки (до 50 символов):</b>',
        parse_mode="HTML"
    )
    
    await state.update_data(recipient_id=recipient_id, anonymous=anonymous)
    await state.set_state(ValentineState.message)


@antispam
async def receive_valentine_message(message: types.Message, state: FSMContext):
    """Получение текста валентинки и отправка"""
    user_id = message.from_user.id
    
    if len(message.text) > 50:
        await message.answer('🚫 Текст должен быть не более 50 символов. Попробуйте снова:')
        return
    
    data = await state.get_data()
    recipient_id = data['recipient_id']
    anonymous = data['anonymous']
    
    # Получаем данные отправителя
    user_info = await db.get_info(user_id)
    if user_info[0] <= 0:
        await message.answer('📭 У вас нет пустых валентинок!')
        await state.clear()
        return
    
    # Отправляем получателю
    sender_text = "Анонимно" if anonymous else f"от {message.from_user.full_name}"
    try:
        await bot.send_message(
            recipient_id,
            f'💌 <b>Вы получили валентинку {sender_text}!</b>\n\n«{message.text}»',
            parse_mode="HTML"
        )
    except:
        pass
    
    await message.answer('✅ Валентинка отправлена!')
    await db.new_valentine(user_id, recipient_id, anonymous, message.text)
    give_valentine_time[user_id] = int(time.time())
    await state.clear()




async def reset_state_timeout(chat_id: int, state: FSMContext):
    """Сброс состояния через 2 минуты бездействия"""
    await asyncio.sleep(120)
    current_state = await state.get_state()
    if current_state == ValentineState.message.state:
        await state.clear()
        await bot.send_message(chat_id, "💘 <b>Время на отправку валентинки вышло</b>.")


@antispam
async def receive_valentine_message(message: types.Message, state: FSMContext):
    """Получение текста валентинки и отправка"""
    user_id = message.from_user.id

    if len(message.text) > 50:
        await message.answer('🚫 Текст валентинки должен содержать не более 50 символов.\n\n🔄 Попробуйте снова:')
        return

    user_info = await db.get_info(user_id)
    if user_info[0] <= 0:
        await message.answer('📭 У вас нет пустых валентинок!\nЗаработайте их в мини-игре.')
        await state.clear()
        return

    data = await state.get_data()
    recipient_id = data['recipient_id']
    anonymous = data['anonymous']

    # Отправляем валентинку получателю
    sender_text = "Анонимно" if anonymous else f"от {message.from_user.full_name}"
    try:
        await bot.send_message(
            recipient_id,
            f'💌 <b>Вы получили валентинку {sender_text}!</b>\n\n«{message.text}»',
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Не удалось отправить валентинку пользователю {recipient_id}: {e}")

    await message.answer('✅ Вы успешно отправили валентинку!')
    await db.new_valentine(user_id, recipient_id, anonymous, message.text)
    give_valentine_time[user_id] = int(time.time())
    await state.clear()

# ==================== FSM И КОЛБЭКИ ====================
async def reset_state_timeout(chat_id: int, state: FSMContext):
    """Сброс состояния через 2 минуты бездействия"""
    await asyncio.sleep(120)
    current_state = await state.get_state()
    if current_state == ValentineState.message.state:
        await state.clear()
        await bot.send_message(chat_id, "💘 <b>Время на отправку валентинки вышло</b>.")



@antispam_earning
async def send_valentine_callback(call: types.CallbackQuery, state: FSMContext):
    """Обработка выбора режима отправки"""
    data_parts = call.data.split('_')
    recipient_id = int(data_parts[2])
    anonymous = int(data_parts[3])

    await call.message.delete()
    await call.message.answer('<b>💌 Введите текст валентинки (до 50 символов), у вас есть 2 минуты:</b>')

    await state.update_data(recipient_id=recipient_id, anonymous=anonymous)
    await state.set_state(ValentineState.message)

    asyncio.create_task(reset_state_timeout(call.from_user.id, state))
    await call.answer()

@antispam
async def receive_valentine_message(message: types.Message, state: FSMContext):
    """Получение текста валентинки и отправка"""
    user_id = message.from_user.id

    if len(message.text) > 50:
        await message.answer('🚫 Текст валентинки должен содержать не более 50 символов.\n\n🔄 Попробуйте снова:')
        return

    user_info = await db.get_info(user_id)
    if user_info[0] <= 0:
        await message.answer('📭 У вас нет пустых валентинок!\nЗаработайте их в мини-игре.')
        await state.clear()
        return

    # Повторная проверка времени (на случай, если пользователь долго думал)
    last_send = give_valentine_time.get(user_id, 0)
    time_diff = int(time.time()) - last_send
    cooldown = 600
    if time_diff < cooldown:
        wait_minutes = (cooldown - time_diff) // 60
        await message.answer(f'⏳ Вы недавно отправляли валентинку! Подождите ещё {wait_minutes} мин.')
        await state.clear()
        return

    data = await state.get_data()
    recipient_id = data['recipient_id']
    anonymous = data['anonymous']

    # Отправка получателю
    sender_info = "Анонимно" if anonymous else f" от {message.from_user.full_name}"
    try:
        await bot.send_message(recipient_id, f'💌 <b>Вы получили валентинку{sender_info}!</b>\n\n«{message.text}»')
    except Exception as e:
        print(f"Не удалось отправить валентинку пользователю {recipient_id}: {e}")

    await message.answer('✅ Вы успешно отправили валентинку!')
    await db.new_valentine(user_id, recipient_id, anonymous, message.text)
    give_valentine_time[user_id] = int(time.time())
    await state.clear()

# ==================== МОИ ВАЛЕНТИНКИ И ТОП ====================
async def get_my_valentine_text(user_id: int) -> str:
    """Формирование текста статистики пользователя"""
    data = await db.get_info(user_id)
    # data: (valentine, sent_valentines, obtained_valentines, lucky_dates, unlucky_dates)
    text = f'''<b>💌 {cfg.bot_name} | День Святого Валентина</b>

🌟 <b>Получено Валентинок:</b> {data[2]}
📤 <b>Отправлено Валентинок:</b> {data[1]}
📭 <b>Пустые Валентинки:</b> {data[0]}

🎲 <b>Статистика свиданий:</b>
💞 <b>Всего:</b> {data[3] + data[4]}
✅ <b>Удачных:</b> {data[3]}
❌ <b>Неудачных:</b> {data[4]}

✨ Отправляйте валентинки друзьям и поднимитесь в топ!'''
    return text

@antispam
async def my_valentine_cmd(message: types.Message, user: BFGuser):
    """Команда для просмотра своей статистики"""
    text = await get_my_valentine_text(user.id)
    msg = await message.answer_photo(photo=VALENTINE_PHOTO, caption=text, reply_markup=valentine_menu(user.id))
    await new_earning_msg(msg.chat.id, msg.message_id)

@antispam_earning
async def my_valentine_menu_callback(call: types.CallbackQuery, user: BFGuser):
    """Возврат в главное меню валентинок"""
    text = await get_my_valentine_text(user.id)
    await call.message.edit_caption(caption=text, reply_markup=valentine_menu(user.id))
    await call.answer()

@antispam_earning
async def my_valentine_list_callback(call: types.CallbackQuery, user: BFGuser):
    """Просмотр списка полученных валентинок"""
    data_parts = call.data.split('_')
    page = int(data_parts[3])
    valentines = await db.get_user_valentines(user.id)

    if not valentines:
        await call.message.edit_caption(
            caption='💔 У вас пока нет полученных валентинок.',
            reply_markup=back_to_menu_kb(user.id)
        )
        await call.answer()
        return

    # Пагинация по 1 валентинке на страницу
    total_pages = (len(valentines) + 4) // 5
    if page < 1 or page > total_pages:
        page = 1

    v = valentines[page - 1] # sender, anonymous, message
    sender_id, anonymous, msg_text = v

    sender_name = "Аноним" if anonymous else (await get_name(sender_id) if 'get_name' in dir() else f"ID {sender_id}") # Используйте вашу функцию get_name

    text = f'''<b>💌 Валентинка #{page}</b>

<b>От:</b> {sender_name}
<b>Сообщение:</b> "{msg_text}"'''

    await call.message.edit_caption(
        caption=text,
        reply_markup=my_valentine_pagination_kb(user.id, page, total_pages)
    )
    await call.answer()

@antispam_earning
async def valentine_top_callback(call: types.CallbackQuery, user: BFGuser):
    """Топ полученных валентинок"""
    top_users = await db.get_top_valentine()
    if not top_users:
        await call.message.edit_caption(
            caption='📊 Топ пока пуст. Будьте первым!',
            reply_markup=back_to_menu_kb(user.id)
        )
        await call.answer()
        return

    text = "🏆 <b>Топ полученных валентинок</b>\n\n"
    emojis = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i, (uid, count) in enumerate(top_users[:10]):
        name = await get_name(uid) if 'get_name' in dir() else f"ID {uid}" # Используйте вашу функцию get_name
        text += f"{emojis[i]} {name} — {count} 💌\n"

    await call.message.edit_caption(caption=text, reply_markup=back_to_menu_kb(user.id))
    await call.answer()

# ==================== РЕГИСТРАЦИЯ ХЭНДЛЕРОВ ====================
def reg(dp: Dispatcher):
    dp.message.register(valentine_cmd, F.text.lower().in_(["валентинка", "/valentine"]))
    dp.message.register(get_valentine_cmd, F.text.lower() == "/get_valentine")
    dp.message.register(give_valentine_cmd, F.text.lower().startswith("/send_valentine"))
    dp.message.register(my_valentine_cmd, F.text.lower() == "/my_valentine")
    
    # Новые обработчики для отправки
    dp.callback_query.register(send_valentine_callback, F.data.startswith("send_valentine_"))
    dp.message.register(receive_valentine_message, ValentineState.message)
    
    dp.callback_query.register(my_valentine_menu_callback, F.data.startswith("my_valentine_menu_"))
    dp.callback_query.register(my_valentine_list_callback, F.data.startswith("my_valentine_list_"))
    dp.callback_query.register(valentine_top_callback, F.data.startswith("valentine_top_"))
# ==================== ОПИСАНИЕ МОДУЛЯ ====================


