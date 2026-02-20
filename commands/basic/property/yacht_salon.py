from aiogram import types, Dispatcher, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from assets.antispam import antispam, antispam_carousel
from commands.basic.property.lists import yahts
from assets.transform import transform_int as tr
from filters.custom import StartsWith
from user import BFGuser, BFGconst
import commands.basic.property.db as db

# Словарь для хранения текущей страницы каждого пользователя
user_yacht_page = {}


def get_yacht_keyboard(user_id: int, current_page: int, total: int) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру для навигации по яхтам"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки навигации
    nav_buttons = []
    
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"yacht_page_{current_page-1}_{user_id}"
            )
        )
    else:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⏺️",
                callback_data="ignore"
            )
        )
    
    nav_buttons.append(
        InlineKeyboardButton(
            text=f"{current_page}/{total}",
            callback_data="ignore"
        )
    )
    
    if current_page < total:
        nav_buttons.append(
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"yacht_page_{current_page+1}_{user_id}"
            )
        )
    else:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⏺️",
                callback_data="ignore"
            )
        )
    
    builder.row(*nav_buttons)
    
    # Кнопка покупки
    builder.row(
        InlineKeyboardButton(
            text="🛥 Купить эту яхту",
            callback_data=f"yacht_buy_{current_page}_{user_id}"
        )
    )
    
    # Кнопка закрытия
    builder.row(
        InlineKeyboardButton(
            text="❌ Закрыть",
            callback_data="yacht_close"
        )
    )
    
    return builder.as_markup()


async def update_yacht_message(message: types.Message, user: BFGuser, page: int, total: int):
    """Обновляет сообщение с новым фото и текстом яхты"""
    yacht_data = yahts.get(page)
    if not yacht_data:
        return
    
    # Для яхт структура: (название, скорость, сила, ссылка на фото, цена)
    name, speed, power, photo_url, price = yacht_data
    
    text = f"""
🛥 <b>{name}</b>

📊 <b>Характеристики:</b>
⛽️ Максимальная скорость: {speed} км/ч
⚡️ Мощность: {power} л.с.

💰 <b>Цена:</b> {tr(price)}$

<i>Почувствуйте себя миллионером на собственной яхте!</i>
"""
    
    # Создаём медиа-объект с новым фото
    media = types.InputMediaPhoto(
        media=photo_url,
        caption=text,
        parse_mode="HTML"
    )
    
    keyboard = get_yacht_keyboard(user.id, page, total)
    
    # Обновляем сообщение
    await message.edit_media(media=media)
    await message.edit_reply_markup(reply_markup=keyboard)


@antispam
async def yacht_salon_cmd(message: types.Message, user: BFGuser):
    """Команда /яхты - просмотр доступных яхт"""
    user_id = user.id
    
    # Начинаем с первой страницы
    user_yacht_page[user_id] = 1
    
    # Получаем общее количество яхт
    total = len(yahts)
    
    # Получаем данные первой яхты
    yacht_data = yahts.get(1)
    name, speed, power, photo_url, price = yacht_data
    
    text = f"""
🛥 <b>{name}</b>

📊 <b>Характеристики:</b>
⛽️ Максимальная скорость: {speed} км/ч
⚡️ Мощность: {power} л.с.

💰 <b>Цена:</b> {tr(price)}$

<i>Почувствуйте себя миллионером на собственной яхте!</i>
"""
    
    # Создаём клавиатуру
    keyboard = get_yacht_keyboard(user.id, 1, total)
    
    # Отправляем сообщение с фото
    await message.answer_photo(
        photo=photo_url,
        caption=text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@antispam_carousel
async def yacht_salon_callback(call: types.CallbackQuery, user: BFGuser):
    """Обработчик нажатий на кнопки салона яхт"""
    data = call.data.split('_')
    action = data[1]
    
    if action == "page":
        # Листание страниц
        page = int(data[2])
        target_user_id = int(data[3])
        
        # Проверяем, что это тот же пользователь
        if target_user_id != user.id:
            await call.answer("Это не ваша сессия!", show_alert=True)
            return
        
        # Сохраняем текущую страницу
        user_yacht_page[user.id] = page
        
        # Получаем общее количество яхт
        total = len(yahts)
        
        # Обновляем сообщение
        await update_yacht_message(call.message, user, page, total)
        await call.answer()
    
    elif action == "buy":
        # Покупка яхты
        page = int(data[2])
        target_user_id = int(data[3])
        
        if target_user_id != user.id:
            await call.answer("Это не ваша сессия!", show_alert=True)
            return
        
        # Получаем данные яхты
        yacht_data = yahts.get(page)
        if not yacht_data:
            await call.answer("Яхта не найден!", show_alert=True)
            return
        
        name, speed, power, photo_url, price = yacht_data
        
        # Проверяем, нет ли уже яхты
        if int(user.property.yahta) != 0:
            await call.answer("У вас уже есть яхта!", show_alert=True)
            return
        
        # Проверяем баланс
        if int(user.balance) < price:
            await call.answer(f"Недостаточно денег! Нужно {tr(price)}$", show_alert=True)
            return
        
        # Покупаем
        await db.buy_property(user.id, page, "yahta", price)
        
        await call.message.edit_caption(
            caption=f"✅ {user.url}, вы успешно купили {name} за {tr(price)}$!\n\n"
                    f"Теперь введите команду <b>моя яхта</b>, чтобы посмотреть информацию.",
            parse_mode="HTML",
            reply_markup=None
        )
        await call.answer("Поздравляем с покупкой! 🛥", show_alert=True)
    
    elif action == "close":
        # Закрываем салон
        await call.message.delete()
        await call.answer()


def reg(dp: Dispatcher):
    dp.message.register(yacht_salon_cmd, StartsWith("/яхты"))
    dp.message.register(yacht_salon_cmd, StartsWith("яхты"))
    dp.callback_query.register(yacht_salon_callback, F.data.startswith("yacht_"))
