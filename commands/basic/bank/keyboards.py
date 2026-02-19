from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from urllib.parse import quote
import config as cfg

def bank_actions_kb(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для банковских операций с упоминанием бота"""
    builder = InlineKeyboardBuilder()
    
    # Кодируем команды для URL
    base_url = f"https://t.me/{cfg.bot_username}?start="
    
    # Команда для пополнения
    put_cmd = quote("банк положить ")
    put_url = base_url + put_cmd
    
    # Команда для снятия
    take_cmd = quote("банк снять ")
    take_url = base_url + take_cmd
    
    # Команда для депозита (положить)
    dep_put_cmd = quote("депозит положить ")
    dep_put_url = base_url + dep_put_cmd
    
    # Команда для депозита (снять)
    dep_take_cmd = quote("депозит снять ")
    dep_take_url = base_url + dep_take_cmd
    
    builder.row(InlineKeyboardButton(
        text="💰 Положить в банк", 
        url=put_url
    ))
    
    builder.row(InlineKeyboardButton(
        text="💸 Снять с банка", 
        url=take_url
    ))
    
    builder.row(InlineKeyboardButton(
        text="📈 Депозит положить", 
        url=dep_put_url
    ))
    
    builder.row(InlineKeyboardButton(
        text="📉 Депозит снять", 
        url=dep_take_url
    ))
    
    return builder.as_markup()
