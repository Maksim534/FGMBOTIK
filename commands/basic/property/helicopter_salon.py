from aiogram import types, Dispatcher, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from assets.antispam import antispam, antispam_carousel
from commands.basic.property.lists import helicopters
from assets.transform import transform_int as tr
from filters.custom import StartsWith
from user import BFGuser, BFGconst
import commands.basic.property.db as db

# Словарь для хранения текущей страницы каждого пользователя
user_helicopter_page = {}


def get_keyboard(user_id: int, current_page: int, total: int) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру для навигации"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки навигации
    nav_buttons = []
    
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"heli_page_{current_page-1}_{user_id}"))
    else:
        nav_buttons.append(InlineKeyboardButton(text="⏺️", callback_data="ignore"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"{current_page}/{total}", callback_data="ignore"))
    
    if current_page < total:
        nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"heli_page_{current_page+1}_{user_id}"))
    else:
        nav_buttons.append(InlineKeyboardButton(text="⏺️", callback_data="ignore"))
    
    builder.row(*nav_buttons)
    builder.row(InlineKeyboardButton(text="💰 Купить", callback_data=f"heli_buy_{current_page}_{user_id}"))
    builder.row(InlineKeyboardButton(text="❌ Закрыть", callback_data="heli_close"))
    
    return builder.as_markup()


async def update_message(message: types.Message, user: BFGuser, page: int, total: int):
    """Обновляет сообщение с новым фото и текстом"""
    item = helicopters.get(page)
    if not item:
        return
    
    # Распаковываем данные (для вертолётов: название, скорость, сила, фото, цена)
    name, speed, power, photo_url, price = item
    
    text = f"""
🚁 <b>{name}</b>

📊 <b>Характеристики:</b>
⛽️ Скорость: {speed} км/ч
⚡️ Мощность: {power} л.с.

💰 <b>Цена:</b> {tr(price)}$
"""
    
    media = types.InputMediaPhoto(media=photo_url, caption=text, parse_mode="HTML")
    keyboard = get_keyboard(user.id, page, total)
    
    await message.edit_media(media=media)
    await message.edit_reply_markup(reply_markup=keyboard)


@antispam
async def salon_cmd(message: types.Message, user: BFGuser):
    """Команда /вертолёты - просмотр вертолётов"""
    user_id = user.id
    user_helicopter_page[user_id] = 1
    total = len(helicopters)
    
    item = helicopters.get(1)
    name, speed, power, photo_url, price = item
    
    text = f"""
🚁 <b>{name}</b>

📊 <b>Характеристики:</b>
⛽️ Скорость: {speed} км/ч
⚡️ Мощность: {power} л.с.

💰 <b>Цена:</b> {tr(price)}$
"""
    
    keyboard = get_keyboard(user.id, 1, total)
    
    await message.answer_photo(photo=photo_url, caption=text, reply_markup=keyboard, parse_mode="HTML")


@antispam_carousel
async def salon_callback(call: types.CallbackQuery, user: BFGuser):
    data = call.data.split('_')
    action = data[1]
    
    if action == "page":
        page = int(data[2])
        target_id = int(data[3])
        
        if target_id != user.id:
            await call.answer("Это не ваша сессия!", show_alert=True)
            return
        
        user_helicopter_page[user.id] = page
        total = len(helicopters)
        await update_message(call.message, user, page, total)
        await call.answer()
    
    elif action == "buy":
        page = int(data[2])
        target_id = int(data[3])
        
        if target_id != user.id:
            await call.answer("Это не ваша сессия!", show_alert=True)
            return
        
        item = helicopters.get(page)
        if not item:
            await call.answer("Не найдено!", show_alert=True)
            return
        
        name, speed, power, photo_url, price = item
        
        if int(user.property.helicopter) != 0:
            await call.answer("У вас уже есть вертолёт!", show_alert=True)
            return
        
        if int(user.balance) < price:
            await call.answer(f"Недостаточно денег! Нужно {tr(price)}$", show_alert=True)
            return
        
        await db.buy_property(user.id, page, "helicopter", price)
        
        await call.message.edit_caption(
            caption=f"✅ {user.url}, вы купили {name} за {tr(price)}$!\n\nКоманда: <b>мой вертолёт</b>",
            parse_mode="HTML",
            reply_markup=None
        )
        await call.answer("Поздравляем!", show_alert=True)
    
    elif action == "close":
        await call.message.delete()
        await call.answer()


def reg(dp: Dispatcher):
    dp.message.register(salon_cmd, StartsWith("/верт"))
    dp.message.register(salon_cmd, StartsWith("верт"))
    dp.callback_query.register(salon_callback, F.data.startswith("heli_"))
