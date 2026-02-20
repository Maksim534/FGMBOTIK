import re
from aiogram import types, Dispatcher
from aiogram.filters import Command

from assets.antispam import antispam
from commands.entertaining.db import get_wedlock
from commands.db import url_name, get_name
from user import BFGuser, BFGconst
from bot import bot

# RP команды для пар
COUPLE_ACTIONS = {
    "обнять": "💞 {} нежно обнял(а) {}",
    "поцеловать": "💋 {} сладко поцеловал(а) {}",
    "погладить": "💖 {} погладил(а) {} по головке",
    "прижать": "🤗 {} прижал(а) {} к себе",
    "ущипнуть": "😜 {} игриво ущипнул(а) {}",
    "прошептать": "🤫 {} прошептал(а) {} на ушко",
    "покормить": "🍜 {} покормил(а) {} вкусняшкой",
    "разбудить": "☀️ {} разбудил(а) {} поцелуем",
    "укутать": "🧣 {} укутал(а) {} в плед",
    "согреть": "🔥 {} согрел(а) своим теплом {}",
    "похвалить": "🌟 {} похвалил(а) {}",
    "рассмешить": "😂 {} рассмешил(а) {}",
    "пожалеть": "🥺 {} пожалел(а) {}",
    "потанцевать": "💃 {} потанцевал(а) с {}",
    "признаться": "💕 {} признался(ась) в любви {}",
}

# Составим регулярное выражение для поиска команд
actions_pattern = "|".join(re.escape(key) for key in COUPLE_ACTIONS.keys())
pattern = rf"^\.отн\s+({actions_pattern})$"


@antispam
async def rp_couple_cmd(message: types.Message, user: BFGuser):
    print(f"🔥 Текст сообщения: '{message.text}'")
    print(f"🔍 Начинается с .отн: {message.text.startswith('.отн')}")
    """Обработка RP-команд для пары (только в ЛС)"""
    win, lose = BFGconst.emj()
    
    # Проверяем, что команда вызвана в личных сообщениях
    if message.chat.type != "private":
        await message.answer(f"{user.url}, RP-команды для пары работают только в личных сообщениях бота! 🤫")
        return
    
    # Проверяем, состоит ли пользователь в браке
    couple_data = await get_wedlock(user.id)
    if not couple_data:
        await message.answer(
            f"{user.url}, у вас нет пары! Сначала найдите свою половинку через 💍 <b>свадьбу</b>",
            parse_mode="HTML"
        )
        return
    
    # Определяем, кто партнёр
    partner_id = couple_data[0] if couple_data[1] == user.id else couple_data[1]
    
    # Получаем действие из сообщения
    match = re.search(pattern, message.text.lower().strip())
    if not match:
        return
    
    action = match.group(1)  # Извлекаем действие (обнять, поцеловать и т.д.)
    
    # Получаем имена для красивого отображения
    user_name = message.from_user.full_name
    partner_name = await get_name(partner_id)
    partner_url = await url_name(partner_id)
    
    # Формируем текст действия
    action_text = COUPLE_ACTIONS[action].format(
        f"<a href='tg://user?id={user.id}'>{user_name}</a>",
        partner_url
    )
    
    # Отправляем уведомление партнёру в ЛС
    try:
        await bot.send_message(
            partner_id,
            f"💌 <b>Романтическое уведомление</b>\n\n"
            f"{action_text}\n\n"
            f"<i>Ответь своей половинке взаимностью через .отн [действие]</i>",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Не удалось отправить уведомление партнёру {partner_id}: {e}")
    
    # Отправляем подтверждение отправителю
    await message.answer(
        f"✅ <b>Действие отправлено!</b>\n\n"
        f"{action_text}",
        parse_mode="HTML"
    )


def reg(dp: Dispatcher):
    dp.message.register(rp_couple_cmd, lambda msg: msg.text and msg.text.startswith(".отн "))
