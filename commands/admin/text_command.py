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
        args = message.get_args().split()
        if len(args) < 2:
            await message.reply("Используйте: /banb [игровой id] [время] [причина]")
            return
            
        game_id, time_str = args[0], args[1]
        reason = ' '.join(args[2:]) if len(args) > 2 else 'Не указана'
        
        # Конвертируем время
        time_s = sum(int(value) * {'д': 86400, 'ч': 3600, 'м': 60}[unit] 
                    for value, unit in re.findall(r'(\d+)([дчм])', time_str))
        time_s = int(time.time()) + time_s
        
    except Exception as e:
        await message.reply(f"Ошибка формата: {e}\nИспользуйте: /banb [игровой id] [время] [причина]")
        return
    
    # Проверяем, существует ли пользователь с таким game_id
    user_data = cursor.execute(
        "SELECT user_id, name FROM users WHERE game_id = ?", 
        (int(game_id),)
    ).fetchone()
    
    if not user_data:
        await message.answer(f"❌ Пользователь с игровым ID <b>{game_id}</b> не найден.")
        return
    
    telegram_id, name = user_data
    
    # Баним
    await db.new_ban(telegram_id, time_s, reason)
    await message.answer(
        f'📛 Пользователь <b>{name}</b> (ID: {game_id}) заблокирован на {time_str}\n'
        f'Причина: <i>{reason}</i>'
    )


@admin_only()
async def unban(message: types.Message):
    try:
        user_id = int(message.text.split()[1])
    except:
        await message.reply("Используйте: /unbanb [игровой id]")
        return
    
    await db.unban_user(user_id)
    await message.answer(f'🛡 Пользователь {user_id} разблокирован.')
    

@admin_only()
async def take_the_money(message: types.Message):
    user_id = message.from_user.id
    url = await url_name(user_id)

    try:
        r_user_id = message.reply_to_message.from_user.id
        r_url = await url_name(user_id)
    except:
        await message.answer(f'{url}, чтобы выдать деньги нужно ответить на сообщение пользователя.')
        return

    try:
        summ = message.text.split()[1].replace('е', 'e')
        summ = int(float(summ))
    except:
        await message.answer(f'{url}, вы не ввели сумму которую хотите забрать.')
        return

    await db.take_the_money(r_user_id, summ)
    await message.answer(f'{url}, вы забрали {tr(summ)}$ у пользователя {r_url}')
    
    
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
