from aiogram import types, Dispatcher

from commands.basic.property.autosalon import reg as autosalon_reg
from commands.basic.property.helicopter_salon import reg as heli_reg
from commands.basic.property.house_salon import reg as house_salon_reg
from commands.basic.property.phone_salon import reg as phone_salon_reg
from commands.basic.property.plane_salon import reg as plane_salon_reg
from commands.basic.property.yacht_salon import reg as yacht_salon_reg

import commands.basic.property.db as db
from assets.antispam import antispam
from commands.basic.property.lists import *
from assets.transform import transform_int as tr
from filters.custom import TextIn, StartsWith
from user import BFGuser, BFGconst
import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import config as cfg

from assets.antispam import antispam_earning
import time

# Словари для хранения времени
last_taxi_time = {}      # для обычных машин (такси)
last_race_time = {}      # для эксклюзивных машин (гонки)


@antispam
async def my_helicopter(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.helicopter) == 0:
        await message.answer(f"{user.url}, к сожалению у вас нет вертолёта {lose}")
        return

    hdata = helicopters.get(user.property.helicopter.get())

    txt = f"""{user.url}, информация о вашем вертолёте "{hdata[0]}"
⛽️ Максимальная скорость: {hdata[1]} км/ч
🐎 Лошадиных сил: {hdata[2]}"""

    await message.answer_photo(photo=hdata[3], caption=txt)


@antispam
async def my_phone(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.phone) == 0:
        await message.answer(f"{user.url}, к сожалению у вас нет телефона {lose}")
        return

    hdata = phones.get(user.property.phone.get())
    await message.answer_photo(photo=hdata[1], caption=f"{user.url}, ваш телефон \"{hdata[0]}\"")


@antispam
async def my_car(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.car) == 0:
        await message.answer(f"{user.url}, к сожалению у вас нет автомобиля {lose}")
        return

    car_id = user.property.car.get()
    
    # Определяем тип машины
    if car_id in exclusive_cars:
        hdata = exclusive_cars.get(car_id)
        exclusive_tag = "✨ ЭКСКЛЮЗИВ ✨"
        is_exclusive = True
    else:
        hdata = cars.get(car_id)
        exclusive_tag = ""
        is_exclusive = False
    
    if not hdata:
        await message.answer(f"{user.url}, данные вашего автомобиля не найдены {lose}")
        return
    
    fuel = await db.get_fuel(user.id) if not is_exclusive else 100  # У эксклюзивных всегда полный бак
    car_price = await db.get_car_price(user.id)
    
    # Создаём клавиатуру в зависимости от типа машины
    keyboard = InlineKeyboardBuilder()
    
    if is_exclusive:
        # Эксклюзивные машины: только гонка (без заправки)
        keyboard.row(
            InlineKeyboardButton(text="🏁 Гонка", switch_inline_query_current_chat=f"гонка"),
            width=1
        )
    else:
        # Обычные машины: заправка + такси
        keyboard.row(
            InlineKeyboardButton(text="⛽ Заправить", switch_inline_query_current_chat=f"заправить"),
            InlineKeyboardButton(text="🚖 Таксовать", switch_inline_query_current_chat=f"таксовать"),
            width=2
        )
    
    fuel_bar = "🟩" * (fuel // 10) + "⬜" * (10 - (fuel // 10))
    
    # Формируем текст в зависимости от типа машины
    if is_exclusive:
        txt = f"""{user.url}, информация о вашем автомобиле "{hdata[0]}" {exclusive_tag}
        
🚗 <b>Характеристики:</b>
⛽️ Максимальная скорость: {hdata[1]} км/ч
🐎 Лошадиных сил: {hdata[2]}
⏱ Разгон до 100 за {hdata[3]} сек
💰 Стоимость: {tr(car_price)}$

🏁 <b>Гоночный болид!</b>
<i>Участвуйте в гонках и выигрывайте до 1 млрд $!</i>"""
    else:
        taxi_earning = int(car_price * random.uniform(0.01, 0.03))
        txt = f"""{user.url}, информация о вашем автомобиле "{hdata[0]}"
        
🚗 <b>Характеристики:</b>
⛽️ Максимальная скорость: {hdata[1]} км/ч
🐎 Лошадиных сил: {hdata[2]}
⏱ Разгон до 100 за {hdata[3]} сек
💰 Стоимость: {tr(car_price)}$

⛽ <b>Топливо:</b> {fuel}%
{fuel_bar}
💰 <b>Заработок за поездку:</b> {tr(taxi_earning)}$"""

    await message.answer_photo(
        photo=hdata[4], 
        caption=txt,
        reply_markup=keyboard.as_markup()
    )


@antispam
async def refuel_cmd(message: types.Message, user: BFGuser):
    """Заправка автомобиля (только для обычных машин)"""
    win, lose = BFGconst.emj()
    
    if int(user.property.car) == 0:
        await message.answer(f"{user.url}, у вас нет автомобиля {lose}")
        return
    
    car_id = user.property.car.get()
    
    # Эксклюзивные машины не заправляются
    if car_id in exclusive_cars:
        await message.answer(
            f"{user.url}, эксклюзивные машины не нуждаются в заправке! ✨\n"
            f"У них вечный двигатель! ⚡",
            parse_mode="HTML"
        )
        return
    
    current_fuel = await db.get_fuel(user.id)
    
    if current_fuel >= 100:
        await message.answer(f"{user.url}, бак уже полный! {lose}")
        return
    
    car_price = await db.get_car_price(user.id)
    cost_per_percent = int(car_price * 0.001)
    needed = 100 - current_fuel
    cost = needed * cost_per_percent
    
    if int(user.balance) < cost:
        await message.answer(f"{user.url}, недостаточно денег! Нужно {tr(cost)}$ {lose}")
        return
    
    await user.balance.upd(cost, '-')
    await db.update_fuel(user.id, needed)
    
    await show_updated_car(message, user, f"✅ Заправлено на {needed}% за {tr(cost)}$")


@antispam
async def taxi_cmd(message: types.Message, user: BFGuser):
    """Такси (только для обычных машин)"""
    win, lose = BFGconst.emj()
    
    if int(user.property.car) == 0:
        await message.answer(f"{user.url}, у вас нет автомобиля {lose}")
        return
    
    car_id = user.property.car.get()
    
    # Эксклюзивные машины не таксуют
    if car_id in exclusive_cars:
        await message.answer(
            f"{user.url}, эта машина — эксклюзив! ✨\n"
            f"Она создана для гонок, а не для работы! 🏁",
            parse_mode="HTML"
        )
        return
    
    hdata = cars.get(car_id)
    if not hdata:
        await message.answer(f"{user.url}, данные вашего автомобиля не найдены {lose}")
        return
    
    current_time = time.time()
    last_time = last_taxi_time.get(user.id, 0)
    time_diff = current_time - last_time
    cooldown = 1800  # 30 минут
    
    if time_diff < cooldown:
        wait_minutes = int((cooldown - time_diff) // 60)
        wait_seconds = int((cooldown - time_diff) % 60)
        await message.answer(f"{user.url}, ⏳ следующая поездка через {wait_minutes} мин {wait_seconds} сек! {lose}")
        return
    
    current_fuel = await db.get_fuel(user.id)
    
    if current_fuel < 10:
        await message.answer(f"{user.url}, недостаточно топлива! Нужно минимум 10% {lose}")
        return
    
    await db.update_fuel(user.id, -10)
    car_price = await db.get_car_price(user.id)
    earnings = int(car_price * random.uniform(0.01, 0.03))
    await user.balance.upd(earnings, '+')
    last_taxi_time[user.id] = current_time
    
    await show_updated_car(message, user, f"🚖 Поездка завершена! Заработано: {tr(earnings)}$")


@antispam
async def race_cmd(message: types.Message, user: BFGuser):
    """Гонка на эксклюзивной машине"""
    win, lose = BFGconst.emj()
    
    if int(user.property.car) == 0:
        await message.answer(f"{user.url}, у вас нет автомобиля {lose}")
        return
    
    car_id = user.property.car.get()
    
    # Проверяем, что это эксклюзивная машина
    if car_id not in exclusive_cars:
        await message.answer(f"{user.url}, эта команда только для эксклюзивных машин! ✨")
        return
    
    # Проверка кулдауна (30 минут)
    current_time = time.time()
    last_time = last_race_time.get(user.id, 0)
    time_diff = current_time - last_time
    cooldown = 1800
    
    if time_diff < cooldown:
        wait_minutes = int((cooldown - time_diff) // 60)
        wait_seconds = int((cooldown - time_diff) % 60)
        await message.answer(
            f"{user.url}, ⏳ двигатель остывает! Следующая гонка через {wait_minutes} мин {wait_seconds} сек! {lose}"
        )
        return
    
    # Эксклюзивные машины не тратят топливо
    # Просто запоминаем время гонки
    last_race_time[user.id] = current_time
    
    # Результаты гонки с фиксированными призами
    race_results = [
        {"place": "🏆 ЗОЛОТО!", "prize": 1_000_000_000, "desc": "Вы пришли к финишу первым! 🥇"},
        {"place": "🥈 СЕРЕБРО!", "prize": 500_000_000, "desc": "Второе место! Неплохо! 🥈"},
        {"place": "🥉 БРОНЗА!", "prize": 250_000_000, "desc": "Третье место! Тоже результат! 🥉"},
        {"place": "⚡ РЕКОРД!", "prize": 750_000_000, "desc": "Новый рекорд трассы! ⚡"},
        {"place": "💨 ЛУЧШИЙ КРУГ!", "prize": 300_000_000, "desc": "Техника на высоте! 💨"},
        {"place": "🤝 НИЧЬЯ!", "prize": 100_000_000, "desc": "Разделили приз с соперником! 🤝"},
        {"place": "🌟 КОНТРАКТ!", "prize": 600_000_000, "desc": "Вас заметили спонсоры! 🌟"},
        {"place": "🔥 ДРАГ-РЕЙС!", "prize": 400_000_000, "desc": "Победа в драг-заезде! 🔥"},
        {"place": "🌧 ГОСТЬ!", "prize": 200_000_000, "desc": "Гостевая победа под дождём! 🌧"},
        {"place": "⭐ УЛИЧНАЯ!", "prize": 350_000_000, "desc": "Слава на ночных улицах! ⭐"},
    ]
    
    result = random.choice(race_results)
    earnings = result["prize"]
    
    # Начисляем деньги
    await user.balance.upd(earnings, '+')
    
    # Получаем название машины
    car_name = exclusive_cars[car_id][0]
    
    # Эффекты гонки
    effects = [
        "🚗 Машина в идеальном состоянии!",
        "🔧 Пришлось заменить покрышки, но оно того стоило!",
        "💥 Небольшой контакт, но вы в порядке!",
        "✨ Нитро сработало идеально в нужный момент!",
        "🎨 Новая аэрография от спонсоров!",
        "⚙️ Двигатель работал как часы!",
        "💨 Попутный ветер помог установить рекорд!",
        "🎯 Идеальная траектория в каждом повороте!",
        "🔩 Механики отлично подготовили машину!",
        "🏁 Соперники кусают локти!",
    ]
    
    await message.answer(
        f"{user.url}, <b>ГОНКА ЗАВЕРШЕНА!</b> 🏁\n\n"
        f"🚗 Автомобиль: <b>{car_name}</b>\n"
        f"{result['place']} {result['desc']}\n"
        f"✨ Эффект: {random.choice(effects)}\n\n"
        f"💰 ВЫИГРЫШ: <b>{tr(earnings)}$</b>",
        parse_mode="HTML"
    )
    
    # Обновляем сообщение с машиной (просто показываем информацию)
    await show_updated_car(message, user)


async def show_updated_car(message: types.Message, user: BFGuser, success_message: str = None):
    """Обновляет сообщение с информацией о машине"""
    car_id = user.property.car.get()
    is_exclusive = car_id in exclusive_cars
    
    if is_exclusive:
        hdata = exclusive_cars.get(car_id)
        exclusive_tag = "✨ ЭКСКЛЮЗИВ ✨"
    else:
        hdata = cars.get(car_id)
        exclusive_tag = ""
    
    if not hdata:
        await message.answer(f"{user.url}, данные вашего автомобиля не найдены.")
        return
    
    fuel = await db.get_fuel(user.id) if not is_exclusive else 100
    car_price = await db.get_car_price(user.id)
    
    # Формируем клавиатуру
    keyboard = InlineKeyboardBuilder()
    
    if is_exclusive:
        keyboard.row(
            InlineKeyboardButton(text="🏁 Гонка", switch_inline_query_current_chat=f"гонка"),
            width=1
        )
    else:
        keyboard.row(
            InlineKeyboardButton(text="⛽ Заправить", switch_inline_query_current_chat=f"заправить"),
            InlineKeyboardButton(text="🚖 Таксовать", switch_inline_query_current_chat=f"таксовать"),
            width=2
        )
    
    fuel_bar = "🟩" * (fuel // 10) + "⬜" * (10 - (fuel // 10))
    
    if is_exclusive:
        txt = f"""{user.url}, информация о вашем автомобиле "{hdata[0]}" {exclusive_tag}
        
🚗 <b>Характеристики:</b>
⛽️ Максимальная скорость: {hdata[1]} км/ч
🐎 Лошадиных сил: {hdata[2]}
⏱ Разгон до 100 за {hdata[3]} сек
💰 Стоимость: {tr(car_price)}$

🏁 <b>Гоночный болид!</b>
<i>Участвуйте в гонках и выигрывайте до 1 млрд $!</i>"""
    else:
        # Статус такси для обычных машин
        current_time = time.time()
        last_time = last_taxi_time.get(user.id, 0)
        time_diff = current_time - last_time
        cooldown = 1800
        
        if time_diff < cooldown:
            wait_minutes = int((cooldown - time_diff) // 60)
            wait_seconds = int((cooldown - time_diff) % 60)
            taxi_status = f"⏳ Доступно через {wait_minutes} мин {wait_seconds} сек"
        else:
            taxi_status = "✅ Доступно сейчас"
        
        taxi_earning = int(car_price * random.uniform(0.01, 0.03))
        
        txt = f"""{user.url}, информация о вашем автомобиле "{hdata[0]}"
        
🚗 <b>Характеристики:</b>
⛽️ Максимальная скорость: {hdata[1]} км/ч
🐎 Лошадиных сил: {hdata[2]}
⏱ Разгон до 100 за {hdata[3]} сек
💰 Стоимость: {tr(car_price)}$

⛽ <b>Топливо:</b> {fuel}%
{fuel_bar}
💰 <b>Заработок за поездку:</b> {tr(taxi_earning)}$
🚖 <b>Статус такси:</b> {taxi_status}"""
    
    if success_message:
        txt = f"✅ {success_message}\n\n{txt}"
    
    photo = hdata[4] if len(hdata) > 4 else None
    if not photo:
        await message.answer(txt, reply_markup=keyboard.as_markup(), parse_mode="HTML")
    elif message.reply_to_message:
        await message.reply_photo(photo=photo, caption=txt, reply_markup=keyboard.as_markup(), parse_mode="HTML")
    else:
        await message.answer_photo(photo=photo, caption=txt, reply_markup=keyboard.as_markup(), parse_mode="HTML")


@antispam
async def my_house(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.house) == 0:
        await message.answer(f"{user.url}, к сожалению у вас нет своего дома {lose}")
        return

    hdata = house.get(user.property.house.get())
    await message.answer_photo(photo=hdata[1], caption=f"{user.url}, ваш дом \"{hdata[0]}\"")


@antispam
async def my_yahta(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.yahta) == 0:
        await message.answer(f"{user.url}, к сожалению у вас нет своей яхты {lose}")
        return

    hdata = yahts.get(user.property.yahta.get())
    txt = f"""{user.url}, информация о вашей яхте "{hdata[0]}"
⛽️ Максимальная скорость: {hdata[1]} км/ч
🐎 Лошадиных сил: {hdata[2]}"""
    await message.answer_photo(photo=hdata[3], caption=txt)


@antispam
async def my_plane(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.plane) == 0:
        await message.answer(f"{user.url}, к сожалению у вас нет своего самолёта {lose}")
        return

    hdata = planes.get(user.property.plane.get())
    txt = f"""{user.url}, информация о вашем самолёте "{hdata[0]}"
⛽️ Максимальная скорость: {hdata[1]} км/ч
💪 Мощность: {hdata[2]}
🛫 Дальность полета: {hdata[3]} км"""
    await message.answer_photo(photo=hdata[4], caption=txt)


@antispam
async def sell_helicopter(message: types.Message, user: BFGuser):
    """Продажа вертолёта"""
    win, lose = BFGconst.emj()
    
    if int(user.property.helicopter) == 0:
        await message.answer(f"{user.url}, у вас нет вертолёта для продажи {lose}")
        return
    
    hdata = helicopters.get(user.property.helicopter.get())
    price = hdata[4] // 2  # Половина стоимости
    
    await db.sell_property(user.id, "helicopter", price)
    await message.answer(f"{user.url}, вы продали вертолёт за {tr(price)}$ {win}")


@antispam
async def sell_car(message: types.Message, user: BFGuser):
    """Продажа автомобиля (любого, включая эксклюзивные)"""
    win, lose = BFGconst.emj()
    
    if int(user.property.car) == 0:
        await message.answer(f"{user.url}, у вас нет автомобиля для продажи {lose}")
        return
    
    car_id = user.property.car.get()
    
    # Определяем, откуда брать данные
    if car_id in exclusive_cars:
        hdata = exclusive_cars.get(car_id)
        car_type = "эксклюзивная"
    else:
        hdata = cars.get(car_id)
        car_type = "обычная"
    
    if not hdata:
        await message.answer(f"{user.url}, данные автомобиля не найдены {lose}")
        return
    
    # Цена продажи = половина стоимости (для эксклюзивных тоже)
    # Для обычных машин цена в индексе 5, для эксклюзивных в индексе 5 тоже (если там цена)
    price = hdata[5] // 2
    
    # Спрашиваем подтверждение
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="✅ Да, продать", callback_data=f"confirm_sell_car_{user.id}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_sell")
    )
    
    await message.answer(
        f"{user.url}, вы действительно хотите продать {hdata[0]}?\n\n"
        f"🚗 Тип: {car_type}\n"
        f"💰 Цена продажи: {tr(price)}$\n"
        f"⚠️ Это действие нельзя отменить!",
        reply_markup=keyboard.as_markup()
    )


@antispam_earning
async def confirm_sell_car(call: types.CallbackQuery, user: BFGuser):
    """Подтверждение продажи автомобиля"""
    target_user_id = int(call.data.split('_')[3])
    
    if target_user_id != user.id:
        await call.answer("Это не ваша машина!", show_alert=True)
        return
    
    if int(user.property.car) == 0:
        await call.answer("У вас уже нет машины!", show_alert=True)
        return
    
    car_id = user.property.car.get()
    
    # Определяем данные машины
    if car_id in exclusive_cars:
        hdata = exclusive_cars.get(car_id)
    else:
        hdata = cars.get(car_id)
    
    if not hdata:
        await call.answer("Данные машины не найдены!", show_alert=True)
        return
    
    # Цена продажи
    price = hdata[5] // 2
    
    # Продаём машину (функция db.sell_property уже есть)
    await db.sell_property(user.id, "car", price)
    
    await call.message.edit_text(
        f"✅ {user.url}, вы продали {hdata[0]} за {tr(price)}$!",
        parse_mode="HTML"
    )
    await call.answer("Машина продана!", show_alert=True)


@antispam_earning
async def cancel_sell(call: types.CallbackQuery):
    """Отмена продажи"""
    await call.message.edit_text("❌ Продажа отменена.")
    await call.answer()


@antispam
async def sell_house(message: types.Message, user: BFGuser):
    """Продажа дома"""
    win, lose = BFGconst.emj()
    
    if int(user.property.house) == 0:
        await message.answer(f"{user.url}, у вас нет дома для продажи {lose}")
        return
    
    hdata = house.get(user.property.house.get())
    price = hdata[2] // 2  # Половина стоимости
    
    await db.sell_property(user.id, "house", price)
    await message.answer(f"{user.url}, вы продали дом за {tr(price)}$ {win}")


@antispam
async def sell_phone(message: types.Message, user: BFGuser):
    """Продажа телефона"""
    win, lose = BFGconst.emj()
    
    if int(user.property.phone) == 0:
        await message.answer(f"{user.url}, у вас нет телефона для продажи {lose}")
        return
    
    hdata = phones.get(user.property.phone.get())
    price = hdata[2] // 2  # Половина стоимости
    
    await db.sell_property(user.id, "phone", price)
    await message.answer(f"{user.url}, вы продали телефон за {tr(price)}$ {win}")


@antispam
async def sell_yacht(message: types.Message, user: BFGuser):
    """Продажа яхты"""
    win, lose = BFGconst.emj()
    
    if int(user.property.yahta) == 0:
        await message.answer(f"{user.url}, у вас нет яхты для продажи {lose}")
        return
    
    hdata = yahts.get(user.property.yahta.get())
    price = hdata[4] // 2  # Половина стоимости
    
    await db.sell_property(user.id, "yahta", price)
    await message.answer(f"{user.url}, вы продали яхту за {tr(price)}$ {win}")


@antispam
async def sell_plane(message: types.Message, user: BFGuser):
    """Продажа самолёта"""
    win, lose = BFGconst.emj()
    
    if int(user.property.plane) == 0:
        await message.answer(f"{user.url}, у вас нет самолёта для продажи {lose}")
        return
    
    hdata = planes.get(user.property.plane.get())
    price = hdata[5] // 2  # Половина стоимости
    
    await db.sell_property(user.id, "plane", price)
    await message.answer(f"{user.url}, вы продали самолёт за {tr(price)}$ {win}")


def reg(dp: Dispatcher):
    # Регистрация салонов
    autosalon_reg(dp)
    heli_reg(dp)
    house_salon_reg(dp)
    phone_salon_reg(dp)
    plane_salon_reg(dp)
    yacht_salon_reg(dp)
    
    # Команды для просмотра своего имущества
    dp.message.register(my_helicopter, TextIn("мой вертолёт"))
    dp.message.register(my_phone, TextIn("мой телефон"))
    dp.message.register(my_car, TextIn("моя машина"))
    dp.message.register(my_house, TextIn("мой дом"))
    dp.message.register(my_yahta, TextIn("моя яхта"))
    dp.message.register(my_plane, TextIn("мой самолёт"))
    
    # Команды для автомобилей
    dp.message.register(refuel_cmd, StartsWith("заправить"))
    dp.message.register(taxi_cmd, StartsWith("таксовать"))
    dp.message.register(race_cmd, StartsWith("гонка"))
    
    # Команды для продажи имущества
    dp.message.register(sell_helicopter, TextIn("продать вертолёт"))
    dp.message.register(sell_car, TextIn("продать машину"))
    dp.message.register(sell_house, TextIn("продать дом"))
    dp.message.register(sell_phone, TextIn("продать телефон"))
    dp.message.register(sell_yacht, TextIn("продать яхту"))
    dp.message.register(sell_plane, TextIn("продать самолёт"))
