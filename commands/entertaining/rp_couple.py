import re
import random
import time
from aiogram import types, Dispatcher
from aiogram.filters import Command

from assets.antispam import antispam
from commands.entertaining.db import get_wedlock, add_sparks, get_couple_level, LEVEL_NAMES
from commands.db import url_name, get_name
from user import BFGuser, BFGconst
from bot import bot

# Словарь для хранения времени последнего действия пары
last_action_time = {}  # ключ: "user1_user2", значение: timestamp

# RP команды для пар с привязкой к уровням
COUPLE_ACTIONS = {
    # 1 уровень - Знакомые (доступно сразу)
    1: {
        "обнять": "💞 {} нежно обнял(а) {}",
        "пожать руку": "🤝 {} пожал(а) руку {}",
        "поздороваться": "👋 {} поздоровался(ась) с {}",
        "улыбнуться": "😊 {} улыбнулся(ась) {}",
    },
    # 2 уровень - Друзья (требуется 10 искр)
    2: {
        "похвалить": "🌟 {} похвалил(а) {}",
        "рассмешить": "😂 {} рассмешил(а) {}",
        "подбодрить": "💪 {} подбодрил(а) {}",
        "поделиться": "🍫 {} поделился(ась) с {}",
    },
    # 3 уровень - Близкие (требуется 20 искр)
    3: {
        "погладить": "💖 {} погладил(а) {} по головке",
        "обнять крепко": "🤗 {} крепко обнял(а) {}",
        "шепнуть": "🤫 {} шепнул(а) {} на ушко",
        "заварить чай": "🍵 {} заварил(а) чай для {}",
    },
    # 4 уровень - Интрижка (требуется 30 искр)
    4: {
        "поцеловать": "💋 {} сладко поцеловал(а) {}",
        "прижать": "🔥 {} прижал(а) {} к себе",
        "ущипнуть": "😜 {} игриво ущипнул(а) {}",
        "прошептать": "💕 {} прошептал(а) {} нежные слова",
    },
    # 5 уровень - Отношения (требуется 40 искр)
    5: {
        "признаться": "💗 {} признался(ась) в любви {}",
        "потанцевать": "💃 {} потанцевал(а) с {}",
        "согреть": "🔥 {} согрел(а) своим теплом {}",
        "покормить": "🍜 {} покормил(а) {} с ложечки",
    },
}

# Составим регулярное выражение для поиска команд
all_actions = {}
for level_actions in COUPLE_ACTIONS.values():
    all_actions.update(level_actions)
actions_pattern = "|".join(re.escape(key) for key in all_actions.keys())
pattern = rf"^\.отн\s+({actions_pattern})$"

# Таймаут между искрами (15 минут = 900 секунд)
SPARK_COOLDOWN = 900


async def is_user_in_chat(chat_id: int, user_id: int) -> bool:
    """Проверяет, находится ли пользователь в чате"""
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False


def get_available_actions(level: int) -> dict:
    """Возвращает доступные действия для данного уровня"""
    available = {}
    for lvl, actions in COUPLE_ACTIONS.items():
        if lvl <= level:
            available.update(actions)
    return available


@antispam
async def rp_couple_cmd(message: types.Message, user: BFGuser):
    """Обработка RP-команд для пары с системой уровней и таймаутом"""
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
    
    # Получаем текущий уровень пары
    level_info = await get_couple_level(user.id, partner_id)
    current_level = level_info["level"]
    
    # Проверяем, доступно ли это действие на текущем уровне
    available_actions = get_available_actions(current_level)
    if action not in available_actions:
        # Ищем на каком уровне откроется это действие
        required_level = None
        for lvl, actions in COUPLE_ACTIONS.items():
            if action in actions:
                required_level = lvl
                break
        
        await message.answer(
            f"{user.url}, это действие откроется на {required_level} уровне! 📈\n\n"
            f"💕 Текущий уровень: {LEVEL_NAMES[current_level]}\n"
            f"🔥 Нужно искр: {required_level * 10}",
            parse_mode="HTML"
        )
        return
    
    # Проверяем таймаут между искрами
    couple_key = f"{min(user.id, partner_id)}_{max(user.id, partner_id)}"
    current_time = time.time()
    last_time = last_action_time.get(couple_key, 0)
    time_diff = current_time - last_time
    
    if time_diff < SPARK_COOLDOWN:
        minutes_left = int((SPARK_COOLDOWN - time_diff) // 60)
        seconds_left = int((SPARK_COOLDOWN - time_diff) % 60)
        await message.answer(
            f"{user.url}, ⏳ искры ещё не накопились!\n"
            f"Следующее получение через {minutes_left} мин {seconds_left} сек",
            parse_mode="HTML"
        )
        return
    
    # Получаем имена
    user_name = message.from_user.full_name
    partner_name = await get_name(partner_id)
    partner_url = await url_name(partner_id)
    
    # Случайное количество искр (1-3)
    sparks_earned = random.randint(1, 3)
    
    # Добавляем искры паре
    level_data = await add_sparks(user.id, partner_id, sparks_earned)
    total_sparks = level_data["total"]
    new_level = level_data["level"]
    
    # Обновляем время последнего действия
    last_action_time[couple_key] = current_time
    
    # Получаем название уровня
    level_name = LEVEL_NAMES[new_level]
    
    # Формируем текст действия
    action_text = available_actions[action].format(
        f"<a href='tg://user?id={user.id}'>{user_name}</a>",
        partner_url
    )
    
    # Проверяем, есть ли партнёр в этом чате
    partner_in_chat = await is_user_in_chat(message.chat.id, partner_id)
    
    if partner_in_chat:
        # Если партнёр в чате - отправляем сообщение с искрами
        next_level = new_level + 1 if new_level < 5 else 5
        next_required = next_level * 10 if new_level < 5 else 0
        sparks_to_next = next_required - total_sparks if new_level < 5 else 0
        
        # Сообщаем, повысился ли уровень
        level_up_text = ""
        if new_level > current_level:
            level_up_text = f"\n🎉 <b>УРОВЕНЬ ПОВЫШЕН!</b> 🎉\n"
            # Показываем новые доступные действия
            new_actions = list(COUPLE_ACTIONS[new_level].keys())
            level_up_text += f"✨ Новые действия: {', '.join(new_actions)}\n"
        
        response = f"💞 <b>Романтический момент</b> 💞\n\n"
        response += f"{action_text}\n\n"
        response += f"✨ <b>+{sparks_earned} искр</b> к вашим отношениям!\n"
        response += level_up_text
        response += f"📊 <b>Уровень:</b> {level_name}\n"
        response += f"🔥 <b>Всего искр:</b> {total_sparks}\n"
        
        if new_level < 5:
            response += f"➡️ <b>До следующего уровня:</b> {sparks_to_next} искр"
        else:
            response += f"🏆 <b>Максимальный уровень!</b>"
        
        await message.answer(response, parse_mode="HTML")
    else:
        # Если партнёра нет в чате
        await message.answer(
            f"{user.url}, вашей половинки нет в этом чате! 😢\n\n"
            f"💭 Пригласи {partner_name} в этот чат, чтобы проявлять свои чувства!",
            parse_mode="HTML"
        )


@antispam
async def rp_couple_list_cmd(message: types.Message, user: BFGuser):
    """Показывает список доступных RP-команд по уровням"""
    win, lose = BFGconst.emj()
    
    # Проверяем, есть ли пара
    couple_data = await get_wedlock(user.id)
    if not couple_data:
        await message.answer(
            f"{user.url}, у вас нет пары! Сначала найдите свою половинку через 💍 <b>свадьбу</b>",
            parse_mode="HTML"
        )
        return
    
    partner_id = couple_data[0] if couple_data[1] == user.id else couple_data[1]
    level_info = await get_couple_level(user.id, partner_id)
    current_level = level_info["level"]
    total_sparks = level_info["total_sparks"]
    
    response = f"{user.url}, <b>доступные RP-команды</b> 💕\n\n"
    response += f"📊 <b>Ваш уровень:</b> {LEVEL_NAMES[current_level]}\n"
    response += f"🔥 <b>Всего искр:</b> {total_sparks}\n\n"
    response += f"━━━━━━━━━━━━━━━━━━━━\n"
    
    for level, actions in COUPLE_ACTIONS.items():
        if level <= current_level:
            status = "✅"
        else:
            status = "🔒"
            required = level * 10
        
        response += f"{status} <b>{LEVEL_NAMES[level]}</b>"
        if level > current_level:
            response += f" (нужно {required} искр)"
        response += "\n"
        
        for action in actions.keys():
            if level <= current_level:
                response += f"  • <code>.отн {action}</code>\n"
        response += "\n"
    
    response += f"━━━━━━━━━━━━━━━━━━━━\n"
    response += f"⏳ <i>Искры можно получать раз в 15 минут</i>\n"
    response += f"💡 <i>Пример: .отн обнять</i>"
    
    await message.answer(response, parse_mode="HTML")


@antispam
async def my_couple_level_cmd(message: types.Message, user: BFGuser):
    """Показывает уровень отношений пары"""
    win, lose = BFGconst.emj()
    
    couple_data = await get_wedlock(user.id)
    if not couple_data:
        await message.answer(
            f"{user.url}, у вас нет пары! Сначала найдите свою половинку через 💍 <b>свадьбу</b>",
            parse_mode="HTML"
        )
        return
    
    partner_id = couple_data[0] if couple_data[1] == user.id else couple_data[1]
    
    level_info = await get_couple_level(user.id, partner_id)
    current_level = level_info["level"]
    total_sparks = level_info["total_sparks"]
    level_name = LEVEL_NAMES[current_level]
    
    # Информация о следующем уровне
    next_level = current_level + 1 if current_level < 5 else 5
    next_required = next_level * 10 if current_level < 5 else 0
    sparks_to_next = next_required - total_sparks if current_level < 5 else 0
    
    # Создаём визуальную шкалу прогресса
    if current_level < 5:
        level_start = (current_level - 1) * 10
        level_end = current_level * 10
        progress_in_level = total_sparks - level_start
        level_progress = int((progress_in_level / 10) * 10)
        progress_bar = "🟩" * level_progress + "⬜" * (10 - level_progress)
    else:
        progress_bar = "🟩" * 10
    
    partner_name = await get_name(partner_id)
    partner_url = await url_name(partner_id)
    
    # Список доступных действий на текущем уровне
    available_actions = list(get_available_actions(current_level).keys())
    actions_sample = ", ".join(available_actions[:5])
    if len(available_actions) > 5:
        actions_sample += f" и ещё {len(available_actions) - 5}"
    
    response = f"{user.url}, <b>уровень ваших отношений</b> 💕\n\n"
    response += f"👤 Вы: {user.url}\n"
    response += f"👤 Партнёр: {partner_url}\n\n"
    response += f"━━━━━━━━━━━━━━━━━━━━\n"
    response += f"📊 <b>Текущий уровень:</b> {level_name}\n"
    response += f"🔥 <b>Всего искр:</b> {total_sparks}\n"
    response += f"📈 <b>Прогресс:</b> {progress_bar}\n"
    
    if current_level < 5:
        response += f"➡️ <b>До {LEVEL_NAMES[next_level]}:</b> {sparks_to_next} искр\n"
    else:
        response += f"🏆 <b>Максимальный уровень!</b>\n"
    
    response += f"━━━━━━━━━━━━━━━━━━━━\n"
    response += f"💬 <b>Доступные действия:</b>\n"
    response += f"{actions_sample}\n\n"
    response += f"⏳ <i>Искры можно получать раз в 15 минут</i>"
    
    await message.answer(response, parse_mode="HTML")


def reg(dp: Dispatcher):
    dp.message.register(rp_couple_list_cmd, lambda msg: msg.text and msg.text.strip() == ".отн список")
    dp.message.register(rp_couple_cmd, lambda msg: msg.text and msg.text.startswith(".отн ") and not msg.text.strip() == ".отн список")
    dp.message.register(my_couple_level_cmd, lambda msg: msg.text and msg.text.strip() == ".мой уровень")
