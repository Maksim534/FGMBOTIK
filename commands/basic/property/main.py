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

# Словарь для хранения времени последней поездки на такси
last_taxi_time = {}


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

    hdata = cars.get(user.property.car.get())
    fuel = await db.get_fuel(user.id)
    car_price = await db.get_car_price(user.id)
    
    taxi_earning = int(car_price * random.uniform(0.01, 0.03))
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="⛽ Заправить", switch_inline_query_current_chat=f"заправить"),
        InlineKeyboardButton(text="🚖 Таксовать", switch_inline_query_current_chat=f"таксовать"),
        width=2
    )
    
    fuel_bar = "🟩" * (fuel // 10) + "⬜" * (10 - (fuel // 10))
    
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
    win, lose = BFGconst.emj()
    
    if int(user.property.car) == 0:
        await message.answer(f"{user.url}, у вас нет автомобиля {lose}")
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
    win, lose = BFGconst.emj()
    
    if int(user.property.car) == 0:
        await message.answer(f"{user.url}, у вас нет автомобиля {lose}")
        return
    
    current_time = time.time()
    last_time = last_taxi_time.get(user.id, 0)
    time_diff = current_time - last_time
    cooldown = 1800
    
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


async def show_updated_car(message: types.Message, user: BFGuser, success_message: str = None):
    hdata = cars.get(user.property.car.get())
    fuel = await db.get_fuel(user.id)
    car_price = await db.get_car_price(user.id)
    taxi_earning = int(car_price * random.uniform(0.01, 0.03))
    
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
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="⛽ Заправить", switch_inline_query_current_chat=f"заправить"),
        InlineKeyboardButton(text="🚖 Таксовать", switch_inline_query_current_chat=f"таксовать"),
        width=2
    )
    
    fuel_bar = "🟩" * (fuel // 10) + "⬜" * (10 - (fuel // 10))
    
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
    
    if message.reply_to_message:
        await message.reply_photo(photo=hdata[4], caption=txt, reply_markup=keyboard.as_markup())
    else:
        await message.answer_photo(photo=hdata[4], caption=txt, reply_markup=keyboard.as_markup())


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
    
    # Команды для автомобиля
    dp.message.register(refuel_cmd, StartsWith("заправить"))
    dp.message.register(taxi_cmd, StartsWith("таксовать"))
