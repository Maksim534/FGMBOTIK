from aiogram import Dispatcher, types

from assets.antispam import antispam, new_earning_msg, antispam_earning
from commands.db import getpofildb, chek_user, cursor
from commands.basic.property import lists
from filters.custom import TextIn, StartsWith
from user import BFGuser, BFGconst
from assets import keyboards as kb
import config as cfg
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


@antispam
async def balance_cmd(message: types.Message, user: BFGuser):
    await message.answer(
        f"""
👫 <b>Имя:</b> <code>{user.name}</code>
💵 <b>Наличные:</b> <code>{user.balance.tr()}$</code>
🏦 <b>Банковский счет:</b> <code>{user.bank.tr()}$</code>
🌐 <b>Криптовалюта:</b> <code>{user.btc.tr()}🌐</code>

{BFGconst.ads}
""",
        reply_markup=balance_keyboard(user.id),
        parse_mode="HTML"
    )


@antispam
async def btc_cmd(message: types.Message, user: BFGuser):
    await message.answer(f"{user.url}, на вашем балансе {user.btc.tr()} BTC 🌐")

def balance_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру для быстрых действий с балансом"""
    builder = InlineKeyboardBuilder()
    
    # Первый ряд: две кнопки (банк)
    builder.row(
        InlineKeyboardButton(
            text="🏦 Банк положить",
            switch_inline_query_current_chat=f"банк положить "
        ),
        InlineKeyboardButton(
            text="🏧 Банк снять",
            switch_inline_query_current_chat=f"банк снять "
        ),
        width=2
    )
    
    # Второй ряд: одна кнопка (банк)
    builder.row(
        InlineKeyboardButton(
            text="🏛 Банк (информация)",
            switch_inline_query_current_chat=f"банк"
        ),
        width=1
    )
    
    return builder.as_markup()


async def creat_help_msg(profil, user: BFGuser):
    profil = profil.format(user.url)

    text = f"""{profil}

🆔 <b>ID:</b> {user.game_id}
👤 <b>Имя:</b> {user.name}
🏆 <b>Статус:</b> {user.Fstatus}
💰 <b>Наличные:</b> {user.balance.tr()}$
🏦 <b>В банке:</b> {user.bank.tr()}$
💳 <b>B-Coins:</b> {user.bcoins.tr()}
🌐 <b>Биткоины:</b> {user.btc.tr()} BTC
⚡️ <b>Энергия:</b> {user.energy}
👑 <b>Рейтинг:</b> {user.rating.tr()}
💡 <b>Опыт:</b> {user.expe.tr()}
🎲 <b>Игр:</b> {user.games.tr()}

{BFGconst.ads}
"""
    return text


@antispam
async def profil_cmd(message: types.Message, user: BFGuser):
    args = message.text.split()
    
    # Если есть аргументы - пытаемся показать чужой профиль
    if len(args) >= 2:
        # Проверка прав администратора (если нужно)
        if user.status != 4:
            await message.answer("❌ Эта команда доступна только администраторам.")
            return
            
        try:
            search_id = int(args[1])
            target_user_id = None

            # 1. Пробуем найти по game_id
            result = cursor.execute(
                "SELECT user_id FROM users WHERE game_id = ?", 
                (search_id,)
            ).fetchone()

            if result:
                target_user_id = result[0]
            else:
                # 2. Если не нашли, пробуем найти по user_id
                result = cursor.execute(
                    "SELECT user_id FROM users WHERE user_id = ?", 
                    (search_id,)
                ).fetchone()
                if result:
                    target_user_id = search_id  # search_id и есть user_id

            # Если пользователь не найден ни по одному ID
            if not target_user_id:
                await message.answer(f"❌ Пользователь с ID <b>{search_id}</b> не найден.")
                return

            # Получаем данные целевого пользователя
            target_user = BFGuser(not_class=target_user_id)
            await target_user.update()
            
            # Показываем профиль
            text = await creat_help_msg("Профиль игрока {0}:", target_user)
            msg = await message.answer(text, reply_markup=kb.profile(target_user.user_id))
            
        except ValueError:
            await message.answer("❌ Неверный формат. ID должен быть числом.")
            return
    else:
        # Нет аргументов - показываем свой профиль
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
async def get_id_cmd(message: types.Message, user: BFGuser):
    """Команда /id - показывает ID пользователя (по реплаю или свой)"""
    win, lose = BFGconst.emj()
    
    # Если это ответ на сообщение - показываем ID того, на кого ответили
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        target_id = target_user.id
        target_name = target_user.full_name
        
        # Ищем игровой ID в базе
        game_id_data = cursor.execute(
            "SELECT game_id FROM users WHERE user_id = ?", 
            (target_id,)
        ).fetchone()
        
        if game_id_data:
            game_id = game_id_data[0]
            await message.answer(
                f"{user.url}, информация о пользователе {target_name}:\n\n"
                f"🆔 <b>Telegram ID:</b> <code>{target_id}</code>\n"
                f"🎮 <b>Игровой ID:</b> <code>{game_id}</code>\n"
                f"<code>═══════════════════</code>\n"
                f"📝 Чтобы получить информацию о другом пользователе, "
                f"ответьте на его сообщение командой /id",
                parse_mode="HTML"
            )
        else:
            await message.answer(
                f"{user.url}, пользователь {target_name} не зарегистрирован в боте.",
                parse_mode="HTML"
            )
    
    # Если команда без реплая - показываем свой ID
    else:
        # Получаем свой игровой ID
        game_id_data = cursor.execute(
            "SELECT game_id FROM users WHERE user_id = ?", 
            (user.id,)
        ).fetchone()
        game_id = game_id_data[0] if game_id_data else "не найден"
        
        await message.answer(
            f"{user.url}, ваш профиль:\n\n"
            f"🆔 <b>Telegram ID:</b> <code>{user.id}</code>\n"
            f"🎮 <b>Игровой ID:</b> <code>{game_id}</code>\n"
            f"<code>═══════════════════</code>",  # 👈 ИСПРАВЛЕНО
            parse_mode="HTML"
        )

@antispam
async def getuser_cmd(message: types.Message, user: BFGuser):
    """Команда /getuser [игровой ID] - показывает Telegram ID и имя пользователя"""
    win, lose = BFGconst.emj()
    
    # Проверяем наличие аргумента
    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            f"{user.url}, укажите игровой ID.\n"
            f"📌 Пример: /getuser 105",
            parse_mode="HTML"
        )
        return
    
    try:
        game_id = int(args[1])
    except ValueError:
        await message.answer(f"{user.url}, игровой ID должен быть числом.")
        return
    
    # Ищем пользователя по game_id
    result = cursor.execute(
        "SELECT user_id, name FROM users WHERE game_id = ?", 
        (game_id,)
    ).fetchone()
    
    if not result:
        await message.answer(
            f"{user.url}, пользователь с игровым ID <b>{game_id}</b> не найден.",
            parse_mode="HTML"
        )
        return
    
    user_id, name = result
    
    # Красиво оформляем ответ
    await message.answer(
        f"{user.url}, информация по игровому ID <b>{game_id}</b>:\n\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n"
        f"<code>═══════════════════</code>",
        parse_mode="HTML"
    )


def reg(dp: Dispatcher):
    dp.message.register(get_id_cmd, StartsWith("айди"))
    dp.message.register(balance_cmd, TextIn("б", "баланс"))
    dp.message.register(btc_cmd, TextIn("биткоины"))
    dp.message.register(getuser_cmd, StartsWith("/getuser"))
    dp.message.register(profil_cmd, StartsWith("профиль"))
    dp.callback_query.register(profil_busines, StartsWith("profil-busines"))
    dp.callback_query.register(profil_back, StartsWith("profil-back"))
    dp.callback_query.register(profil_property, StartsWith("profil-property"))
