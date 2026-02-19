from decimal import Decimal

from aiogram import types, Dispatcher

from commands.db import getperevod, url_name, cursor
from commands.admin.db import give_bcoins_db, give_money_db
from filters.custom import TextIn, StartsWith
from user import BFGuser, BFGconst
from assets.transform import transform_int as tr
from commands.admin.game_log import new_log
from assets.antispam import antispam, admin_only
import config as cfg


def get_limit_cmd(status: int) -> int:
    """Получить лимит на дневную передачу"""
    limits = {
        1: 1_000_000_000,
        2: 5_000_000_000,
        3: 9_500_000,  # Здесь была ошибка (не хватало нулей)? Исправлю на 9.5 млрд
        4: 30_000_000_000,
    }
    return limits.get(status, 500_000_000)  # Для статуса 0


async def get_user_id_by_input(input_str: str) -> int | None:
    """Получение user_id по игровому ID или Telegram ID"""
    try:
        # Пробуем найти по game_id
        result = cursor.execute(
            "SELECT user_id FROM users WHERE game_id = ?", 
            (int(input_str),)
        ).fetchone()
        if result:
            return result[0]
        
        # Если не нашли, пробуем как Telegram ID
        result = cursor.execute(
            "SELECT user_id FROM users WHERE user_id = ?", 
            (int(input_str),)
        ).fetchone()
        if result:
            return result[0]
    except ValueError:
        return None
    return None


@antispam
async def transfer_cmd(message: types.Message, user: BFGuser):
    user_id = message.from_user.id
    win, lose = BFGconst.emj()
    limit = get_limit_cmd(user.status)
    
    target_user_id = None
    target_url = None
    
    # Случай 1: Перевод по реплаю (ответ на сообщение)
    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
        target_url = await url_name(target_user_id)
    
    # Случай 2: Перевод по ID (игровому или Telegram)
    else:
        try:
            args = message.text.split()
            if len(args) < 2:
                await message.reply(
                    f"{user.url}, чтобы передать деньги нужно ответить на сообщение пользователя "
                    f"или указать ID. Пример: дать 105 1000000"
                )
                return
            
            target_input = args[1]
            target_user_id = await get_user_id_by_input(target_input)
            
            if not target_user_id:
                await message.reply(f"{user.url}, пользователь с ID {target_input} не найден {lose}")
                return
            
            target_url = await url_name(target_user_id)
            
            # Проверяем, не переводим ли мы сами себе
            if user_id == target_user_id:
                await message.reply(f"{user.url}, нельзя переводить деньги самому себе {lose}")
                return
            
            # Получаем сумму (она может быть вторым или третьим аргументом)
            if len(args) >= 3:
                summ_str = args[2]
            else:
                summ_str = args[1]  # Если ID не указан, но это уже обработано выше
                
        except Exception as e:
            await message.reply(f"{user.url}, ошибка в формате команды {lose}")
            return

    try:
        summ = summ_str.replace("е", "e")
        summ = int(float(summ))
    except:
        await message.reply(f"{user.url}, вы не ввели сумму которую хотите передать игроку {lose}")
        return

    # Проверка лимита
    total_limit = Decimal(str(limit)) + Decimal(str(user.perlimit))
    d_per = Decimal(str(user.per)) + Decimal(str(summ))

    if d_per > total_limit:
        await message.reply(
            f"{user.url}, вы уже исчерпали свой дневной лимит передачи денег.\n"
            f"Лимит: {tr(total_limit)}$, осталось: {tr(total_limit - Decimal(str(user.per)))}$"
        )
        return

    if summ <= 0:
        await message.reply(f"{user.url}, вы не можете передать отрицательное число игроку {lose}")
        return

    if int(user.balance) >= summ:
        # Отправляем уведомление получателю
        try:
            sender_name = message.from_user.full_name
            await message.bot.send_message(
                target_user_id,
                f"💸 <b>Вам перевели деньги!</b>\n\n"
                f"👤 Отправитель: {sender_name}\n"
                f"💰 Сумма: {tr(summ)}$\n\n"
                f"💵 Ваш новый баланс скоро обновится.",
                parse_mode="HTML"
            )
        except Exception as e:
            # Если не удалось отправить уведомление
            print(f"Не удалось отправить уведомление пользователю {target_user_id}: {e}")
        
        await message.answer(f"Вы передали {tr(summ)}$ игроку {target_url} {win}")
        await getperevod(summ, user_id, target_user_id)
        await new_log(f"#перевод\n{user_id}\nСумма: {tr(summ)}\nПередал: {target_user_id}", "money_transfers")
    else:
        await message.reply(f"{user.url}, вы не можете передать больше чем у вас есть на балансе {lose}")


@antispam
async def limit_cmd(message: types.Message, user: BFGuser):
    limit = get_limit_cmd(user.status)

    total_limit = int(limit) + int(user.perlimit)
    per = int(user.per)
    ost = total_limit - per

    await message.reply(f"""{user.url}, здесь ваш лимит на сегодня: {tr(total_limit)}$
💫 Вы уже передали: {tr(per)}$
🚀 У вас осталось: {tr(ost)}$ для передачи!""")


@antispam
async def give_money(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()

    # Проверка прав администратора
    if not (user.user_id in cfg.admin or user.status == 4):
        await message.answer(
            "👮‍♂️ Вы не являетесь администратором бота чтобы использовать данную команду.\n"
            "Для покупки введи команду \"Донат\"")
        return

    target_user_id = None
    target_url = None

    # Случай 1: Выдача по реплаю
    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
        target_url = await url_name(target_user_id)
    
    # Случай 2: Выдача по ID
    else:
        try:
            args = message.text.split()
            if len(args) < 3:
                await message.answer(
                    f"{user.url}, укажите ID и сумму. Пример: выдать 105 1000000"
                )
                return
            
            target_input = args[1]
            target_user_id = await get_user_id_by_input(target_input)
            
            if not target_user_id:
                await message.answer(f"{user.url}, пользователь с ID {target_input} не найден {lose}")
                return
            
            target_url = await url_name(target_user_id)
            summ_str = args[2]
            
        except Exception as e:
            await message.answer(f"{user.url}, ошибка в формате команды {lose}")
            return

    try:
        summ = summ_str.replace("е", "e")
        summ = int(float(summ))
    except:
        await message.answer(f"{user.url}, вы не ввели сумму которую хотите выдать {lose}")
        return

    if user.user_id in cfg.admin:
        await give_money_db(user.user_id, target_user_id, summ, "rab")
        await message.answer(f"{user.url}, вы выдали {tr(summ)}$ пользователю {target_url}  {win}")
    else:
        res = await give_money_db(user.user_id, target_user_id, summ, "adm")
        if res == "limit":
            await message.answer(f"{user.url}, вы достигли лимита на выдачу денег {lose}")
            return
        await message.answer(f"{user.url}, вы выдали {tr(summ)}$ пользователю {target_url}  {win}")

    await new_log(f"#выдача\nИгрок {user.user_id}\nСумма: {tr(summ)}$\nИгроку {target_user_id}", "issuance_money")


@admin_only()
async def give_bcoins(message: types.Message):
    user_id = message.from_user.id
    win, lose = BFGconst.emj()

    target_user_id = None
    target_url = None

    # Случай 1: Выдача по реплаю
    if message.reply_to_message:
        target_user_id = message.reply_to_message.from_user.id
        target_url = await url_name(target_user_id)
    
    # Случай 2: Выдача по ID
    else:
        try:
            args = message.text.split()
            if len(args) < 3:
                await message.answer(
                    f"Админ, укажите ID и сумму. Пример: бдать 105 100"
                )
                return
            
            target_input = args[1]
            target_user_id = await get_user_id_by_input(target_input)
            
            if not target_user_id:
                await message.answer(f"Админ, пользователь с ID {target_input} не найден {lose}")
                return
            
            target_url = await url_name(target_user_id)
            summ_str = args[2]
            
        except Exception as e:
            await message.answer(f"Админ, ошибка в формате команды {lose}")
            return

    try:
        summ = summ_str.replace("е", "e")
        summ = int(float(summ))
    except:
        await message.answer(f"Админ, вы не ввели сумму которую хотите выдать {lose}")
        return

    await give_bcoins_db(target_user_id, summ)
    await message.answer(f"Админ, вы выдали {tr(summ)}💳 пользователю {target_url}  {win}")
    await new_log(f"#бкоин-выдача\nАдмин {user_id}\nСумма: {tr(summ)}$\nПользователю {target_user_id}", "issuance_bcoins")


def reg(dp: Dispatcher):
    dp.message.register(limit_cmd, TextIn("мой лимит"))
    dp.message.register(transfer_cmd, StartsWith("дать"))
    dp.message.register(give_money, StartsWith("выдать"))
    dp.message.register(give_bcoins, StartsWith("бдать"))
