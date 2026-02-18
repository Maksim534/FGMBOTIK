import time
import re

from aiogram import types, Dispatcher
from aiogram.filters import Command

from assets.transform import transform_int as tr
from assets.antispam import admin_only
from commands.admin import db
from commands.db import url_name
from filters.custom import StartsWith


@admin_only()
async def sql(message: types.Message):
    res = await db.zap_sql(message.text[message.text.find(' '):])
    bot_msg = await message.answer(f'🕘 Выполнение запроса...')
    if not res:
        await bot_msg.edit_text(f"🚀 SQL Запрос выполнен.")
    else:
        await bot_msg.edit_text(f"❌ Возникла ошибка при изменении\n⚠️ Ошибка: {res}")
        
        
@admin_only()
async def ban(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.reply("❌ Используйте: /banb [игровой id] [время] [причина]\n"
                               "Пример: /banb 105 7д Нарушение")
            return
            
        game_id = parts[1]
        time_str = parts[2]
        reason = ' '.join(parts[3:]) if len(parts) > 3 else 'Не указана'
        
        # Конвертируем время в секунды
        total_seconds = 0
        matches = re.findall(r'(\d+)([дчм])', time_str)
        
        if not matches:
            await message.reply("❌ Неверный формат времени. Используйте: 7д, 5ч, 30м")
            return
            
        for value, unit in matches:
            value = int(value)
            if unit == 'д':
                total_seconds += value * 86400
            elif unit == 'ч':
                total_seconds += value * 3600
            elif unit == 'м':
                total_seconds += value * 60
        
        if total_seconds == 0:
            await message.reply("❌ Время должно быть больше 0")
            return
        
        # Рассчитываем время разблокировки
        unban_time = int(time.time()) + total_seconds
        unban_date = datetime.fromtimestamp(unban_time).strftime('%Y-%m-%d %H:%M:%S')
        
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")
        return
    
    # Проверяем существование пользователя
    user_data = cursor.execute(
        "SELECT user_id, name FROM users WHERE game_id = ?", 
        (int(game_id),)
    ).fetchone()
    
    if not user_data:
        await message.answer(f"❌ Пользователь с игровым ID <b>{game_id}</b> не найден.")
        return
    
    telegram_id, name = user_data
    
    # Баним
    await db.new_ban(telegram_id, unban_time, reason)
    
    # Форматируем время для вывода
    if 'д' in time_str:
        display_time = time_str
    else:
        # Переводим секунды обратно в дни/часы/минуты
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        parts = []
        if days > 0: parts.append(f"{days}д")
        if hours > 0: parts.append(f"{hours}ч")
        if minutes > 0: parts.append(f"{minutes}м")
        display_time = ''.join(parts)
    
    await message.answer(
        f'📛 <b>Пользователь заблокирован</b>\n'
        f'👤 Имя: {name}\n'
        f'🆔 Игровой ID: {game_id}\n'
        f'⏱ Срок: {display_time}\n'
        f'📅 Разблокировка: {unban_date}\n'
        f'📋 Причина: {reason}'
    )


@admin_only()
async def unban(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.reply("❌ Используйте: /unbanb [игровой id]")
            return
            
        game_id = parts[1]
        
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")
        return
    
    # Проверяем существование пользователя
    user_data = cursor.execute(
        "SELECT user_id, name FROM users WHERE game_id = ?", 
        (int(game_id),)
    ).fetchone()
    
    if not user_data:
        await message.answer(f"❌ Пользователь с игровым ID <b>{game_id}</b> не найден.")
        return
    
    telegram_id, name = user_data
    
    # Проверяем, забанен ли пользователь
    ban_info = cursor.execute(
        "SELECT * FROM ban_list WHERE user_id = ?", 
        (telegram_id,)
    ).fetchone()
    
    if not ban_info:
        await message.answer(f"👤 {name} (ID: {game_id}) не находится в бане.")
        return
    
    # Разбаниваем
    await db.unban_user(telegram_id)  # Передаём Telegram ID
    
    await message.answer(
        f'🛡 <b>Пользователь разблокирован</b>\n'
        f'👤 Имя: {name}\n'
        f'🆔 Игровой ID: {game_id}'
    )
    
    
@admin_only()
async def reset_the_money(message: types.Message):
    user_id = message.from_user.id
    url = await url_name(user_id)

    try:
        r_user_id = message.reply_to_message.from_user.id
        r_url = await url_name(user_id)
    except:
        await message.answer(f'{url}, чтобы выдать деньги нужно ответить на сообщение пользователя.')
        return

    await db.reset_the_money(r_user_id)
    await message.answer(f'{url}, пользователь {r_url} обнулен!')


def reg(dp: Dispatcher):
    dp.message.register(sql, Command("sql"))
    dp.message.register(ban, Command("banb"))
    dp.message.register(unban, Command("unbanb"))
    dp.message.register(take_the_money, StartsWith("забрать"))
    dp.message.register(reset_the_money, StartsWith("обнулить"))
