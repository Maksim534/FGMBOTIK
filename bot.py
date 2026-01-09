# bot version: 2.0.0,7

import config as cfg
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


bot = Bot(token='7092521991:AAG18Ty2cie-czUSvfhQmyWo9sZmIpHtYos', default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher(storage=MemoryStorage())

