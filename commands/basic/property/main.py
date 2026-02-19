from aiogram import types, Dispatcher

import commands.basic.property.db as db
from assets.antispam import antispam
from commands.basic.property.lists import *
from assets.transform import transform_int as tr
from filters.custom import TextIn, StartsWith
from user import BFGuser, BFGconst
import random
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Добавьте эти импорты в начало файла
from assets.antispam import antispam_earning
import time


@antispam
async def helicopters_list(message: types.Message, user: BFGuser):
    await message.answer(f"""{user.url}, доступные вертолёты:
🚁 1. Воздушный шар - 100.000$
🚁 2. Robinson R22 - 620.000$
🚁 3. Robinson R44 Raven - 850.000$
🚁 4. Bell 505 Jet Ranger X - 1.550.000$
🚁 5. Airbus H125 - 2.100.000$
🚁 6. Leonardo AW109 Grand New - 3.800.000$
🚁 7. Airbus H145 - 5.000.000$
🚁 8. Bell 429 GlobalRanger - 7.550.000$
🚁 9. Leonardo AW139 - 10.300.000$
🚁 10. Sikorsky S-76D - 13.700.000$

🛒 Для покупки вертолёта введите "Купить вертолет [номер]\"""")


@antispam
async def cars_list(message: types.Message, user: BFGuser):
    await message.answer(f"""{user.url}, доступные машины:
🚗 1. Самокат - 100.000$
🚗 2. УАЗ Хантер - 500.000$
🚗 3. Peel P50 - 750.000$
🚗 4. Daihatsu Terios kid - 1.200.000$
🚗 5. Mitsubishi Pajero Mini - 3.700.000$
🚗 6. Honda civic - 15.000.000$
🚗 7. Acura Integra - 50.000.000$
🚗 8. Mazda MX-5 Miata - 80.000.000$
🚗 9. Opel Astra - 100.000.000$
🚗 10. Audi 80 - 120.000.000$
🚗 11. Lada Granta - 150.000.000$
🚗 12. Lincoln Continental - 200.000.000$
🚗 13. Volkswagen Golf GTI - 250.000.000$
🚗 14. Nissan Almera Classic - 310.000.000$
🚗 15. BMW 3-series e36 - 450.000.000$
🚗 16. Mercedes-Benz w220 - 600.000.000$
🚗 17. Ford Raptor - 800.000.000$
🚗 18. Dodge Durango - 1.650.000.000$
🚗 19. Infinity FX37 - 4.000.000.000$
🚗 20. Porsche Cayenne S - 8.000.000.000$
🚗 21. Jeep grand Cherokee - 30.000.000.000$
🚗 22. Aurus Senat - 70.000.000.000$
🚗 23. Bugatti La Voiture Noire - 500.000.000.000$


🛒 Для покупки машины введите "Купить машину [номер]\"""")


@antispam
async def house_list(message: types.Message, user: BFGuser):
    await message.answer(f"""{user.url}, доступные дома:
🏠 1. Коробка - 500.000$
🏠 2. Почтовый Ящик - 750.000$
🏠 3. Подвал -  800.000$
🏠 4. Гараж - 1.200.000$
🏠 5. Бытовка - 1.500.000$
🏠 6. Маленький Домик - 2.750.000$
🏠 7. Дом в Скандинавском Стиле - 3.500.000$
🏠 8. Дом в стиле Барнхаус - 4.555.000$
🏠 9. Дом в стиле Хай-тек - 5.930.000$
🏠 10. Дом в стиле Райта - 6.555.000$
🏠 11. Дом в стиле Футуризм - 7.400.000$
🏠 12. Особняк - 10.750.000$
🏠 13. Дворец - 14.000.000$
🏠 14. Замок - 17.555.000$
🏠 15. Небоскрёб Антилия - 25.000.00$
🏠 16. Марс - 99.999.999$


🛒 Для покупки дома введите "Купить дом [номер]\"""")


@antispam
async def yahta_list(message: types.Message, user: BFGuser):
    await message.answer(f"""{user.url}, доступные дома:
🏠 1. Коробка - 500.000$

🛒 Для покупки дома введите "Купить дом [номер]\"""")


@antispam
async def phone_list(message: types.Message, user: BFGuser):
    await message.answer(f"""{user.url}, доступные телефоны:
📱 1. Игрушечный Телефон - 75.000$
📱 2. Nokia 3310 - 200.000$
📱 3. Sony Ericsson W810 - 390.000$
📱 4. Nokia 3250 - 530.000$
📱 5. Motorola ROKR Z6 - 750.000$
📱 6. LG Optimus P500 - 1.200.000$
📱 7. iPhone 5 - 2.500.000$
📱 8. Xiaomi Redmi 12C - 3.000.000$
📱 9. iPhone X - 4.500.000$
📱 10. Samsung Galaxy S23 Ultra - 7.500.000$
📱 11. iPhone 13 - 8.700.000$
📱 12. Samsung Galaxy Z Fold5 - 9.500.000$
📱 13. iPhone 17 Pro Max - 15.000.000$
📱 14. Diamond Crypto Smartphone - 19.000.000$

🛒 Для покупки телефона введите "Купить телефон [номер]\"""")


@antispam
async def yahts_list(message: types.Message, user: BFGuser):
    await message.answer(f"""{user.url}, доступные яхты:
🛳 1. Ванна - 1.000.000$
🛳 2. Boston Whaler 170 Montauk - 5.530.000$
🛳 3. Sea Ray SPX 190 OB - 25.850.000$
🛳 4. Axopar 28 Cabin - 40.500.000$
🛳 5. Beneteau Gran Turismo 41 - 55.780.000$
🛳 6. Sunseeker Manhattan 55 - 75.000.000$
🛳 7. Princess Y78 - 80.000.000$
🛳 8. Azimut S7 - 130.000.000$
🛳 9. Ferretti Yachts 1000 - 270.790.000$
🛳 10. Heesen 3700 Project SkyFall - 380.990.000$
🛳 11. Oceanco Y712 - 980.890.000$
🛳 12. Lürssen Dilbar - 1.890.550.000$


🛒 Для покупки яхты введите "Купить яхту [номер]\"""")


@antispam
async def plane_list(message: types.Message, user: BFGuser):
    await message.answer(f"""{user.url}, доступные самолеты:
✈️ 1. Параплан - 50.000$
✈️ 2. Cessna 172 Skyhawk - 360.000$
✈️ 3. АН-2 - 780.000$
✈️ 4. Boeing 717 - 1.350.000$
✈️ 5. Boeing 737-200 - 4.700.000$
✈️ 6. Cessna 182 (Skylane) - 4.900.000$
✈️ 7. Bombardier Challenger 3500 - 10.700.000$
✈️ 8. Falcon 2000LX - 13.900.000$
✈️ 9. Embraer Legacy 450 - 16.570.000$
✈️ 10. Gulfstream G280 - 19.000.000$
✈️ 11. Airbus A318 - 26.950.000$
✈️ 12. Sukhoi Superjet 100-95 (SSJ100) - 574.950.000$
✈️ 13. Bombardier CRJ1000 - 678.850.000$
✈️ 14. Embraer E195-E2 - 689.970.000$
✈️ 15. Airbus A220-300 (Bombardier CSeries) - 987.990.000$
✈️ 16. Boeing 737-8 MAX - 1.050.650.000$
✈️ 17. Airbus A320neo - 1.450.980.000$
✈️ 18.Airbus A321ceo - 1.970.650.000$
✈️ 19. Airbus A350-1000 - 2.750.875.000$
✈️ 20. Airbus A380 - 3.560.457.000$
✈️ 21. Boeing 747-800 Intercontinental - 3.630.220.000$
✈️ 22. Туполев Ту-144 - 4.245.950.000$

🛒 Для покупки самолёта введите "Купить самолёт [номер]\"""")


@antispam
async def my_helicopter(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.helicopter) == 0:
        await message.answer(f"{user.url}, к сожалению у вас нет вертолёта {lose}")
        return

    hdata = helicopters.get(user.property.helicopter.get())

    txt = f"""{user.url}, информация о вашем вертолёте "{hdata[0]}"
⛽️ Максимальная скорость: {hdata[1]} км/ч
🐎 Лошадиных сил: {hdata[2]}""

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
    
    # Рассчитываем заработок от такси (1-3% от стоимости машины)
    taxi_earning = int(car_price * random.uniform(0.01, 0.03))
    
    # Создаём клавиатуру
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="⛽ Заправить", callback_data=f"refuel_{user.id}"),
        InlineKeyboardButton(text="🚖 Таксовать", callback_data=f"taxi_{user.id}")
    )
    
    # Индикатор топлива
    fuel_bar = "🟩" * (fuel // 10) + "⬜" * (10 - (fuel // 10))
    
    txt = f"""{user.url}, информация о вашем автомобиле "{hdata[0]}"
    
🚗 <b>Характеристики:</b>
⛽️ Максимальная скорость: {hdata[1]} км/ч
🐎 Лошадиных сил: {hdata[2]}
⏱ Разгон до 100 за {hdata[3]} сек
💰 Стоимость: {tr(car_price)}$

⛽ <b>Топливо:</b> {fuel}%
{fuel_bar}
💰 <b>Заработок за поездку:</b> {tr(taxi_earning)}$""

    await message.answer_photo(
        photo=hdata[4], 
        caption=txt,
        reply_markup=keyboard.as_markup()
    )


@antispam_earning
async def refuel_callback(call: types.CallbackQuery, user: BFGuser):
    """Заправка автомобиля"""
    win, lose = BFGconst.emj()
    
    if int(user.property.car) == 0:
        await call.answer("У вас нет автомобиля!", show_alert=True)
        return
    
    current_fuel = await db.get_fuel(user.id)
    
    if current_fuel >= 100:
        await call.answer("Бак уже полный!", show_alert=True)
        return
    
    # Стоимость заправки зависит от цены машины
    car_price = await db.get_car_price(user.id)
    # 1% топлива стоит 0.1% от стоимости машины
    cost_per_percent = int(car_price * 0.001)
    needed = 100 - current_fuel
    cost = needed * cost_per_percent
    
    if int(user.balance) < cost:
        await call.answer(f"Недостаточно денег! Нужно {tr(cost)}$", show_alert=True)
        return
    
    # Списываем деньги и добавляем топливо
    await user.balance.upd(cost, '-')
    await db.update_fuel(user.id, needed)
    
    await call.answer(f"✅ Заправлено на {needed}% за {tr(cost)}$", show_alert=True)
    
    # Обновляем сообщение
    await update_car_message(call.message, user)


@antispam_earning
async def taxi_callback(call: types.CallbackQuery, user: BFGuser):
    """Работа в такси"""
    win, lose = BFGconst.emj()
    
    if int(user.property.car) == 0:
        await call.answer("У вас нет автомобиля!", show_alert=True)
        return
    
    current_fuel = await db.get_fuel(user.id)
    
    if current_fuel < 10:
        await call.answer("Недостаточно топлива! Нужно минимум 10%", show_alert=True)
        return
    
    # Тратим 10% топлива
    await db.update_fuel(user.id, -10)
    
    # Заработок зависит от цены машины (1-3%)
    car_price = await db.get_car_price(user.id)
    earnings = int(car_price * random.uniform(0.01, 0.03))
    
    await user.balance.upd(earnings, '+')
    
    await call.answer(f"🚖 Поездка завершена! Заработано: {tr(earnings)}$", show_alert=True)
    
    # Обновляем сообщение
    await update_car_message(call.message, user)
    

async def update_car_message(message: types.Message, user: BFGuser):
    """Обновление сообщения с машиной"""
    try:
        hdata = cars.get(user.property.car.get())
        fuel = await db.get_fuel(user.id)
        car_price = await db.get_car_price(user.id)
        taxi_earning = int(car_price * random.uniform(0.01, 0.03))
        
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(text="⛽ Заправить", callback_data=f"refuel_{user.id}"),
            InlineKeyboardButton(text="🚖 Таксовать", callback_data=f"taxi_{user.id}")
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
💰 <b>Заработок за поездку:</b> {tr(taxi_earning)}$""

        await message.edit_caption(
            caption=txt,
            reply_markup=keyboard.as_markup()
        )
    except Exception as e:
        print(f"❌ Ошибка в update_car_message: {e}")


        
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
🛫 Дальность полета: {hdata[3]}""

    await message.answer_photo(photo=hdata[4], caption=txt)


@antispam
async def buy_helicopter(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.helicopter) != 0:
        await message.answer(f"{user.url}, у вас уже есть данный тип имущества {lose}")
        return

    try:
        num = int(message.text.split()[2])
    except:
        await message.answer(f"{user.url}, вы не ввели число имущества или привелегии которое хотите купить {lose}")
        return

    hdata = helicopters.get(num)
    
    if not hdata:
        await message.answer(f"{user.url}, вы не ввели число имущества или привелегии которое хотите купить {lose}")
        return

    if int(user.balance) < hdata[4]:
        await message.answer(f"{user.url}, у вас недостаточно денег для покупки имущества {lose}")
        return

    await message.answer(f"{user.url}, вы успешно купили вертолёт \"{hdata[0]}\" 🎉")
    await db.buy_property(user.user_id, num, "helicopter", hdata[4])


@antispam
async def buy_phone(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.phone) != 0:
        await message.answer(f"{user.url}, у вас уже есть данный тип имущества {lose}")
        return

    try:
        num = int(message.text.split()[2])
    except:
        await message.answer(f"{user.url}, вы не ввели число имущества или привелегии которое хотите купить {lose}")
        return

    hdata = phones.get(num)
    
    if not hdata:
        await message.answer(f"{user.url}, вы не ввели число имущества или привелегии которое хотите купить {lose}")
        return

    if int(user.balance) < hdata[2]:
        await message.answer(f"{user.url}, у вас недостаточно денег для покупки имущества {lose}")
        return

    await message.answer(f"{user.url}, вы успешно купили телефон \"{hdata[0]}\" 🎉")
    await db.buy_property(user.user_id, num, "phone", hdata[2])


@antispam
async def buy_car(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.car) != 0:
        await message.answer(f"{user.url}, у вас уже есть данный тип имущества {lose}")
        return

    try:
        num = int(message.text.split()[2])
    except:
        await message.answer(f"{user.url}, вы не ввели число имущества или привелегии которое хотите купить {lose}")
        return

    hdata = cars.get(num)
    
    if not hdata:
        await message.answer(f"{user.url}, вы не ввели число имущества или привелегии которое хотите купить {lose}")
        return

    if int(user.balance) < hdata[5]:
        await message.answer(f"{user.url}, у вас недостаточно денег для покупки имущества {lose}")
        return

    await message.answer(f"{user.url}, вы успешно купили машину \"{hdata[0]}\" 🎉")
    await db.buy_property(user.user_id, num, "car", hdata[5])


@antispam
async def buy_house(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.house) != 0:
        await message.answer(f"{user.url}, у вас уже есть данный тип имущества {lose}")
        return

    try:
        num = int(message.text.split()[2])
    except:
        await message.answer(f"{user.url}, вы не ввели число имущества или привелегии которое хотите купить {lose}")
        return

    hdata = house.get(num)
    
    if not hdata:
        await message.answer(f"{user.url}, вы не ввели число имущества или привелегии которое хотите купить {lose}")
        return

    if int(user.balance) < hdata[2]:
        await message.answer(f"{user.url}, у вас недостаточно денег для покупки имущества {lose}")
        return

    await message.answer(f"{user.url}, вы успешно купили дом \"{hdata[0]}\" 🎉")
    await db.buy_property(user.user_id, num, "house", hdata[2])


@antispam
async def buy_yahta(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.yahta) != 0:
        await message.answer(f"{user.url}, у вас уже есть данный тип имущества {lose}")
        return

    try:
        num = int(message.text.split()[2])
    except:
        await message.answer(f"{user.url}, вы не ввели число имущества или привелегии которое хотите купить {lose}")
        return

    hdata = yahts.get(num)
    
    if not hdata:
        await message.answer(f"{user.url}, вы не ввели число имущества или привелегии которое хотите купить {lose}")
        return

    if int(user.balance) < hdata[4]:
        await message.answer(f"{user.url}, у вас недостаточно денег для покупки имущества {lose}")
        return

    await message.answer(f"{user.url}, вы успешно купили яхту \"{hdata[0]}\" 🎉")
    await db.buy_property(user.user_id, num, "yahta", hdata[4])


@antispam
async def buy_plane(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.plane) != 0:
        await message.answer(f"{user.url}, у вас уже есть данный тип имущества {lose}")
        return

    try:
        num = int(message.text.split()[2])
    except:
        await message.answer(f"{user.url}, вы не ввели число имущества или привелегии которое хотите купить {lose}")
        return

    hdata = planes.get(num)
    
    if not hdata:
        await message.answer(f"{user.url}, вы не ввели число имущества или привелегии которое хотите купить {lose}")
        return

    if int(user.balance) < hdata[5]:
        await message.answer(f"{user.url}, у вас недостаточно денег для покупки имущества {lose}")
        return

    await message.answer(f"{user.url}, вы успешно купили самолёт \"{hdata[0]}\" 🎉")
    await db.buy_property(user.user_id, num, "plane", hdata[5])


@antispam
async def sell_helicopter(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.helicopter) == 0:
        await message.answer(f"{user.url}, у вас нет данного имущества {lose}")
        return

    hdata = helicopters.get(int(user.property.helicopter))
    
    summ = int(hdata[4] * 0.75)

    await message.answer(f"{user.url}, вы успешно продали вертолёт за {tr(summ)}$ 🎉")
    await db.sell_property(user.user_id, "helicopter", summ)


@antispam
async def sell_phone(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.phone) == 0:
        await message.answer(f"{user.url}, у вас нет данного имущества {lose}")
        return

    hdata = phones.get(int(user.property.phone))
    summ = int(hdata[2] * 0.75)

    await message.answer(f"{user.url}, вы успешно продали телефон за {tr(summ)}$ 🎉")
    await db.sell_property(user.user_id, "phone", summ)


@antispam
async def sell_car(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.car) == 0:
        await message.answer(f"{user.url}, у вас нет данного имущества {lose}")
        return

    hdata = cars.get(int(user.property.car))
    summ = int(hdata[5] * 0.75)

    await message.answer(f"{user.url}, вы успешно продали машину за {tr(summ)}$ 🎉")
    await db.sell_property(user.user_id, "car", summ)


@antispam
async def sell_house(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.house) == 0:
        await message.answer(f"{user.url}, у вас нет данного имущества {lose}")
        return

    hdata = house.get(int(user.property.house))
    summ = int(hdata[2] * 0.75)

    await message.answer(f"{user.url}, вы успешно продали дом за {tr(summ)}$ 🎉")
    await db.sell_property(user.user_id, "house", summ)


@antispam
async def sell_yahta(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.yahta) == 0:
        await message.answer(f"{user.url}, у вас нет данного имущества {lose}")
        return

    hdata = yahts.get(int(user.property.yahta))
    summ = int(hdata[4] * 0.75)

    await message.answer(f"{user.url}, вы успешно продали яхту за {tr(summ)}$ 🎉")
    await db.sell_property(user.user_id, "yahta", summ)


@antispam
async def sell_plane(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    
    if int(user.property.plane) == 0:
        await message.answer(f"{user.url}, у вас нет данного имущества {lose}")
        return

    hdata = planes.get(int(user.property.plane))
    summ = int(hdata[5] * 0.75)

    await message.answer(f"{user.url}, вы успешно продали самолёт за {tr(summ)}$ 🎉")
    await db.sell_property(user.user_id, "plane", summ)


def reg(dp: Dispatcher):
    # ... существующие регистрации ...
    dp.callback_query.register(refuel_callback, lambda call: call.data.startswith("refuel_"))
    dp.callback_query.register(taxi_callback, lambda call: call.data.startswith("taxi_"))
    dp.message.register(helicopters_list, TextIn("вертолеты", "вертолёты"))
    dp.message.register(cars_list, TextIn("машины"))
    dp.message.register(house_list, TextIn("дома"))
    dp.message.register(phone_list, TextIn("телефоны"))
    dp.message.register(plane_list, TextIn("самолеты", "самолёты"))
    dp.message.register(yahts_list, TextIn("яхты"))

    dp.message.register(my_helicopter, TextIn("мой вертолет", "мой вертолёт"))
    dp.message.register(my_phone, TextIn("мой телефон"))
    dp.message.register(my_car, TextIn("моя машина"))
    dp.message.register(my_house, TextIn("мой дом"))
    dp.message.register(my_yahta, TextIn("моя яхта"))
    dp.message.register(my_plane, TextIn("мой самолет", "мой самолёт"))

    dp.message.register(buy_helicopter, StartsWith("купить вертолет", "купить вертолёт"))
    dp.message.register(buy_phone, StartsWith("купить телефон"))
    dp.message.register(buy_car, StartsWith("купить машину"))
    dp.message.register(buy_house, StartsWith("купить дом"))
    dp.message.register(buy_yahta, StartsWith("купить яхту"))
    dp.message.register(buy_plane, StartsWith("купить самолет", "купить самолёт"))

    dp.message.register(sell_helicopter, TextIn("продать вертолет", "продать вертолёт"))
    dp.message.register(sell_phone, TextIn("продать телефон"))
    dp.message.register(sell_car, TextIn("продать машину"))
    dp.message.register(sell_house, TextIn("продать дом"))
    dp.message.register(sell_yahta, TextIn("продать яхту"))
    dp.message.register(sell_plane, TextIn("продать самолет", "продать самолёт"))
