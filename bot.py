# bot version: 3.0.0,3
from aiogram import Bot, Dispatcher

import config as cfg


bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
