from aiogram import Dispatcher, types

from assets.antispam import antispam, new_earning_msg, antispam_earning
from commands.db import getpofildb, chek_user, cursor
from commands.basic.property import lists
from filters.custom import TextIn, StartsWith
from user import BFGuser, BFGconst
from assets import keyboards as kb


@antispam
async def balance_cmd(message: types.Message, user: BFGuser):
    await message.answer(f"""
👫  Имя: {user.name}
💵  Наличные: {user.balance.tr()}$
💴  Йены: {user.yen.tr()}¥
🏦  Банковский счет: {user.bank.tr()}$
🌐  Криптовалюта: {user.btc.tr()}🌐


{BFGconst.ads}""")


@antispam
async def btc_cmd(message: types.Message, user: BFGuser):
    await message.answer(f"{user.url}, на вашем балансе {user.btc.tr()} BTC 🌐")


async def creat_help_msg(profil, user: BFGuser):
    profil = profil.format(user.url)

    text = f"""{profil}
🪪 ID: {user.game_id}
🏆 Статус: {user.Fstatus}
💰 Денег: {user.balance.tr()}$
💴 Йены: {user.yen.tr()}¥
🏦 В банке: {user.bank.tr()}$
💳 B-Coins: {user.bcoins.tr()}
💽 Биткоины: {user.btc.tr()}฿
🏋 Энергия: {user.energy}
👑 Рейтинг: {user.rating.tr()}
🌟 Опыт: {user.expe.tr()}
🎲 Всего сыграно игр: {user.games.tr()}

"""
    return text


@antispam
async def profil_cmd(message: types.Message, user: BFGuser):
    # Разбираем аргументы команды
    args = message.text.split()
    
    # Если есть второй аргумент (ID) - пытаемся показать чужой профиль
    if len(args) >= 2:
        # Проверяем, является ли пользователь администратором (статус 4)
        if user.status != 4:
            await message.answer(f"❌ Эта команда доступна только администраторам.")
            return
            
        try:
            target_id = int(args[1])
            
            # Проверяем, существует ли пользователь с таким ID
            if not await chek_user(target_id):
                await message.answer(f"❌ Игрок с ID <b>{target_id}</b> не найден. Перепроверьте ID.")
                return
            
            # Получаем данные целевого пользователя
            target_user = BFGuser(not_class=target_id)
            await target_user.update()
            
            # Показываем профиль целевого пользователя
            text = await creat_help_msg("Профиль игрока {0}:", target_user)
            msg = await message.answer(
                text, 
                reply_markup=kb.profile(target_user.user_id)
            )
            
        except ValueError:
            await message.answer("❌ Неверный формат ID. ID должен быть числом.")
            return
    else:
        # Если аргументов нет - показываем свой профиль (доступно всем)
        text = await creat_help_msg("{0}, ваш профиль:", user)
        msg = await message.answer(text, reply_markup=kb.profile(user.user_id))
    
    await new_earning_msg(msg.chat.id, msg.message_id)


@antispam_earning
async def profil_busines(call: types.CallbackQuery, user: BFGuser):
    _, business, _ = await getpofildb(call.from_user.id)

    txt = ""
    if business[0]: txt += "\n  🔋 Ферма: Майнинг ферма"
    if business[1]: txt += "\n  💼 Бизнес: Бизнес"
    if business[2]: txt += "\n  🌳 Сад: Сад"
    if business[3]: txt += "\n  ⛏ Генератор: Генератор"
    if txt == "": txt = "\n🥲 У вас нету бизнесов"

    await call.message.edit_text(text=f"🧳 Ваши бизнесы:{txt}", reply_markup=kb.profile_back(call.from_user.id))


@antispam_earning
async def profil_property(call: types.CallbackQuery, user: BFGuser):
    _, _, data = await getpofildb(call.from_user.id)

    txt = ""
    if data[4]:
        name = lists.phones.get(data[4])
        txt += f"\n  📱 Телефон: {name[0]}"

    if data[2]:
        name = lists.cars.get(data[2])
        txt += f"\n  🚘 Машина: {name[0]}"

    if data[1]:
        name = lists.helicopters.get(data[1])
        txt += f"\n  🚁 Вертолёт: {name[0]}"

    if data[6]:
        name = lists.planes.get(data[6])
        txt += f"\n  🛩 Самолёт: {name[0]}"

    if data[3]:
        name = lists.yahts.get(data[3])
        txt += f"\n  🛥 Яхта: {name[0]}"

    if data[5]:
        name = lists.house.get(data[5])
        txt += f"\n  🏠 Дом: {name[0]}"

    if txt == "": txt = "\n🥲 У вас нету имущества"

    await call.message.edit_text(text=f"📦 Ваше имущество:{txt}", reply_markup=kb.profile_back(call.from_user.id))


@antispam_earning
async def profil_back(call: types.CallbackQuery, user: BFGuser):
    text = await creat_help_msg("{0}, ваш профиль:", user)
    await call.message.edit_text(text=text, reply_markup=kb.profile(call.from_user.id))

@antispam
async def find_id_cmd(message: types.Message, user: BFGuser):
    """Команда /айди - поиск информации о пользователе по ID"""
    win, lose = BFGconst.emj()
    
    # Проверяем наличие аргумента
    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            f"{user.url}, укажите ID для поиска.\n"
            f"📌 Примеры:\n"
            f"• `/айди 105` - поиск по игровому ID\n"
            f"• `/айди 123456789` - поиск по Telegram ID",
            parse_mode="Markdown"
        )
        return
    
    try:
        search_id = int(args[1])
    except ValueError:
        await message.answer(f"{user.url}, ID должен быть числом.")
        return
    
    # Пытаемся найти пользователя
    user_info = None
    found_by = None
    
    # Сначала ищем по game_id (игровой ID)
    result = cursor.execute(
        "SELECT user_id, game_id, name FROM users WHERE game_id = ?", 
        (search_id,)
    ).fetchone()
    
    if result:
        user_info = result
        found_by = "game_id"
    else:
        # Если не нашли по game_id, ищем по user_id (Telegram ID)
        result = cursor.execute(
            "SELECT user_id, game_id, name FROM users WHERE user_id = ?", 
            (search_id,)
        ).fetchone()
        
        if result:
            user_info = result
            found_by = "user_id"
    
    if not user_info:
        await message.answer(
            f"{user.url}, пользователь с ID <b>{search_id}</b> не найден.\n"
            f"Проверьте правильность ввода.",
            parse_mode="HTML"
        )
        return
    
    telegram_id, game_id, name = user_info
    
    # Формируем информативное сообщение
    search_method = "🔍 Найден по игровому ID" if found_by == "game_id" else "🔍 Найден по Telegram ID"
    
    response = (
        f"{user.url}, информация о пользователе:\n\n"
        f"{search_method}\n"
        f"<code>═══════════════════</code>\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"🆔 <b>Telegram ID:</b> <code>{telegram_id}</code>\n"
        f"🎮 <b>Игровой ID:</b> <code>{game_id}</code>\n"
        f"<code>═══════════════════</code>\n"
    )
    
    # Если пользователь ищет самого себя, добавим подсказку
    if telegram_id == user.id:
        response += f"\n✨ Это вы! Эти ID可以使用 для ссылок и переводов."
    
    await message.answer(response, parse_mode="HTML")


def reg(dp: Dispatcher):
    dp.message.register(find_id_cmd, StartsWith("/айди"))
    dp.message.register(find_id_cmd, StartsWith("/id"))
    dp.message.register(balance_cmd, TextIn("б", "баланс"))
    dp.message.register(btc_cmd, TextIn("биткоины"))
    dp.message.register(profil_cmd, StartsWith("профиль"))
    dp.callback_query.register(profil_busines, StartsWith("profil-busines"))
    dp.callback_query.register(profil_back, StartsWith("profil-back"))
    dp.callback_query.register(profil_property, StartsWith("profil-property"))
