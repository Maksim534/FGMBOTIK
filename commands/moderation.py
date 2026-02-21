from aiogram import types, Dispatcher, F
from aiogram.types import ChatPermissions

from datetime import timedelta
from assets.antispam import antispam, moderation
from commands.db import chek_user
from assets.gettime import get_ptime
from bot import bot
from user import BFGuser
import time
import re

print("🔥 МОДУЛЬ MODERATION ЗАГРУЖЕН!")

time_units = {"д": 86400, "d": 86400, "ч": 3600, "h": 3600, "м": 60, "m": 60}

MutePermissions = ChatPermissions(
	can_send_messages=False,
	can_send_audios=False,
	can_send_documents=False,
	can_send_photos=False,
	can_send_videos=False,
	can_send_video_notes=False,
	can_send_voice_notes=False,
	can_send_other_messages=False
)

UnMutePermissions = ChatPermissions(
	can_send_messages=True,
	can_send_audios=True,
	can_send_documents=True,
	can_send_photos=True,
	can_send_videos=True,
	can_send_video_notes=True,
	can_send_voice_notes=True,
	can_send_other_messages=True
)


async def get_ruser(message: types.Message) -> str:
	user_id = message.reply_to_message.from_user.id
	user = await chek_user(user_id)
	if not user:
		rname = message.from_user.full_name.replace('<', '').replace('>', '').replace('@', '').replace('t.me', '')
		return f'<a href="tg://user?id={user_id}">{rname}</a>'
	return f'<a href="tg://user?id={user_id}">{user[0]}</a>'


@antispam  # можно пока убрать, если мешает
async def mute_cmd(message: types.Message, user: BFGuser):
    print(f"🔥 mute_cmd вызвана! Текст: '{message.text}'")
    await message.answer("Команда сработала!")

@antispam
@moderation
async def unmute_cmd(message: types.Message, user: BFGuser):
	chat_id = message.chat.id

	if not message.reply_to_message:
		await message.reply('Вы должны ответить на сообщение пользователя.')
		return
	
	rid = message.reply_to_message.from_user.id
	rname = await get_ruser(message)
	
	await bot.restrict_chat_member(chat_id, rid, permissions=UnMutePermissions)
	await message.answer(f'Администратор {user.url}, снял мут {rname}.')


@antispam
@moderation
async def ban_cmd(message: types.Message, user: BFGuser):
	chat_id = message.chat.id
	
	if not message.reply_to_message:
		await message.reply('Вы должны ответить на сообщение пользователя.')
		return
	
	try:
		pattern = r"(\d+)\s*([a-zа-я]+)"
		match = re.search(pattern, message.text.lower())
		amount, unit = match.groups()
		amount = int(amount)
		unit = unit[0]
		ban_time_s = int(amount * time_units[unit])
		ban_time = timedelta(seconds=ban_time_s)
	except:
		ban_time = None
	
	rid = message.reply_to_message.from_user.id
	rname = await get_ruser(message)
	
	await bot.ban_chat_member(chat_id, rid, until_date=ban_time)
	txt = get_ptime(int(time.time() - ban_time_s)) if ban_time else 'всегда'
	await message.answer(f'Администратор {user.url}, выдал бан на {txt} {rname}.')


@antispam
@moderation
async def unban_cmd(message: types.Message, user: BFGuser):
	chat_id = message.chat.id
	
	if not message.reply_to_message:
		await message.reply('Вы должны ответить на сообщение пользователя.')
		return
	
	rid = message.reply_to_message.from_user.id
	rname = await get_ruser(message)
	
	await bot.unban_chat_member(chat_id, rid, only_if_banned=True)
	await message.answer(f'Администратор {user.url}, снял бан {rname}.')


def reg(dp: Dispatcher):
	print("🔥 reg() ВЫЗВАНА для moderation.py")
	dp.message.register(mute_cmd, lambda msg: True)
	dp.message.register(unmute_cmd, F.text.startswith(("unmute", "размут", "говори")))
	dp.message.register(ban_cmd, F.text.startswith(("ban", "бан",)))
	dp.message.register(unban_cmd, F.text.startswith(("unban", "разбан")))
