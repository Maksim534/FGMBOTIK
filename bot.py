# bot version: 2.0.0,7

import config as cfg
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from telegram.ext import Updater, DefaultBotProperties


bot = Bot(token='YOUR_BOT_TOKEN', default=DefaultBotProperties(parse_mode='HTML'))
updater = Updater(bot=bot, use_context=True)

