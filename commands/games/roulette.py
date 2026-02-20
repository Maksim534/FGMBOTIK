import random
import asyncio
from datetime import datetime, timedelta
from aiogram import types, Dispatcher, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from assets.antispam import antispam, antispam_earning
from assets.transform import transform_int as tr
from commands.games.db import gXX
from filters.custom import StartsWith
from user import BFGuser, BFGconst
from commands.basic.property.lists import exclusive_cars
import commands.basic.property.db as prop_db

# ==================== КОНФИГУРАЦИЯ ====================
ROULETTE_COST = 10_000_000  # Стоимость одного круга (10 млн)
COOLDOWN_HOURS = 24  # Кулдаун в часах

# Словарь для хранения времени последнего использования
last_roulette_time = {}  # {user_id: timestamp}

# Анимация вращения
ROULETTE_ANIMATION = [
    "🎰 [ ••• ] Крутим...",
    "🎰 [ •• ] Крутим..",
    "🎰 [ • ] Крутим.",
    "🎰 [ ✦ ] Почти...",
    "🎰 [ ✦✦ ] Ещё немного...",
    "🎰 [ ✦✦✦ ] Стоп!",
]

# Призы и их шансы (в сумме должно быть 100)
PRIZES = [
    # Деньги (50% шанс)
    {"type": "money", "name": "💰 Деньги", "chance": 50},
    
    # Опыт (15% шанс)
    {"type": "exp", "name": "💡 Опыт", "chance": 15},
    
    # Рейтинг (10% шанс)
    {"type": "rating", "name": "👑 Рейтинг", "chance": 10},
    
    # Биткоины (10% шанс)
    {"type": "btc", "name": "🌐 Биткоины", "chance": 10},
    
    # B-Coins (8% шанс)
    {"type": "bcoins", "name": "💳 B-Coins", "chance": 8},
    
    # Энергия (5% шанс)
    {"type": "energy", "name": "⚡ Энергия", "chance": 5},
    
    # Йены (1.5% шанс)
    {"type": "yen", "name": "💴 Йены", "chance": 1.5},
    
    # Эксклюзивная машина (0.5% шанс) - СУПЕРПРИЗ!
    {"type": "car", "name": "🚗 ЭКСКЛЮЗИВНАЯ МАШИНА", "chance": 0.5},
]

# Список эксклюзивных машин для выпадения
EXCLUSIVE_CARS_LIST = list(exclusive_cars.keys())


def get_prize() -> dict:
    """Определяет приз на основе шансов"""
    rand = random.uniform(0, 100)
    cumulative = 0
    
    for prize in PRIZES:
        cumulative += prize["chance"]
        if rand <= cumulative:
            # Если приз - деньги, генерируем случайную сумму
            if prize["type"] == "money":
                amount = random.randint(5_000_000, 50_000_000)
                return {"type": "money", "name": "💰 Деньги", "amount": amount}
            
            # Если приз - опыт
            elif prize["type"] == "exp":
                amount = random.randint(1_000, 10_000)
                return {"type": "exp", "name": "💡 Опыт", "amount": amount}
            
            # Если приз - рейтинг
            elif prize["type"] == "rating":
                amount = random.randint(500, 5_000)
                return {"type": "rating", "name": "👑 Рейтинг", "amount": amount}
            
            # Если приз - биткоины
            elif prize["type"] == "btc":
                amount = round(random.uniform(0.001, 0.05), 6)
                return {"type": "btc", "name": "🌐 Биткоины", "amount": amount}
            
            # Если приз - B-Coins
            elif prize["type"] == "bcoins":
                amount = random.randint(100, 1_000)
                return {"type": "bcoins", "name": "💳 B-Coins", "amount": amount}
            
            # Если приз - энергия
            elif prize["type"] == "energy":
                amount = random.randint(5, 20)
                return {"type": "energy", "name": "⚡ Энергия", "amount": amount}
            
            # Если приз - йены
            elif prize["type"] == "yen":
                amount = random.randint(1_000_000, 10_000_000)
                return {"type": "yen", "name": "💴 Йены", "amount": amount}
            
            # Если приз - машина
            elif prize["type"] == "car":
                car_id = random.choice(EXCLUSIVE_CARS_LIST)
                car_name = exclusive_cars[car_id][0]
                return {
                    "type": "car", 
                    "name": f"🚗 {car_name}", 
                    "car_id": car_id,
                    "car_name": car_name
                }
    
    # На всякий случай (если что-то пошло не так)
    return {"type": "money", "name": "💰 Деньги", "amount": 10_000_000}


async def award_prize(user: BFGuser, prize: dict) -> str:
    """Начисляет приз пользователю и возвращает описание"""
    
    if prize["type"] == "money":
        await user.balance.upd(prize["amount"], '+')
        return f"+{tr(prize['amount'])}$"
    
    elif prize["type"] == "exp":
        await user.exp.upd(prize["amount"], '+')
        return f"+{prize['amount']} 💡 опыта"
    
    elif prize["type"] == "rating":
        await user.rating.upd(prize["amount"], '+')
        return f"+{prize['amount']} 👑 рейтинга"
    
    elif prize["type"] == "btc":
        await user.btc.upd(prize["amount"], '+')
        return f"+{prize['amount']} 🌐 BTC"
    
    elif prize["type"] == "bcoins":
        await user.bcoins.upd(prize["amount"], '+')
        return f"+{prize['amount']} 💳 B-Coins"
    
    elif prize["type"] == "energy":
        await user.energy.upd(prize["amount"], '+')
        return f"+{prize['amount']} ⚡ энергии"
    
    elif prize["type"] == "yen":
        await user.yen.upd(prize["amount"], '+')
        return f"+{tr(prize['amount'])} 💴 йен"
    
    elif prize["type"] == "car":
        # Выдаём машину (даже если уже есть - просто заменится)
        await prop_db.buy_property(user.id, prize["car_id"], "car", 0)  # 0 цена
        return f"🚗 ЭКСКЛЮЗИВНАЯ МАШИНА: {prize['car_name']} ✨"
    
    return "❌ Ошибка"


@antispam
async def roulette_cmd(message: types.Message, user: BFGuser):
    print(f"🔥 roulette_cmd вызвана! Текст: {message.text}")
    """Команда /рулетка - запустить анимированную рулетку"""
    win, lose = BFGconst.emj()
    
    # Проверка кулдауна
    current_time = datetime.now()
    last_time = last_roulette_time.get(user.id)
    
    if last_time:
        time_diff = current_time - last_time
        if time_diff.total_seconds() < COOLDOWN_HOURS * 3600:
            remaining = timedelta(hours=COOLDOWN_HOURS) - time_diff
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            
            await message.answer(
                f"{user.url}, ⏳ рулетка ещё крутится!\n"
                f"Следующий раз через {hours} ч {minutes} мин",
                parse_mode="HTML"
            )
            return
    
    # Проверяем баланс
    if int(user.balance) < ROULETTE_COST:
        await message.answer(
            f"{user.url}, для игры в рулетку нужно {tr(ROULETTE_COST)}$ {lose}",
            parse_mode="HTML"
        )
        return
    
    # Списываем деньги
    await user.balance.upd(ROULETTE_COST, '-')
    
    # Отправляем первое сообщение
    msg = await message.answer(
        f"{user.url}, 🎰 <b>РУЛЕТКА ЗАПУЩЕНА!</b>\n\n"
        f"{ROULETTE_ANIMATION[0]}",
        parse_mode="HTML"
    )
    
    # Анимация вращения
    for frame in ROULETTE_ANIMATION[1:-1]:  # Пропускаем первый и последний
        await asyncio.sleep(0.5)  # Пауза между кадрами
        await msg.edit_text(
            f"{user.url}, 🎰 <b>РУЛЕТКА ЗАПУЩЕНА!</b>\n\n"
            f"{frame}",
            parse_mode="HTML"
        )
    
    await asyncio.sleep(0.5)
    
    # Получаем приз
    prize = get_prize()
    award_text = await award_prize(user, prize)
    
    # Запоминаем время
    last_roulette_time[user.id] = current_time
    
    # Финальное сообщение
    await msg.edit_text(
        f"{user.url}, 🎰 <b>РУЛЕТКА ОСТАНОВИЛАСЬ!</b>\n\n"
        f"🎯 <b>ВАШ ПРИЗ:</b>\n"
        f"{prize['name']}: {award_text}\n\n"
        f"💸 Потрачено: {tr(ROULETTE_COST)}$\n"
        f"⏳ Следующий раз через 24 часа",
        parse_mode="HTML"
    )


def reg(dp: Dispatcher):
    print("🔥 РЕГИСТРАЦИЯ РУЛЕТКИ ВЫЗВАНА!")
    dp.message.register(roulette_cmd, StartsWith("рулетка"))
    dp.message.register(roulette_cmd, StartsWith("/рулетка"))
