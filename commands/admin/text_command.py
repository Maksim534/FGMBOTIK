import time
import re
from datetime import datetime, timedelta
from aiogram import types, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from assets.transform import transform_int as tr
from assets.antispam import admin_only
from commands.admin import db
from commands.db import url_name, cursor
from filters.custom import StartsWith
from user import BFGuser


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
        moscow_time = datetime.fromtimestamp(unban_time) + timedelta(hours=2)
        unban_date = moscow_time.strftime('%Y-%m-%d %H:%M:%S')  # 👈 ИСПРАВЛЕНО
        
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
    
    # Разбаниваем - передаём game_id
    await db.unban_user(int(game_id))
    
    await message.answer(
        f'🛡 <b>Пользователь разблокирован</b>\n'
        f'👤 Имя: {name}\n'
        f'🆔 Игровой ID: {game_id}'
    )
    
@admin_only()
async def take_the_money(message: types.Message):
    """Команда 'забрать' - забирает деньги у пользователя (ответом на сообщение)"""
    admin_id = message.from_user.id
    admin_url = await url_name(admin_id)

    # Проверяем, что это ответ на сообщение
    if not message.reply_to_message:
        await message.answer(f'{admin_url}, чтобы забрать деньги нужно ответить на сообщение пользователя.')
        return
    
    try:
        target_user_id = message.reply_to_message.from_user.id
        target_url = await url_name(target_user_id)
    except Exception as e:
        await message.answer(f'{admin_url}, ошибка получения пользователя.')
        return

    # Получаем сумму
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer(f'{admin_url}, вы не ввели сумму которую хотите забрать.')
            return
            
        summ_str = parts[1].replace('е', 'e').replace(' ', '')
        summ = int(float(summ_str))
        
        if summ <= 0:
            await message.answer(f'{admin_url}, сумма должна быть больше 0.')
            return
            
    except ValueError:
        await message.answer(f'{admin_url}, введите корректную сумму.')
        return
    except Exception as e:
        await message.answer(f'{admin_url}, ошибка в формате суммы.')
        return

    # Проверяем баланс пользователя
    balance = cursor.execute(
        "SELECT balance FROM users WHERE user_id = ?", 
        (target_user_id,)
    ).fetchone()
    
    if not balance:
        await message.answer(f'{admin_url}, пользователь не найден в базе данных.')
        return
    
    current_balance = int(balance[0])
    if current_balance < summ:
        await message.answer(
            f'{admin_url}, у пользователя {target_url} недостаточно денег.\n'
            f'💰 Баланс: {tr(current_balance)}$'
        )
        return

    # Забираем деньги
    await db.take_the_money(target_user_id, summ)
    
    await message.answer(
        f'{admin_url}, вы забрали {tr(summ)}$ у пользователя {target_url}\n'
        f'💰 Новый баланс: {tr(current_balance - summ)}$'
    )


@admin_only()
async def reset_the_money(message: types.Message):
    """Команда 'обнулить' - полностью обнуляет прогресс пользователя (по реплаю или по ID)"""
    admin_id = message.from_user.id
    admin_url = await url_name(admin_id)
    
    target_user_id = None
    target_url = None
    target_game_id = None
    
    # Случай 1: Обнуление по реплаю (ответ на сообщение)
    if message.reply_to_message:
        try:
            target_user_id = message.reply_to_message.from_user.id
            target_url = await url_name(target_user_id)
            
            # Получаем game_id пользователя
            game_id_data = cursor.execute(
                "SELECT game_id FROM users WHERE user_id = ?", 
                (target_user_id,)
            ).fetchone()
            target_game_id = game_id_data[0] if game_id_data else None
            
        except Exception as e:
            await message.answer(f'{admin_url}, ошибка получения пользователя: {e}')
            return
    
    # Случай 2: Обнуление по игровому ID (например: обнулить 105)
    else:
        try:
            parts = message.text.split()
            if len(parts) < 2:
                await message.answer(
                    f'{admin_url}, укажите игровой ID или ответьте на сообщение пользователя.\n'
                    f'Пример: обнулить 105'
                )
                return
            
            game_id = int(parts[1])
            target_game_id = game_id
            
            # Ищем пользователя по game_id
            user_data = cursor.execute(
                "SELECT user_id, name FROM users WHERE game_id = ?", 
                (game_id,)
            ).fetchone()
            
            if not user_data:
                await message.answer(f'{admin_url}, пользователь с игровым ID <b>{game_id}</b> не найден.')
                return
            
            target_user_id = user_data[0]
            target_url = await url_name(target_user_id)
            
        except ValueError:
            await message.answer(f'{admin_url}, игровой ID должен быть числом.')
            return
        except Exception as e:
            await message.answer(f'{admin_url}, ошибка: {e}')
            return
    
    # Запрашиваем подтверждение
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, обнулить", callback_data=f"confirm_reset_{target_user_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_reset")
        ]
    ])
    
    await message.answer(
        f'{admin_url}, вы действительно хотите ПОЛНОСТЬЮ ОБНУЛИТЬ пользователя?\n\n'
        f'👤 Имя: {target_url}\n'
        f'🆔 Игровой ID: {target_game_id}\n'
        f'🆔 Telegram ID: <code>{target_user_id}</code>\n\n'
        f'⚠️ Это действие удалит:\n'
        f'• Все деньги и банковские счета\n'
        f'• Всю недвижимость и имущество\n'
        f'• Весь прогресс в шахте, ферме, бизнесе\n'
        f'• Энергию, опыт и рейтинг\n\n'
        f'<b>Это действие необратимо!</b>',
        reply_markup=markup
    )


@admin_only()
async def reset_cancel_callback(call: types.CallbackQuery):
    """Отмена обнуления"""
    await call.message.edit_text('❌ Обнуление отменено.')
    await call.answer()

@admin_only()
async def reset_confirm_callback(call: types.CallbackQuery, user: BFGuser):
    """Подтверждение обнуления пользователя"""
    target_user_id = int(call.data.split('_')[2])
    
    # Получаем game_id пользователя для красивого вывода
    game_id_data = cursor.execute(
        "SELECT game_id FROM users WHERE user_id = ?", 
        (target_user_id,)
    ).fetchone()
    target_game_id = game_id_data[0] if game_id_data else "?"
    
    # Обнуляем пользователя
    await db.reset_the_money(target_user_id)
    
    target_url = await url_name(target_user_id)
    await call.message.edit_text(
        f'✅ Пользователь успешно обнулён!\n'
        f'👤 Имя: {target_url}\n'
        f'🆔 Игровой ID: {target_game_id}\n'
        f'🆔 Telegram ID: <code>{target_user_id}</code>\n\n'
        f'Все его данные сброшены до начальных значений.'
    )
    await call.answer()

def reg(dp: Dispatcher):
    dp.message.register(sql, Command("sql"))
    dp.message.register(ban, Command("banb"))
    dp.message.register(unban, Command("unbanb"))
    dp.message.register(take_the_money, StartsWith("забрать"))
    dp.message.register(reset_the_money, StartsWith("обнулить"))
    
    # Добавьте эти две строки для колбэков подтверждения
    dp.callback_query.register(reset_confirm_callback, F.data.startswith("confirm_reset_"))
    dp.callback_query.register(reset_cancel_callback, F.data == "cancel_reset")
