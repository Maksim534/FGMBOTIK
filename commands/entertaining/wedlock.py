from aiogram import Dispatcher, types

from assets.antispam import antispam
from commands.db import url_name, get_name
from commands.entertaining.db import *
from bot import bot
from assets import keyboards as kb
from filters.custom import TextIn, StartsWith
from user import BFGuser, BFGconst
from assets.gettime import get_ptime


@antispam
async def my_wedlock(message: types.message, user: BFGuser):
    data = await get_wedlock(user.id)
    win, lose = BFGconst.emj()
    
    if not data:
        await message.answer(f'{user.url}, к сожалению вы не состоите в браке {lose}')
        return

    name1 = await get_name(data[0])
    name2 = await get_name(data[1])
    partner_id = data[0] if data[1] == user.id else data[1]

    name1 = f'<a href="tg://openmessage?user_id={data[0]}">{name1}</a>'
    name2 = f'<a href="tg://openmessage?user_id={data[1]}">{name2}</a>'

    dt = datetime.fromtimestamp(data[2]).strftime('%d.%m.%y в %H:%M:%S')
    dt_delta = get_ptime(data[2])
    
    # Получаем информацию об уровне отношений
    level_info = await get_couple_level(user.id, partner_id)
    current_level = level_info["level"]
    total_sparks = level_info["total_sparks"]
    level_name = LEVEL_NAMES[current_level]
    
    # Информация о следующем уровне
    next_level = current_level + 1 if current_level < 5 else 5
    sparks_to_next = (next_level * 10) - total_sparks if current_level < 5 else 0
    
    # Прогресс-бар
    if current_level < 5:
        progress = int((total_sparks - (current_level - 1) * 10) / 10 * 10)
        progress_bar = "🟩" * progress + "⬜" * (10 - progress)
    else:
        progress_bar = "🟩" * 10

    response = f"""💍 <b>Ваш брак</b> 💍

{name1} 💞 {name2}

🗓 Зарегистрирован: {dt}
👩‍❤️‍👨 Существует: {dt_delta}

📊 <b>Уровень отношений:</b> {level_name}
🔥 <b>Всего искр:</b> {total_sparks}
📈 <b>Прогресс:</b> {progress_bar}
"""

    if current_level < 5:
        response += f"➡️ <b>До {LEVEL_NAMES[next_level]}:</b> {sparks_to_next} искр\n"
    else:
        response += f"🏆 <b>Максимальный уровень!</b>\n"
    
    response += f"""
💬 <b>RP-команды для пары:</b>

<code>.отн список</code> — все доступные действия
<code>.мой уровень</code> — детальная статистика
<code>.отн [действие]</code> — проявить чувства

💡 <i>Как улучшать отношения?</i>
• Используйте RP-команды в общих чатах
• Каждое действие даёт 1-3 🔥 искры
• Искры можно получать раз в 15 минут
• Собирайте искры и открывайте новые действия!

✨ <b>Доступно на {level_name}:</b> {', '.join(list(get_available_actions(current_level).keys())[:5])}..."""

    await message.answer(response, parse_mode="HTML")

@antispam
async def wedlock(message: types.message, user: BFGuser):
	win, lose = BFGconst.emj()

	try:
		r_id = message.reply_to_message.from_user.id
		rname = await url_name(r_id)
	except:
		await message.answer(f'{user.url}, вы не ответили на сообщение партнёра на котором вы хотите пожениться {lose}')
		return

	if user.id == r_id:
		await message.answer(f'{user.url}, к сожалению вы не можете жениться на самому себе {lose}')
		return

	res = await get_new_wedlock(user.id, r_id)

	if res == 'u_not':
		await message.answer(f'{user.url}, вы уже находитесь в браке {lose}')
	elif res == 'r_not':
		await message.answer(f'{user.url}, ваш партнёр уже находиться в браке {lose}')
	else:
		await message.answer(f'''💍 {rname}, минуту внимания!
💓 {user.url} сделал вам предложение руки и сердца.
😍 Принять решение можно кнопками внизу.''', reply_markup=kb.wedlock(user.id, r_id))


async def wedlock_call(call: types.CallbackQuery):
	data = call.data.split('-')[1].split('|')
	action, r_id, u_id = data[0], int(data[1]), int(data[2])
	user_id = call.from_user.id

	if action == 'false' and user_id == u_id:
		try:
			await call.message.delete()
		except:
			...
		return

	if user_id != r_id:
		await bot.answer_callback_query(call.id, text='⚠️ Вы не можете нажать эту кнопку.')
		return

	try:
		await call.message.delete()
	except:
		return

	name1 = await url_name(u_id)
	name2 = await url_name(r_id)

	if action != 'true':
		await call.message.answer(f'💔 {name1}, cожалеем, но {name2} отклонил ваше предложение о бракосочетании.')
		return

	if (await new_wedlock(u_id, r_id)):
		return
	
	await call.message.answer(f'''💍 Вы успешно приняли предложение о браке
👰👨‍⚖ С сегодняшнего дня {name1} и {name2} состоят в браке!
Поздравим молодоженов 🎉''')


@antispam
async def divorce(message: types.message, user: BFGuser):
	data = await get_wedlock(user.id)
	win, lose = BFGconst.emj()
	
	if not data:
		await message.answer(f'{user.url}, к сожалению вы не женаты {lose}')
		return

	await message.answer(f'📝 Убедитесь что вы согласны разводится.\nЧтобы развестись, нажмите на кнопку ниже', reply_markup=kb.divorce(user.id))


async def divorce_call(call: types.CallbackQuery):
	action = call.data.split('-')[1].split('|')[0]
	uid = int(call.data.split('|')[1])
	user_id = call.from_user.id

	if user_id != uid:
		await bot.answer_callback_query(call.id, text='⚠️ Вы не можете нажать эту кнопку.')
		return

	name = await url_name(user_id)
	data = await get_wedlock(user_id)

	if not data:
		return

	try:
		await call.message.delete()
	except:
		return

	if action == 'true':
		await divorce_db(uid)
		dt_delta = get_ptime(data[2])
		name1 = await url_name(data[0])
		name2 = await url_name(data[1])
		await call.message.answer(f'💔 Брак между {name1} и {name2} расторгнут.\nОн просуществовал {dt_delta}')
	else:
		await call.message.answer(f'{name}, вы успешно отказались от развода 😎')


def reg(dp: Dispatcher):
	dp.message.register(my_wedlock, TextIn("мой брак"))

	dp.message.register(wedlock, TextIn("свадьба"))
	dp.callback_query.register(wedlock_call, StartsWith("wedlock-"))

	dp.message.register(divorce, TextIn("развод"))
	dp.callback_query.register(divorce_call, StartsWith("divorce-"))
