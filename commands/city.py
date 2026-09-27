import time
import sqlite3
from typing import Optional

from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config as cfg
from commands.db import conn, cursor


# =========================
# CITY EDITION — GAME CORE
# =========================

HOUSES = {
    1: {"name": "Комната", "price": 50_000, "garage": 0, "storage": 50, "workshop": 0, "business": 0},
    2: {"name": "Квартира", "price": 450_000, "garage": 1, "storage": 200, "workshop": 0, "business": 1},
    3: {"name": "Частный дом", "price": 2_500_000, "garage": 3, "storage": 700, "workshop": 1, "business": 2},
    4: {"name": "Пентхаус", "price": 12_000_000, "garage": 6, "storage": 2_000, "workshop": 2, "business": 4},
}

CARS = {
    1: {"name": "Lada Vesta", "price": 650_000, "speed": 190, "power": 122, "accel": 10.5, "handling": 55},
    2: {"name": "Toyota Camry", "price": 2_900_000, "speed": 220, "power": 200, "accel": 8.9, "handling": 68},
    3: {"name": "BMW M4", "price": 8_400_000, "speed": 285, "power": 510, "accel": 3.9, "handling": 87},
    4: {"name": "Nissan GT-R", "price": 11_500_000, "speed": 315, "power": 565, "accel": 3.1, "handling": 91},
}

BUSINESSES = {
    1: {"name": "Магазин автозапчастей", "price": 3_000_000, "base": 45_000, "tax": 0.12, "category": "parts"},
    2: {"name": "АЗС", "price": 5_500_000, "base": 72_000, "tax": 0.15, "category": "fuel"},
    3: {"name": "Автосервис", "price": 7_500_000, "base": 98_000, "tax": 0.16, "category": "service"},
    4: {"name": "Кафе", "price": 2_800_000, "base": 40_000, "tax": 0.11, "category": "food"},
    5: {"name": "Магазин электроники", "price": 4_200_000, "base": 61_000, "tax": 0.13, "category": "electronics"},
}

PARTS = {
    "engine": ("Двигатель", 750_000),
    "turbo": ("Турбина", 450_000),
    "tires": ("Спортивные шины", 180_000),
    "suspension": ("Гоночная подвеска", 300_000),
    "brakes": ("Спортивные тормоза", 220_000),
}


# ---------- database ----------

def init_city_db():
    cursor.execute("""CREATE TABLE IF NOT EXISTS city_player (
        user_id INTEGER PRIMARY KEY,
        house_level INTEGER DEFAULT 0,
        job TEXT DEFAULT 'Безработный',
        job_level INTEGER DEFAULT 1,
        job_exp INTEGER DEFAULT 0,
        reputation INTEGER DEFAULT 0,
        last_income INTEGER DEFAULT 0,
        bank_card INTEGER DEFAULT 1,
        debt INTEGER DEFAULT 0
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS city_vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        car_type INTEGER,
        condition INTEGER DEFAULT 100,
        fuel INTEGER DEFAULT 100,
        mileage INTEGER DEFAULT 0,
        engine INTEGER DEFAULT 0,
        turbo INTEGER DEFAULT 0,
        tires INTEGER DEFAULT 0,
        suspension INTEGER DEFAULT 0,
        brakes INTEGER DEFAULT 0,
        for_sale INTEGER DEFAULT 0,
        sale_price INTEGER DEFAULT 0
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS city_businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        business_type INTEGER,
        level INTEGER DEFAULT 1,
        balance INTEGER DEFAULT 0,
        tax_due INTEGER DEFAULT 0,
        last_accrual INTEGER DEFAULT 0,
        for_sale INTEGER DEFAULT 0,
        sale_price INTEGER DEFAULT 0
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS city_parts (
        user_id INTEGER,
        part TEXT,
        amount INTEGER DEFAULT 0,
        PRIMARY KEY(user_id, part)
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS city_market (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id INTEGER,
        object_type TEXT,
        object_id INTEGER,
        price INTEGER,
        created_at INTEGER
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS city_races (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        creator_id INTEGER,
        opponent_id INTEGER,
        creator_car INTEGER,
        opponent_car INTEGER,
        stake INTEGER DEFAULT 0,
        status TEXT DEFAULT 'waiting',
        winner_id INTEGER DEFAULT 0,
        created_at INTEGER
    )""")
    conn.commit()


init_city_db()


def ensure_player(user_id: int):
    row = cursor.execute("SELECT user_id FROM city_player WHERE user_id=?", (user_id,)).fetchone()
    if not row:
        cursor.execute("INSERT INTO city_player(user_id,last_income) VALUES(?,?)", (user_id, int(time.time())))
        conn.commit()


def user_balance(user_id: int) -> int:
    row = cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,)).fetchone()
    return int(float(row[0])) if row else 0


def add_cash(user_id: int, amount: int):
    cursor.execute("UPDATE users SET balance=CAST(balance AS INTEGER)+? WHERE user_id=?", (amount, user_id))


def add_bank(user_id: int, amount: int):
    cursor.execute("UPDATE users SET bank=CAST(bank AS INTEGER)+? WHERE user_id=?", (amount, user_id))


def get_city(user_id: int):
    ensure_player(user_id)
    return cursor.execute("SELECT * FROM city_player WHERE user_id=?", (user_id,)).fetchone()


def house(user_id: int):
    row = get_city(user_id)
    return HOUSES.get(row[1]) if row and row[1] else None


def garage_count(user_id: int) -> int:
    h = house(user_id)
    return h["garage"] if h else 0


def format_money(n: int) -> str:
    return f"{int(n):,}".replace(",", " ") + "$"


# ---------- income / taxes ----------

def accrue_businesses(user_id: Optional[int] = None):
    now = int(time.time())
    query = "SELECT id,user_id,business_type,level,balance,tax_due,last_accrual FROM city_businesses"
    params = ()
    if user_id is not None:
        query += " WHERE user_id=?"
        params = (user_id,)
    rows = cursor.execute(query, params).fetchall()
    changed = False
    for bid, owner, btype, level, balance, tax_due, last in rows:
        if not last:
            last = now
        hours = min(max((now - last) // 3600, 0), 168)
        if hours <= 0:
            continue
        data = BUSINESSES[btype]
        gross = int(data["base"] * (1 + (level - 1) * 0.35) * hours)
        tax = int(gross * data["tax"])
        net = gross - tax
        cursor.execute("UPDATE city_businesses SET balance=balance+?, tax_due=tax_due+?, last_accrual=? WHERE id=?", (net, tax, last + hours * 3600, bid))
        changed = True
    if changed:
        conn.commit()


# ---------- keyboards ----------

def kb_main():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="👤 Профиль", callback_data="city:profile"), InlineKeyboardButton(text="🏠 Дом", callback_data="city:house"))
    b.row(InlineKeyboardButton(text="🚗 Гараж", callback_data="city:garage"), InlineKeyboardButton(text="💼 Работа", callback_data="city:jobs"))
    b.row(InlineKeyboardButton(text="🏢 Бизнесы", callback_data="city:businesses"), InlineKeyboardButton(text="🏦 Банк", callback_data="city:bank"))
    b.row(InlineKeyboardButton(text="🔨 Рынок", callback_data="city:market"), InlineKeyboardButton(text="🏁 Гонки", callback_data="city:races"))
    b.row(InlineKeyboardButton(text="🔩 Детали", callback_data="city:parts"), InlineKeyboardButton(text="ℹ️ Помощь", callback_data="city:help"))
    return b.as_markup()


def back_home():
    b = InlineKeyboardBuilder()
    b.button(text="⬅️ В город", callback_data="city:home")
    return b.as_markup()


def house_kb():
    b = InlineKeyboardBuilder()
    for level, data in HOUSES.items():
        b.button(text=f"🏠 {data['name']} — {format_money(data['price'])}", callback_data=f"city:buyhouse:{level}")
    b.adjust(1)
    b.button(text="⬅️ В город", callback_data="city:home")
    return b.as_markup()


def cars_kb():
    b = InlineKeyboardBuilder()
    for cid, data in CARS.items():
        b.button(text=f"🚗 {data['name']} — {format_money(data['price'])}", callback_data=f"city:buycar:{cid}")
    b.adjust(1)
    b.button(text="⬅️ В город", callback_data="city:home")
    return b.as_markup()


def business_kb():
    b = InlineKeyboardBuilder()
    for bid, data in BUSINESSES.items():
        b.button(text=f"🏢 {data['name']} — {format_money(data['price'])}", callback_data=f"city:buybiz:{bid}")
    b.adjust(1)
    b.button(text="⬅️ В город", callback_data="city:home")
    return b.as_markup()


# ---------- screens ----------

async def city_screen(target, user_id: int):
    ensure_player(user_id)
    accrue_businesses(user_id)
    row = get_city(user_id)
    h = HOUSES.get(row[1]) if row[1] else None
    cars = cursor.execute("SELECT COUNT(*) FROM city_vehicles WHERE user_id=?", (user_id,)).fetchone()[0]
    biz = cursor.execute("SELECT COUNT(*) FROM city_businesses WHERE user_id=?", (user_id,)).fetchone()[0]
    cash = user_balance(user_id)
    bank = int(float(cursor.execute("SELECT bank FROM users WHERE user_id=?", (user_id,)).fetchone()[0]))
    text = (
        f"🏙 <b>Город</b>\n\n"
        f"💵 Наличные: <b>{format_money(cash)}</b>\n"
        f"🏦 Банк: <b>{format_money(bank)}</b>\n"
        f"🏠 Жильё: <b>{h['name'] if h else 'нет'}</b>\n"
        f"🚗 Машин: <b>{cars}/{h['garage'] if h else 0}</b>\n"
        f"🏢 Бизнесов: <b>{biz}</b>\n\n"
        f"<i>Основные системы игры находятся в личных сообщениях с ботом.</i>"
    )
    await target.edit_text(text, reply_markup=kb_main(), parse_mode="HTML") if isinstance(target, types.CallbackQuery) else await target.answer(text, reply_markup=kb_main(), parse_mode="HTML")


async def city_cmd(message: types.Message):
    if message.chat.type != "private":
        await message.answer("🏙 Откройте игру в личных сообщениях с ботом.")
        return
    await city_screen(message, message.from_user.id)


async def city_callback(call: types.CallbackQuery):
    if call.message.chat.type != "private":
        await call.answer("Откройте игру в ЛС.", show_alert=True)
        return
    uid = call.from_user.id
    ensure_player(uid)
    await call.answer()
    action = call.data.split(":")
    key = action[1]

    if key == "home":
        return await city_screen(call, uid)
    if key == "profile":
        row = get_city(uid)
        await call.message.edit_text(
            f"👤 <b>Профиль города</b>\n\n"
            f"💵 Наличные: <b>{format_money(user_balance(uid))}</b>\n"
            f"🏠 Дом: <b>{HOUSES[row[1]]['name'] if row[1] else 'нет'}</b>\n"
            f"💼 Профессия: <b>{row[2]}</b>\n"
            f"📈 Ранг: <b>{row[3]}</b>\n"
            f"⭐ Опыт: <b>{row[4]}</b>\n"
            f"🏆 Репутация: <b>{row[5]}</b>", reply_markup=back_home())
    elif key == "house":
        row = get_city(uid)
        current = HOUSES.get(row[1]) if row[1] else None
        text = "🏠 <b>Недвижимость</b>\n\n"
        if current:
            text += f"Текущее жильё: <b>{current['name']}</b>\n🚗 Гараж: {current['garage']}\n📦 Склад: {current['storage']}\n🔧 Мастерская: {current['workshop']}\n\n"
        else:
            text += "У вас пока нет жилья.\n\n"
        text += "Выберите недвижимость:"
        await call.message.edit_text(text, reply_markup=house_kb())
    elif key == "buyhouse":
        level = int(action[2]); data = HOUSES[level]
        row = get_city(uid)
        if row[1] >= level:
            return await call.message.edit_text("🏠 У вас уже есть жильё этого уровня или выше.", reply_markup=back_home())
        if user_balance(uid) < data["price"]:
            return await call.message.edit_text(f"❌ Не хватает {format_money(data['price'] - user_balance(uid))}.", reply_markup=back_home())
        add_cash(uid, -data["price"])
        cursor.execute("UPDATE city_player SET house_level=? WHERE user_id=?", (level, uid))
        conn.commit()
        await call.message.edit_text(f"✅ Вы приобрели: <b>{data['name']}</b>\n💵 Потрачено: {format_money(data['price'])}", reply_markup=back_home())
    elif key == "garage":
        h = house(uid)
        cars = cursor.execute("SELECT id,car_type,condition,fuel,mileage,for_sale,sale_price FROM city_vehicles WHERE user_id=?", (uid,)).fetchall()
        text = "🚗 <b>Гараж</b>\n\n"
        if not h:
            text += "🔒 Сначала приобретите жильё."
            await call.message.edit_text(text, reply_markup=back_home()); return
        text += f"Мест: {len(cars)}/{h['garage']}\n\n"
        if cars:
            for c in cars:
                d = CARS[c[1]]
                text += f"🚗 <b>{d['name']}</b> — {c[2]}%\n⛽ {c[3]}% · {c[4]} км\n"
                if c[5]: text += f"🔨 Выставлена: {format_money(c[6])}\n"
                text += "\n"
        b = InlineKeyboardBuilder()
        if len(cars) < h['garage']:
            b.button(text="🚘 Купить машину", callback_data="city:cars")
        for c in cars:
            b.button(text=f"🔧 {CARS[c[1]]['name']}", callback_data=f"city:tune:{c[0]}")
            if not c[5]:
                b.button(text=f"🔨 Продать {CARS[c[1]]['name']}", callback_data=f"city:sellcarhelp:{c[0]}")
        b.adjust(1)
        b.button(text="⬅️ В город", callback_data="city:home")
        await call.message.edit_text(text, reply_markup=b.as_markup())
    elif key == "sellcarhelp":
        vid=int(action[2]); await call.message.edit_text(f"🔨 Чтобы выставить машину №{vid} на рынок, используйте в ЛС: <code>/citysellcar {vid} ЦЕНА</code>",reply_markup=back_home())
    elif key == "cars":
        await call.message.edit_text("🚘 <b>Автосалон</b>\n\nВыберите автомобиль:", reply_markup=cars_kb())
    elif key == "buycar":
        cid = int(action[2]); data = CARS[cid]; h = house(uid)
        count = cursor.execute("SELECT COUNT(*) FROM city_vehicles WHERE user_id=?", (uid,)).fetchone()[0]
        if not h:
            return await call.message.edit_text("🔒 Для владения автомобилем нужен хотя бы дом.", reply_markup=back_home())
        if count >= h['garage']:
            return await call.message.edit_text("🔒 В гараже нет свободного места.", reply_markup=back_home())
        if user_balance(uid) < data['price']:
            return await call.message.edit_text("❌ Недостаточно денег.", reply_markup=back_home())
        add_cash(uid, -data['price'])
        cursor.execute("INSERT INTO city_vehicles(user_id,car_type) VALUES(?,?)", (uid,cid))
        conn.commit()
        await call.message.edit_text(f"✅ Вы купили <b>{data['name']}</b>.\n🚗 Машина помещена в гараж.", reply_markup=back_home())
    elif key == "tune":
        vid = int(action[2])
        car = cursor.execute("SELECT car_type,condition,fuel,mileage,engine,turbo,tires,suspension,brakes FROM city_vehicles WHERE id=? AND user_id=?", (vid,uid)).fetchone()
        if not car: return await call.message.edit_text("❌ Машина не найдена.", reply_markup=back_home())
        d=CARS[car[0]]
        text=f"🔧 <b>{d['name']}</b>\n\n🏁 {d['speed']} км/ч · 🐎 {d['power']} л.с. · 💨 {d['accel']} сек\n🔧 Состояние: {car[1]}%\n⛽ Топливо: {car[2]}%\n🛣 Пробег: {car[3]} км\n\n<b>Тюнинг</b>\n"
        keys=InlineKeyboardBuilder()
        for idx,part in enumerate(['engine','turbo','tires','suspension','brakes'],start=4):
            keys.button(text=f"{PARTS[part][0]} — {format_money(PARTS[part][1])}", callback_data=f"city:part:{vid}:{part}")
        keys.adjust(1); keys.button(text="⬅️ В гараж", callback_data="city:garage")
        await call.message.edit_text(text, reply_markup=keys.as_markup())
    elif key == "part":
        vid=int(action[2]); part=action[3]; price=PARTS[part][1]
        car=cursor.execute("SELECT car_type,condition FROM city_vehicles WHERE id=? AND user_id=?",(vid,uid)).fetchone()
        if not car: return await call.message.edit_text("❌ Машина не найдена.",reply_markup=back_home())
        if house(uid)['workshop'] < 1: return await call.message.edit_text("🔒 Для тюнинга нужна мастерская в доме.",reply_markup=back_home())
        if user_balance(uid)<price: return await call.message.edit_text("❌ Недостаточно денег.",reply_markup=back_home())
        add_cash(uid,-price)
        cursor.execute(f"UPDATE city_vehicles SET {part}=MIN({part}+1,5), condition=MIN(condition+2,100) WHERE id=?",(vid,))
        conn.commit()
        await call.message.edit_text(f"🔧 Установка завершена.\n{PARTS[part][0]} улучшена.",reply_markup=back_home())
    elif key == "jobs":
        jobs=[("🚚 Курьер", "Доставка заказов", 4_000), ("🔧 Механик", "Ремонт автомобилей", 7_500), ("📦 Логист", "Управление доставкой", 11_000), ("💻 Техник", "Работа с электроникой", 9_000)]
        b=InlineKeyboardBuilder()
        for i,(name,desc,pay) in enumerate(jobs): b.button(text=name,callback_data=f"city:job:{i}")
        b.adjust(1); b.button(text="⬅️ В город",callback_data="city:home")
        await call.message.edit_text("💼 <b>Профессии</b>\n\nВыберите направление. Работа повышает опыт и репутацию.",reply_markup=b.as_markup())
    elif key == "job":
        jobs=[("Курьер",4_000), ("Механик",7_500), ("Логист",11_000), ("Техник",9_000)]
        idx=int(action[2]); name,pay=jobs[idx]; row=get_city(uid)
        now=int(time.time()); last=row[6]
        if now-last < 900: return await call.message.edit_text(f"⏳ Следующая смена через {(900-(now-last))//60} мин.",reply_markup=back_home())
        bonus=(row[3]-1)*0.08
        earned=int(pay*(1+bonus))
        add_cash(uid,earned); cursor.execute("UPDATE city_player SET job=?,job_exp=job_exp+10,reputation=reputation+2,last_income=? WHERE user_id=?",(name,now,uid)); conn.commit()
        await call.message.edit_text(f"💼 <b>Смена завершена</b>\n\nПрофессия: {name}\n💵 Доход: <b>{format_money(earned)}</b>\n⭐ Репутация: +2\n📈 Опыт: +10",reply_markup=back_home())
    elif key == "businesses":
        accrue_businesses(uid)
        rows=cursor.execute("SELECT id,business_type,level,balance,tax_due FROM city_businesses WHERE user_id=?",(uid,)).fetchall()
        text="🏢 <b>Бизнесы</b>\n\n"
        if rows:
            for r in rows:
                d=BUSINESSES[r[1]]; hour=int(d['base']*(1+(r[2]-1)*.35)); text+=f"🏢 <b>{d['name']}</b>\nУровень: {r[2]} · ~{format_money(hour)}/ч\nБаланс: {format_money(r[3])} · Налог: {format_money(r[4])}\n\n"
        else: text+="У вас пока нет бизнеса.\n\n"
        b=InlineKeyboardBuilder()
        for r in rows:
            b.button(text=f"⚙️ Управление: {BUSINESSES[r[1]]['name']}", callback_data=f"city:bizmanage:{r[0]}")
        b.button(text="🏪 Купить бизнес",callback_data="city:buybusiness")
        b.button(text="💰 Забрать доход",callback_data="city:collect")
        b.button(text="⬅️ В город",callback_data="city:home")
        b.adjust(1)
        await call.message.edit_text(text,reply_markup=b.as_markup())
    elif key == "bizmanage":
        bid=int(action[2]); row=cursor.execute("SELECT business_type,level,balance,tax_due FROM city_businesses WHERE id=? AND user_id=?",(bid,uid)).fetchone()
        if not row:return await call.message.edit_text("❌ Бизнес не найден.",reply_markup=back_home())
        d=BUSINESSES[row[0]]; upgrade=int(d["price"]*0.45*row[1]); hour=int(d["base"]*(1+(row[1]-1)*.35))
        b=InlineKeyboardBuilder(); b.button(text=f"📈 Улучшить — {format_money(upgrade)}",callback_data=f"city:upgradebiz:{bid}"); b.button(text=f"🧾 Оплатить налог {format_money(row[3])}",callback_data=f"city:paytax:{bid}"); b.button(text="🔨 Выставить на рынок",callback_data=f"city:sellbizhelp:{bid}"); b.button(text="⬅️ К бизнесам",callback_data="city:businesses"); b.adjust(1)
        await call.message.edit_text(f"🏢 <b>{d['name']}</b>\n\nУровень: <b>{row[1]}</b>\nДоход: <b>~{format_money(hour)}/ч</b>\nБаланс: <b>{format_money(row[2])}</b>\nНалог: <b>{format_money(row[3])}</b>\n\nСледующее улучшение: <b>{format_money(upgrade)}</b>",reply_markup=b.as_markup())
    elif key == "upgradebiz":
        bid=int(action[2]); row=cursor.execute("SELECT business_type,level FROM city_businesses WHERE id=? AND user_id=?",(bid,uid)).fetchone()
        if not row:return await call.message.edit_text("❌ Бизнес не найден.",reply_markup=back_home())
        if row[1]>=10:return await call.message.edit_text("🏢 Максимальный уровень достигнут.",reply_markup=back_home())
        cost=int(BUSINESSES[row[0]]["price"]*0.45*row[1])
        if user_balance(uid)<cost:return await call.message.edit_text(f"❌ Не хватает {format_money(cost-user_balance(uid))}.",reply_markup=back_home())
        add_cash(uid,-cost); cursor.execute("UPDATE city_businesses SET level=level+1 WHERE id=?",(bid,)); conn.commit()
        await call.message.edit_text(f"📈 Бизнес улучшен до уровня <b>{row[1]+1}</b>.\n💵 Потрачено: {format_money(cost)}",reply_markup=back_home())
    elif key == "paytax":
        bid=int(action[2]); row=cursor.execute("SELECT tax_due FROM city_businesses WHERE id=? AND user_id=?",(bid,uid)).fetchone()
        if not row:return await call.message.edit_text("❌ Бизнес не найден.",reply_markup=back_home())
        tax=row[0]
        if tax<=0:return await call.message.edit_text("✅ Налогов нет.",reply_markup=back_home())
        if user_balance(uid)<tax:return await call.message.edit_text("❌ Недостаточно денег для оплаты налога.",reply_markup=back_home())
        add_cash(uid,-tax); cursor.execute("UPDATE city_businesses SET tax_due=0 WHERE id=?",(bid,)); conn.commit()
        await call.message.edit_text(f"🧾 Налог оплачен: <b>{format_money(tax)}</b>",reply_markup=back_home())
    elif key == "sellbizhelp":
        bid=int(action[2]); await call.message.edit_text(f"🔨 Чтобы выставить бизнес №{bid} на рынок, используйте в ЛС: <code>/citysellbiz {bid} ЦЕНА</code>",reply_markup=back_home())
    elif key == "buybusiness":
        if not house(uid) or house(uid)['business']<1: return await call.message.edit_text("🔒 Сначала нужна квартира или лучшее жильё.",reply_markup=back_home())
        await call.message.edit_text("🏢 <b>Каталог бизнеса</b>\n\nВыберите объект:",reply_markup=business_kb())
    elif key == "buybiz":
        bid=int(action[2]); d=BUSINESSES[bid]; row=get_city(uid)
        count=cursor.execute("SELECT COUNT(*) FROM city_businesses WHERE user_id=?",(uid,)).fetchone()[0]
        if count>=row[1]+1: return await call.message.edit_text("🔒 Для нового бизнеса нужно улучшить жильё.",reply_markup=back_home())
        if user_balance(uid)<d['price']: return await call.message.edit_text("❌ Недостаточно денег.",reply_markup=back_home())
        add_cash(uid,-d['price']); now=int(time.time()); cursor.execute("INSERT INTO city_businesses(user_id,business_type,last_accrual) VALUES(?,?,?)",(uid,bid,now)); conn.commit()
        await call.message.edit_text(f"✅ Бизнес <b>{d['name']}</b> приобретён.\nДоход начнёт накапливаться автоматически.",reply_markup=back_home())
    elif key == "collect":
        accrue_businesses(uid); rows=cursor.execute("SELECT id,balance,tax_due FROM city_businesses WHERE user_id=?",(uid,)).fetchall(); total=0
        for bid,balance,tax in rows:
            if tax>0: continue
            total+=balance; cursor.execute("UPDATE city_businesses SET balance=0 WHERE id=?",(bid,))
        if total: add_cash(uid,total); conn.commit()
        await call.message.edit_text(f"💰 Получено из бизнеса: <b>{format_money(total)}</b>\nНалоговые задолженности сначала нужно погасить.",reply_markup=back_home())
    elif key == "bank":
        row=get_city(uid); bank=int(float(cursor.execute("SELECT bank FROM users WHERE user_id=?",(uid,)).fetchone()[0])); debt=row[8]
        b=InlineKeyboardBuilder(); b.button(text="💵 Внести 100 000$",callback_data="city:deposit:100000"); b.button(text="🏧 Снять 100 000$",callback_data="city:withdraw:100000"); b.button(text="💳 Кредит 500 000$",callback_data="city:loan:500000"); b.button(text="⬅️ В город",callback_data="city:home"); b.adjust(1)
        await call.message.edit_text(f"🏦 <b>Банк</b>\n\n💵 Наличные: {format_money(user_balance(uid))}\n🏦 Счёт: {format_money(bank)}\n💳 Долг: {format_money(debt)}",reply_markup=b.as_markup())
    elif key in ("deposit","withdraw"):
        amount=int(action[2]); cash=user_balance(uid); bank=int(float(cursor.execute("SELECT bank FROM users WHERE user_id=?",(uid,)).fetchone()[0]))
        if key=="deposit":
            if cash<amount:return await call.message.edit_text("❌ Недостаточно наличных.",reply_markup=back_home())
            add_cash(uid,-amount);add_bank(uid,amount)
        else:
            if bank<amount:return await call.message.edit_text("❌ Недостаточно средств на счёте.",reply_markup=back_home())
            add_bank(uid,-amount);add_cash(uid,amount)
        conn.commit(); await call.message.edit_text("✅ Операция выполнена.",reply_markup=back_home())
    elif key=="loan":
        amount=int(action[2]); row=get_city(uid)
        if row[8]>0:return await call.message.edit_text("❌ Сначала погасите текущий кредит.",reply_markup=back_home())
        add_bank(uid,amount); cursor.execute("UPDATE city_player SET debt=? WHERE user_id=?",(int(amount*1.1),uid)); conn.commit(); await call.message.edit_text(f"💳 Кредит зачислен.\nК возврату: {format_money(int(amount*1.1))}",reply_markup=back_home())
    elif key=="parts":
        rows=cursor.execute("SELECT part,amount FROM city_parts WHERE user_id=?",(uid,)).fetchall(); text="🔩 <b>Склад деталей</b>\n\n"+"\n".join(f"{PARTS.get(p,(p,0))[0]}: {a}" for p,a in rows) if rows else "🔩 <b>Склад деталей</b>\n\nПока пусто."
        await call.message.edit_text(text,reply_markup=back_home())
    elif key=="market":
        rows=cursor.execute("SELECT id,object_type,object_id,seller_id,price FROM city_market ORDER BY id DESC LIMIT 20").fetchall(); text="🔨 <b>Рынок игроков</b>\n\n"; b=InlineKeyboardBuilder()
        for mid,typ,oid,seller,price in rows:
            if typ=="car":
                car=cursor.execute("SELECT car_type FROM city_vehicles WHERE id=?",(oid,)).fetchone(); label=f"🚗 {CARS[car[0]]['name']} — {format_money(price)}" if car else "🚗 Машина"
            else: label=f"🏢 Объект — {format_money(price)}"
            text+=label+"\n"; b.button(text=label[:55],callback_data=f"city:buylisting:{mid}")
        if not rows:text+="Пока ничего не выставлено."
        b.adjust(1); b.button(text="⬅️ В город",callback_data="city:home"); await call.message.edit_text(text,reply_markup=b.as_markup())
    elif key=="buylisting":
        mid=int(action[2]); listing=cursor.execute("SELECT object_type,object_id,seller_id,price FROM city_market WHERE id=?",(mid,)).fetchone()
        if not listing:return await call.message.edit_text("❌ Объявление уже недоступно.",reply_markup=back_home())
        typ,oid,seller,price=listing
        if seller==uid:return await call.message.edit_text("❌ Нельзя купить собственное объявление.",reply_markup=back_home())
        if user_balance(uid)<price:return await call.message.edit_text("❌ Недостаточно денег.",reply_markup=back_home())
        if typ=="car":
            car=cursor.execute("SELECT car_type FROM city_vehicles WHERE id=? AND user_id=? AND for_sale=1",(oid,seller)).fetchone()
            if not car:return await call.message.edit_text("❌ Машина уже продана.",reply_markup=back_home())
            if garage_count(uid)<=cursor.execute("SELECT COUNT(*) FROM city_vehicles WHERE user_id=?",(uid,)).fetchone()[0]:return await call.message.edit_text("🔒 В вашем гараже нет места.",reply_markup=back_home())
            cursor.execute("UPDATE city_vehicles SET user_id=?,for_sale=0,sale_price=0 WHERE id=?",(uid,oid))
        elif typ=="business":
            biz=cursor.execute("SELECT id FROM city_businesses WHERE id=? AND user_id=? AND for_sale=1",(oid,seller)).fetchone()
            if not biz:return await call.message.edit_text("❌ Бизнес уже продан.",reply_markup=back_home())
            cursor.execute("UPDATE city_businesses SET user_id=?,for_sale=0,sale_price=0 WHERE id=?",(uid,oid))
        else:return await call.message.edit_text("❌ Неизвестный тип объекта.",reply_markup=back_home())
        add_cash(uid,-price); add_cash(seller,price); cursor.execute("DELETE FROM city_market WHERE id=?",(mid,)); conn.commit()
        await call.message.edit_text(f"✅ Покупка завершена.\n💵 Списано: {format_money(price)}",reply_markup=back_home())
    elif key=="races":
        cars=cursor.execute("SELECT id,car_type FROM city_vehicles WHERE user_id=?",(uid,)).fetchall();
        if not cars:return await call.message.edit_text("🏁 Для гонок нужна машина.",reply_markup=back_home())
        text="🏁 <b>Гонки</b>\n\nВыберите свою машину для поиска соперника."; b=InlineKeyboardBuilder()
        for cid,ct in cars:b.button(text=f"🏁 {CARS[ct]['name']}",callback_data=f"city:race:{cid}")
        b.adjust(1); b.button(text="⬅️ В город",callback_data="city:home"); await call.message.edit_text(text,reply_markup=b.as_markup())
    elif key=="race":
        vid=int(action[2]); car=cursor.execute("SELECT car_type FROM city_vehicles WHERE id=? AND user_id=?",(vid,uid)).fetchone()
        if not car:return await call.message.edit_text("❌ Машина не найдена.",reply_markup=back_home())
        pending=cursor.execute("SELECT id,creator_id,creator_car FROM city_races WHERE status='waiting' AND creator_id!=? ORDER BY id LIMIT 1",(uid,)).fetchone()
        if not pending:
            cursor.execute("INSERT INTO city_races(creator_id,creator_car,status,created_at) VALUES(?,?,?,?)",(uid,vid,'waiting',int(time.time()))); conn.commit(); return await call.message.edit_text("🏁 Заявка создана.\nОжидаем другого игрока.",reply_markup=back_home())
        rid,creator,creator_car=pending
        c1=cursor.execute("SELECT car_type FROM city_vehicles WHERE id=?",(creator_car,)).fetchone(); c2=car
        score1=CARS[c1[0]]['power']+CARS[c1[0]]['speed']*.7+CARS[c1[0]]['handling']*10-CARS[c1[0]]['accel']*20
        score2=CARS[c2[0]]['power']+CARS[c2[0]]['speed']*.7+CARS[c2[0]]['handling']*10-CARS[c2[0]]['accel']*20
        winner=creator if score1>=score2 else uid
        prize=50_000
        add_cash(winner,prize); cursor.execute("UPDATE city_races SET opponent_id=?,opponent_car=?,status='finished',winner_id=? WHERE id=?",(uid,vid,winner,rid)); conn.commit()
        await call.message.edit_text(f"🏁 <b>Гонка завершена!</b>\n\n🏆 Победитель: {'вы' if winner==uid else 'соперник'}\n💰 Приз: {format_money(prize)}",reply_markup=back_home())
    elif key=="help":
        await call.message.edit_text("ℹ️ <b>Город</b>\n\nВсе основные действия выполняются кнопками в ЛС. Дом открывает гараж и бизнесы, машины участвуют в гонках и тюнинге, бизнесы приносят доход и формируют налог.",reply_markup=back_home())


async def citysellcar(message: types.Message):
    if message.chat.type != 'private': return
    p=message.text.split()
    if len(p)!=3:return await message.answer("Формат: /citysellcar ID_МАШИНЫ ЦЕНА")
    try: vid=int(p[1]); price=int(p[2])
    except ValueError:return await message.answer("❌ ID и цена должны быть числами.")
    row=cursor.execute("SELECT car_type,for_sale FROM city_vehicles WHERE id=? AND user_id=?",(vid,message.from_user.id)).fetchone()
    if not row:return await message.answer("❌ Машина не найдена.")
    if row[1]:return await message.answer("❌ Машина уже выставлена.")
    if price<=0:return await message.answer("❌ Цена должна быть положительной.")
    cursor.execute("UPDATE city_vehicles SET for_sale=1,sale_price=? WHERE id=?",(price,vid)); cursor.execute("INSERT INTO city_market(seller_id,object_type,object_id,price,created_at) VALUES(?,?,?,?,?)",(message.from_user.id,'car',vid,price,int(time.time()))); conn.commit()
    await message.answer(f"🔨 <b>{CARS[row[0]]['name']}</b> выставлена на рынок за <b>{format_money(price)}</b>.")

async def citysellbiz(message: types.Message):
    if message.chat.type != 'private': return
    p=message.text.split()
    if len(p)!=3:return await message.answer("Формат: /citysellbiz ID_БИЗНЕСА ЦЕНА")
    try: bid=int(p[1]); price=int(p[2])
    except ValueError:return await message.answer("❌ ID и цена должны быть числами.")
    row=cursor.execute("SELECT business_type,for_sale FROM city_businesses WHERE id=? AND user_id=?",(bid,message.from_user.id)).fetchone()
    if not row:return await message.answer("❌ Бизнес не найден.")
    if row[1]:return await message.answer("❌ Бизнес уже выставлен.")
    if price<=0:return await message.answer("❌ Цена должна быть положительной.")
    cursor.execute("UPDATE city_businesses SET for_sale=1,sale_price=? WHERE id=?",(price,bid)); cursor.execute("INSERT INTO city_market(seller_id,object_type,object_id,price,created_at) VALUES(?,?,?,?,?)",(message.from_user.id,'business',bid,price,int(time.time()))); conn.commit()
    await message.answer(f"🔨 <b>{BUSINESSES[row[0]]['name']}</b> выставлен на рынок за <b>{format_money(price)}</b>.")

async def cityloanpay(message: types.Message):
    if message.chat.type!='private': return
    row=get_city(message.from_user.id); debt=row[8]
    if debt<=0:return await message.answer("✅ У вас нет кредита.")
    if user_balance(message.from_user.id)<debt:return await message.answer(f"❌ Для погашения нужно {format_money(debt)}.")
    add_cash(message.from_user.id,-debt); cursor.execute("UPDATE city_player SET debt=0 WHERE user_id=?",(message.from_user.id,)); conn.commit(); await message.answer(f"✅ Кредит погашен: {format_money(debt)}")

# ---------- admin ----------

def is_admin(uid: int) -> bool:
    return uid in cfg.admin


async def admin_panel(message: types.Message):
    if message.chat.type != 'private' or not is_admin(message.from_user.id): return
    users=cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    biz=cursor.execute("SELECT COUNT(*) FROM city_businesses").fetchone()[0]
    cars=cursor.execute("SELECT COUNT(*) FROM city_vehicles").fetchone()[0]
    b=InlineKeyboardBuilder(); b.button(text="📊 Статистика",callback_data="cityadmin:stats"); b.button(text="💰 Выдать деньги",callback_data="cityadmin:give"); b.button(text="🏢 Бизнесы",callback_data="cityadmin:biz"); b.button(text="🧾 Налоги",callback_data="cityadmin:tax"); b.adjust(2)
    await message.answer(f"🛠 <b>Админ-панель City</b>\n\n👤 Игроков: {users}\n🚗 Машин: {cars}\n🏢 Бизнесов: {biz}",reply_markup=b.as_markup())

async def admin_cb(call: types.CallbackQuery):
    if not is_admin(call.from_user.id): return await call.answer("Нет доступа",show_alert=True)
    await call.answer()
    key=call.data.split(":")[1]
    if key=='stats':
        cash=cursor.execute("SELECT COALESCE(SUM(CAST(balance AS INTEGER)),0) FROM users").fetchone()[0]; bank=cursor.execute("SELECT COALESCE(SUM(CAST(bank AS INTEGER)),0) FROM users").fetchone()[0]
        await call.message.edit_text(f"📊 <b>Статистика</b>\n\n💵 Наличные: {format_money(cash)}\n🏦 Банки: {format_money(bank)}\n🚗 Машин: {cursor.execute('SELECT COUNT(*) FROM city_vehicles').fetchone()[0]}\n🏢 Бизнесов: {cursor.execute('SELECT COUNT(*) FROM city_businesses').fetchone()[0]}")
    elif key=='tax':
        accrue_businesses(); total=cursor.execute("SELECT COALESCE(SUM(tax_due),0) FROM city_businesses").fetchone()[0]
        await call.message.edit_text(f"🧾 Налоговая задолженность всех бизнесов: <b>{format_money(total)}</b>")
    elif key=='biz':
        rows=cursor.execute("SELECT business_type,COUNT(*),COALESCE(SUM(balance),0),COALESCE(SUM(tax_due),0) FROM city_businesses GROUP BY business_type").fetchall()
        text="🏢 <b>Бизнесы</b>\n\n"+"\n".join(f"{BUSINESSES[r[0]]['name']}: {r[1]} шт. · {format_money(r[2])} · налог {format_money(r[3])}" for r in rows)
        await call.message.edit_text(text or "🏢 Бизнесов нет.")
    elif key=='give':
        await call.message.edit_text("💰 Используйте /citygive USER_ID AMOUNT")

async def citygive(message: types.Message):
    if not is_admin(message.from_user.id): return
    p=message.text.split()
    if len(p)!=3: return await message.answer("Формат: /citygive USER_ID AMOUNT")
    try: uid=int(p[1]); amount=int(p[2])
    except ValueError: return await message.answer("❌ Неверные числа.")
    if not cursor.execute("SELECT 1 FROM users WHERE user_id=?",(uid,)).fetchone(): return await message.answer("❌ Игрок не найден.")
    add_cash(uid,amount); conn.commit(); await message.answer(f"✅ Игроку {uid} выдано {format_money(amount)}")


def reg(dp: Dispatcher):
    dp.message.register(city_cmd, Command("city"))
    dp.message.register(citysellcar, Command("citysellcar"))
    dp.message.register(citysellbiz, Command("citysellbiz"))
    dp.message.register(cityloanpay, Command("cityloanpay"))
    dp.message.register(admin_panel, Command("cityadmin"))
    dp.message.register(citygive, Command("citygive"))
    dp.callback_query.register(city_callback, F.data.startswith("city:"))
    dp.callback_query.register(admin_cb, F.data.startswith("cityadmin:"))
