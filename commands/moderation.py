from aiogram import types, Dispatcher, F
from aiogram.types import ChatPermissions
from datetime import timedelta, datetime
import re

from assets.antispam import antispam, moderation
from bot import bot
from user import BFGuser

# Конвертер времени: 10м -> 600 секунд, 2ч -> 7200, 1д -> 86400
TIME_UNITS = {
    'м': 60, 'm': 60,
    'ч': 3600, 'h': 3600,
    'д': 86400, 'd': 86400
}

def parse_time(text: str) -> int | None:
    """Извлекает число и единицу времени из строки (например, '10м' -> 600)"""
    match = re.search(r'(\d+)\s*([мчдmhd]?)', text.lower().strip())
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2) or 'м'  # если единица не указана, считаем минуты
    if unit not in TIME_UNITS:
        return None
    return amount * TIME_UNITS[unit]

@antispam
@moderation
async def mute_cmd(message: types.Message, user: BFGuser):
    """Замутить пользователя (ответом на сообщение)"""
    if not message.reply_to_message:
        await message.reply("❌ Ответьте на сообщение пользователя.")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("❌ Укажите время. Пример: мут 10м")
        return

    seconds = parse_time(args[1])
    if not seconds:
        await message.reply("❌ Неверный формат времени. Используйте: 10м, 2ч, 1д")
        return

    target = message.reply_to_message.from_user
    until = timedelta(seconds=seconds)

    await bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=target.id,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=datetime.now() + until
    )

    await message.reply(f"🔇 Пользователь {target.full_name} замучен на {args[1]}.")

@antispam
@moderation
async def unmute_cmd(message: types.Message, user: BFGuser):
    """Снять мут с пользователя"""
    if not message.reply_to_message:
        await message.reply("❌ Ответьте на сообщение пользователя.")
        return

    target = message.reply_to_message.from_user
    await bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=target.id,
        permissions=ChatPermissions(can_send_messages=True),
        until_date=None
    )

    await message.reply(f"🔊 Пользователь {target.full_name} размучен.")

@antispam
@moderation
async def ban_cmd(message: types.Message, user: BFGuser):
    """Забанить пользователя (с временем или навсегда)"""
    if not message.reply_to_message:
        await message.reply("❌ Ответьте на сообщение пользователя.")
        return

    target = message.reply_to_message.from_user
    args = message.text.split()
    until = None

    if len(args) >= 2:
        seconds = parse_time(args[1])
        if seconds:
            until = datetime.now() + timedelta(seconds=seconds)
        else:
            await message.reply("❌ Неверный формат времени. Бан будет вечным.")
            until = None
    else:
        until = None  # вечный бан

    await bot.ban_chat_member(
        chat_id=message.chat.id,
        user_id=target.id,
        until_date=until
    )

    time_str = args[1] if len(args) >= 2 else "навсегда"
    await message.reply(f"⛔ Пользователь {target.full_name} забанен ({time_str}).")

@antispam
@moderation
async def unban_cmd(message: types.Message, user: BFGuser):
    """Разбанить пользователя"""
    if not message.reply_to_message:
        await message.reply("❌ Ответьте на сообщение пользователя.")
        return

    target = message.reply_to_message.from_user
    await bot.unban_chat_member(
        chat_id=message.chat.id,
        user_id=target.id,
        only_if_banned=True
    )

    await message.reply(f"✅ Пользователь {target.full_name} разбанен.")

@antispam
@moderation
async def kick_cmd(message: types.Message, user: BFGuser):
    """Выгнать пользователя (кик)"""
    if not message.reply_to_message:
        await message.reply("❌ Ответьте на сообщение пользователя.")
        return

    target = message.reply_to_message.from_user
    await bot.ban_chat_member(
        chat_id=message.chat.id,
        user_id=target.id,
        until_date=datetime.now() + timedelta(seconds=1)  # баним на секунду
    )
    await bot.unban_chat_member(
        chat_id=message.chat.id,
        user_id=target.id
    )

    await message.reply(f"👢 Пользователь {target.full_name} кикнут.")

def reg(dp: Dispatcher):
    dp.message.register(mute_cmd, F.text.startswith(("мут", "mute")))
    dp.message.register(unmute_cmd, F.text.startswith(("размут", "unmute")))
    dp.message.register(ban_cmd, F.text.startswith(("бан", "ban")))
    dp.message.register(unban_cmd, F.text.startswith(("разбан", "unban")))
    dp.message.register(kick_cmd, F.text.startswith(("кик", "kick")))
