from aiogram import types, Dispatcher, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from assets.antispam import antispam, antispam_carousel
from commands.basic.property.lists import planes
from assets.transform import transform_int as tr
from filters.custom import StartsWith
from user import BFGuser, BFGconst
import commands.basic.property.db as db

# Словарь для хранения текущей страницы каждого пользователя
user_plane_page = {}


def get_plane_keyboard(user_id: int, current_page: int, total: int) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру для навигации по самолётам"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки навигации
    nav_buttons = []
    
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"plane_page_{current_page-1}_{user_id}"
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
                callback_data=f"plane_page_{current_page+1}_{user_id}"
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
            text="✈️ Купить этот самолёт",
            callback_data=f"plane_buy_{current_page}_{user_id}"
        )
    )
    
    # Кнопка закрытия
    builder.row(
        InlineKeyboardButton(
            text="❌ Закрыть",
            callback_data="plane_close"
        )
    )
    
    return builder.as_markup()


async def update_plane_message(message: types.Message, user: BFGuser, page: int, total: int):
    """Обновляет сообщение с новым фото и текстом самолёта"""
    plane_data = planes.get(page)
    if not plane_data:
        return
    
    # Для самолётов структура: (название, скорость, мощность, дальность, ссылка на фото, цена)
    name, speed, power, range_km, photo_url, price = plane_data
    
    text = f"""
✈️ <b>{name}</b>

📊 <b>Характеристики:</b>
⛽️ Максимальная скорость: {speed} км/ч
⚡️ Мощность: {power} л.с.
🛫 Дальность полета: {range_km} км

💰 <b>Цена:</b> {tr(price)}$

<i>Покорите небо на собственном самолёте!</i>
"""
    
    # Создаём медиа-объект с новым фото
    media = types.InputMediaPhoto(
        media=photo_url,
        caption=text,
        parse_mode="HTML"
    )
    
    keyboard = get_plane_keyboard(user.id, page, total)
    
    # Обновляем сообщение
    await message.edit_media(media=media)
    await message.edit_reply_markup(reply_markup=keyboard)


@antispam
async def plane_salon_cmd(message: types.Message, user: BFGuser):
    """Команда /самолёты - просмотр доступных самолётов"""
    user_id = user.id
    
    # Начинаем с первой страницы
    user_plane_page[user_id] = 1
    
    # Получаем общее количество самолётов
    total = len(planes)
    
    # Получаем данные первого самолёта
    plane_data = planes.get(1)
    name, speed, power, range_km, photo_url, price = plane_data
    
    text = f"""
✈️ <b>{name}</b>

📊 <b>Характеристики:</b>
⛽️ Максимальная скорость: {speed} км/ч
⚡️ Мощность: {power} л.с.
🛫 Дальность полета: {range_km} км

💰 <b>Цена:</b> {tr(price)}$

<i>Покорите небо на собственном самолёте!</i>
"""
    
    # Создаём клавиатуру
    keyboard = get_plane_keyboard(user.id, 1, total)
    
    # Отправляем сообщение с фото
    await message.answer_photo(
        photo=photo_url,
        caption=text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@antispam_carousel
async def plane_salon_callback(call: types.CallbackQuery, user: BFGuser):
    """Обработчик нажатий на кнопки салона самолётов"""
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
        user_plane_page[user.id] = page
        
        # Получаем общее количество самолётов
        total = len(planes)
        
        # Обновляем сообщение
        await update_plane_message(call.message, user, page, total)
        await call.answer()
    
    elif action == "buy":
        # Покупка самолёта
        page = int(data[2])
        target_user_id = int(data[3])
        
        if target_user_id != user.id:
            await call.answer("Это не ваша сессия!", show_alert=True)
            return
        
        # Получаем данные самолёта
        plane_data = planes.get(page)
        if not plane_data:
            await call.answer("Самолёт не найден!", show_alert=True)
            return
        
        name, speed, power, range_km, photo_url, price = plane_data
        
        # Проверяем, нет ли уже самолёта
        if int(user.property.plane) != 0:
            await call.answer("У вас уже есть самолёт!", show_alert=True)
            return
        
        # Проверяем баланс
        if int(user.balance) < price:
            await call.answer(f"Недостаточно денег! Нужно {tr(price)}$", show_alert=True)
            return
        
        # Покупаем
        await db.buy_property(user.id, page, "plane", price)
        
        await call.message.edit_caption(
            caption=f"✅ {user.url}, вы успешно купили {name} за {tr(price)}$!\n\n"
                    f"Теперь введите команду <b>мой самолёт</b>, чтобы посмотреть информацию.",
            parse_mode="HTML",
            reply_markup=None
        )
        await call.answer("Поздравляем с покупкой! ✈️", show_alert=True)
    
    elif action == "close":
        # Закрываем салон
        await call.message.delete()
        await call.answer()


def reg(dp: Dispatcher):
    dp.message.register(plane_salon_cmd, StartsWith("/самолёты"))
    dp.message.register(plane_salon_cmd, StartsWith("самолёты"))
    dp.callback_query.register(plane_salon_callback, F.data.startswith("plane_"))
