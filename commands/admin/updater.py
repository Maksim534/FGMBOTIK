import subprocess
import tempfile
import requests
import shutil
import time
import sys
import os

from aiogram.types import FSInputFile

from assets.antispam import admin_only
from assets import keyboards as kb
from utils.settings import get_setting, update_setting
from filters.custom import TextIn, StartsWith
from aiogram import types, Dispatcher
import config as cfg
from bot import bot, dp
import asyncio


@admin_only()
async def restart_bot(message: types.Message):
	msg = await message.answer("<i>🔄 Перезагрузка бота...</i>")

	update_setting(key="restart_flag", value={"time": time.time(), "chat_id": msg.chat.id, "message_id": msg.message_id})

	await asyncio.sleep(2)

	try:
		await bot.close()
	except Exception as e:
		await message.answer(f"‼️ Не удалось закрыть соединение с сервером: <code>{e}</code>")

	await dp.storage.close()
	
	os.execl(sys.executable, sys.executable, *sys.argv)


def reg(dp: Dispatcher):
	dp.message.register(restart_bot, TextIn("🔄 Перезагрузка", "/restartb"))
