from aiogram import types, Dispatcher

import commands.basic.property.db as db
from assets.antispam import antispam
from commands.basic.property.lists import *
from assets.transform import transform_int as tr
from filters.custom import TextIn, StartsWith
from user import BFGuser, BFGconst


@antispam
async def helicopters_list(message: types.Message, user: BFGuser):
    await message.answer(f"""{user.url}, доступные вертолёты:
🚁 1. Воздушный шар - 100.000$

🛒 Для покупки вертолёта введите "Купить вертолет [номер]\"""")


@antispam
async def cars_list(message: types.Message, user: BFGuser):
    await message.answer(f"""{user.url}, доступные машины:
🚗 1. Самокат - 10.000$
🚗 2. УАЗ Хантер - 32.500$
🚗 3. Peel P50 - 50.000$
🚗 4. Daihatsu Terios kid - 200.000$
🚗 5. Mitsubishi Pajero Mini - 370.000$
🚗 6. Honda civic - 450.000$
🚗 7. Acura Integra - 650.000$
🚗 8. Mazda MX-5 Miata - 800.000$
🚗 9. Opel Astra - 1.000.000$
🚗 10. Audi 80 - 1.200.000$
🚗 11. Lada Granta - 1.500.000$
🚗 12. Lincoln Continental - 2.000.000$
🚗 13. Volkswagen Golf GTI - 2.500.000$
🚗 14. Nissan Almera Classic - 3.100.000$
🚗 15. BMW 3-series e36 - 4.500.000$
🚗 16. Mercedes-Benz w220 - 6.000.000$
🚗 17. Ford Raptor - 8.000.000$
🚗 18. Dodge Durango - 16.500.000$
🚗 19. Infinity FX37 - 40.000.000$
🚗 20. Porsche Cayenne S - 80.000.000$
🚗 21. Jeep grand Cherokee - 300.000.000$
🚗 22. Aurus Senat - 700.000.000$
🚗 23. Bugatti La Voiture Noire - 4.000.000.000$


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

    txt = f"""{user.url}, информация о вашем автомобиле "{hdata[0]}"
⛽️ Максимальная скорость: {hdata[1]} км/ч
🐎 Лошадиных сил: {hdata[2]}
⏱ Разгон до 100 за {hdata[3]} сек"""

    await message.answer_photo(photo=hdata[4], caption=txt)


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
🐎 Лошадиных сил: {hdata[2]}"""

    await message.answer_photo(photo=hdata[3], caption=txt)


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

    if int(user.balance) < hdata[4]:
        await message.answer(f"{user.url}, у вас недостаточно денег для покупки имущества {lose}")
        return

    await message.answer(f"{user.url}, вы успешно купили самолёт \"{hdata[0]}\" 🎉")
    await db.buy_property(user.user_id, num, "plane", hdata[4])


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
    summ = int(hdata[4] * 0.75)

    await message.answer(f"{user.url}, вы успешно продали самолёт за {tr(summ)}$ 🎉")
    await db.sell_property(user.user_id, "plane", summ)


def reg(dp: Dispatcher):
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
