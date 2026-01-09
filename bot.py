# bot version: 3.0.0,3
from aiogram import Bot, Dispatcher

import config as cfg


bot = Bot(token=cfg.API_TOKEN, (parse_mode='html', link_preview_is_disabled=True))
dp = Dispatcher(storage=MemoryStorage())
