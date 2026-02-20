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


async def is_user_in_chat(chat_id: int, user_id: int) -> bool:
    """Проверяет, находится ли пользователь в чате"""
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False


@antispam
async def rp_couple_cmd(message: types.Message, user: BFGuser):
    """Обработка RP-команд для пары (только в общих чатах)"""
    win, lose = BFGconst.emj()
    
    # Проверяем, что команда вызвана в групповом чате
    if message.chat.type == "private":
        await message.answer(
            f"{user.url}, RP-команды для пары работают только в общих чатах! 🌍\n\n"
            f"Приходите в общий чат со своей половинкой и проявляйте чувства там! 💕",
            parse_mode="HTML"
        )
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
    
    action = match.group(1)
    
    # Получаем имена
    user_name = message.from_user.full_name
    partner_name = await get_name(partner_id)
    partner_url = await url_name(partner_id)
    
    # Формируем текст действия
    action_text = COUPLE_ACTIONS[action].format(
        f"<a href='tg://user?id={user.id}'>{user_name}</a>",
        partner_url
    )
    
    # Проверяем, есть ли партнёр в этом чате
    partner_in_chat = await is_user_in_chat(message.chat.id, partner_id)
    
    if partner_in_chat:
        # Если партнёр в чате - отправляем сообщение
        await message.answer(
            f"💞 <b>Романтический момент</b> 💞\n\n"
            f"{action_text}",
            parse_mode="HTML"
        )
    else:
        # Если партнёра нет в чате
        await message.answer(
            f"{user.url}, вашей половинки нет в этом чате! 😢\n\n"
            f"💭 Пригласи {partner_name} в этот чат, чтобы проявлять свои чувства!",
            parse_mode="HTML"
        )


@antispam
async def rp_couple_list_cmd(message: types.Message, user: BFGuser):
    """Показывает список доступных RP-команд для пары"""
    win, lose = BFGconst.emj()
    
    actions_list = "\n".join([f"  • <code>.отн {action}</code>" for action in COUPLE_ACTIONS.keys()])
    
    await message.answer(
        f"{user.url}, <b>доступные RP-команды для пары:</b>\n\n"
        f"{actions_list}\n\n"
        f"📍 <i>Команды работают только в общих чатах</i>\n"
        f"📍 <i>Оба партнёра должны быть в одном чате</i>\n"
        f"💡 <i>Пример: .отн обнять</i>\n"
        f"💕 <i>Команды работают только если у вас есть пара!</i>",
        parse_mode="HTML"
    )


def reg(dp: Dispatcher):
    dp.message.register(rp_couple_list_cmd, lambda msg: msg.text and msg.text.strip() == ".отн список")
    dp.message.register(rp_couple_cmd, lambda msg: msg.text and msg.text.startswith(".отн ") and not msg.text.strip() == ".отн список")
