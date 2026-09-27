import random
import re

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Dispatcher, types
from assets.antispam import antispam
from commands.db import get_colvo_users, setname
from assets.gettime import lucktime
from assets.transform import transform_int as tr
import config as cfg
from filters.custom import StartsWith, TextIn
from user import BFGuser, BFGconst


@antispam
async def shar_cmd(message: types.Message, user: BFGuser):
    list = ["Мой ответ - нет", "Мне кажется - да", "Сейчас нельзя предсказать", "Мне кажется - нет",
            "Знаки говорят - нет", "Да", "Нет", "Можешь быть уверен в этом"]
    await message.answer(random.choice(list))


@antispam
async def vibor_cmd(message: types.Message, user: BFGuser):
    list = ["Первый варинат лучше", "Однозначно первый", "Второй варинат лучше", "Однозначно второй"]
    await message.answer(random.choice(list))


@antispam
async def shans_cmd(message: types.Message, user: BFGuser):
    await message.answer(f'Шанс этого - {random.randint(1, 100)}%')


@antispam
async def set_name_cmd(message: types.Message, user: BFGuser):
    user_id = message.from_user.id
    win, lose = BFGconst.emj()
    
    try:
        name = " ".join(message.text.split()[2:])
    except:
        await message.answer(f'{user.url}, ваш ник не может быть короче 5 символов {lose}')
        return

    climit = {0: 20, 1: 25, 2: 30, 3: 45, 4: 50}.get(user.status, 20)

    if re.search(r'<|>|@|t\.me|http', name):
        await message.answer(f'{user.url}, ваш ник содержит запрещённые символы {lose}')
        return

    if len(name) < 5:
        await message.answer(f'{user.url}, ваш ник не может быть короче 5 символов {lose}')
        return

    if len(name) > climit:
        await message.answer(f'{user.url}, ваш ник не может быть длиннее {climit} символов {lose}')
        return

    await setname(name, user_id)
    await message.answer(f'Ваш ник изменён на «{name}»')



@antispam
async def stats_cmd(message: types.Message, user: BFGuser):
    users, chats, uchats = await get_colvo_users()

    await message.answer(f'''📊 Кол-во пользователей бота: {tr(users)}
📊 Общее кол-во чатов: {tr(chats)}
📊 Общее кол-во игроков в беседах: {tr(uchats)}''')


@antispam
async def chat_list(message: types.Message, user: BFGuser):
    await message.answer(f'''💭 Официальная беседа бота: {cfg.chat}
💭 Официальный канал разработки: {cfg.channel}
🏆 Официальный чат с розыгрышами: ...''', disable_web_page_preview=True)


@antispam
async def my_name(message: types.Message, user: BFGuser):
    await message.answer(f'🗂 Ваш ник - «{user.name}»')


def reg(dp: Dispatcher):
    dp.message.register(shar_cmd, StartsWith("шар "))
    dp.message.register(vibor_cmd, StartsWith("выбери "))
    dp.message.register(shans_cmd, StartsWith("шанс "))
    dp.message.register(set_name_cmd, StartsWith("сменить ник"))
    dp.message.register(stats_cmd, TextIn("статистика бота"))
    dp.message.register(my_name, TextIn("мой ник"))
    dp.message.register(chat_list, TextIn("!беседа"))
