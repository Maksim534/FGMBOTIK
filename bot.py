# bot version: 2.0.0,7

import config as cfg
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import DefaultBotProperties

bot = Bot(cfg.API_TOKEN, default=DefaultBotProperties(parse_mode='HTML', link_preview_is_disabled=True))
dp = Dispatcher(bot, storage=MemoryStorage())

