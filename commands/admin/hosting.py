import psutil
import platform
import time
from datetime import datetime, timedelta
from aiogram import types, Dispatcher, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import bot
from assets.antispam import antispam, admin_only
from assets.transform import transform_int as tr
from user import BFGuser
from filters.custom import StartsWith

# Время запуска бота
BOT_START_TIME = datetime.now()

def get_color(percent: float) -> str:
    """Возвращает цвет в зависимости от процента"""
    if percent < 50:
        return "🟢"
    elif percent < 80:
        return "🟡"
    else:
        return "🔴"

def get_bar(percent: float, length: int = 10) -> str:
    """Создаёт визуальную полосу загрузки"""
    filled = int(percent / 100 * length)
    empty = length - filled
    return "█" * filled + "░" * empty

def format_uptime() -> str:
    """Форматирует время работы бота"""
    uptime = datetime.now() - BOT_START_TIME
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} дн.")
    if hours > 0:
        parts.append(f"{hours} ч.")
    if minutes > 0:
        parts.append(f"{minutes} мин.")
    parts.append(f"{seconds} сек.")
    
    return " ".join(parts)

def get_system_info() -> dict:
    """Собирает информацию о системе с обработкой ошибок"""
    info = {
        'cpu': {'percent': 0, 'count': 0},
        'ram': {'used': 0, 'total': 0, 'percent': 0},
        'swap': {'used': 0, 'total': 0, 'percent': 0},
        'disk': {'used': 0, 'total': 0, 'percent': 0},
        'system': {
            'platform': 'Неизвестно',
            'python': platform.python_version(),
            'hostname': 'Неизвестно',
            'processes': 0
        }
    }
    
    try:
        # CPU (без частоты, так как она вызывает ошибку на FreeBSD)
        info['cpu']['percent'] = psutil.cpu_percent(interval=0.5)
        info['cpu']['count'] = psutil.cpu_count()
    except Exception as e:
        print(f"Ошибка получения CPU: {e}")
    
    try:
        # RAM
        memory = psutil.virtual_memory()
        info['ram']['used'] = round(memory.used / (1024**3), 2)
        info['ram']['total'] = round(memory.total / (1024**3), 2)
        info['ram']['percent'] = memory.percent
    except Exception as e:
        print(f"Ошибка получения RAM: {e}")
    
    try:
        # Swap
        swap = psutil.swap_memory()
        info['swap']['used'] = round(swap.used / (1024**3), 2)
        info['swap']['total'] = round(swap.total / (1024**3), 2)
        info['swap']['percent'] = swap.percent
    except Exception as e:
        print(f"Ошибка получения Swap: {e}")
    
    try:
        # Диск
        disk = psutil.disk_usage('/')
        info['disk']['used'] = round(disk.used / (1024**3), 2)
        info['disk']['total'] = round(disk.total / (1024**3), 2)
        info['disk']['percent'] = disk.percent
    except Exception as e:
        print(f"Ошибка получения диска: {e}")
    
    try:
        # Системная информация
        info['system']['platform'] = platform.platform()
        info['system']['hostname'] = platform.node()
        info['system']['processes'] = len(psutil.pids())
    except Exception as e:
        print(f"Ошибка получения системной информации: {e}")
    
    return info

def get_status_emoji(percent: float) -> str:
    """Возвращает эмодзи статуса"""
    if percent < 50:
        return "✅"
    elif percent < 80:
        return "⚠️"
    else:
        return "🚨"

@antispam
@admin_only(private=True)
async def hosting_status_cmd(message: types.Message, user: BFGuser):
    """Команда для просмотра состояния хостинга"""
    info = get_system_info()
    
    # Создаём клавиатуру с кнопкой обновления
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(
        text="🔄 Обновить",
        callback_data="hosting_refresh"
    ))
    
    # Формируем сообщение
    text = f"""
📊 **СТАТУС ХОСТИНГА** 📊

⏱ **Бот запущен:** {format_uptime()}
🕐 **Время старта:** {BOT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}

💻 **СИСТЕМА**
• Платформа: {info['system']['platform'][:50]}...
• Python: {info['system']['python']}
• Хост: {info['system']['hostname']}
• Процессов: {info['system']['processes']}

⚙️ **ПРОЦЕССОР**
{get_status_emoji(info['cpu']['percent'])} Загрузка: {info['cpu']['percent']}%
{get_bar(info['cpu']['percent'])} 
• Ядер: {info['cpu']['count']}

🧠 **ОПЕРАТИВНАЯ ПАМЯТЬ**
{get_status_emoji(info['ram']['percent'])} Использовано: {info['ram']['used']} GB / {info['ram']['total']} GB
{get_bar(info['ram']['percent'])} 
• {info['ram']['percent']}%

💾 **SWAP (Файл подкачки)**
{get_status_emoji(info['swap']['percent'])} Использовано: {info['swap']['used']} GB / {info['swap']['total']} GB
{get_bar(info['swap']['percent'])} 
• {info['swap']['percent']}%

📀 **ДИСК**
{get_status_emoji(info['disk']['percent'])} Использовано: {info['disk']['used']} GB / {info['disk']['total']} GB
{get_bar(info['disk']['percent'])} 
• {info['disk']['percent']}%

📊 **Сводка:**
• CPU: {info['cpu']['percent']}% {get_color(info['cpu']['percent'])}
• RAM: {info['ram']['percent']}% {get_color(info['ram']['percent'])}
• DISK: {info['disk']['percent']}% {get_color(info['disk']['percent'])}
"""

    await message.answer(text, reply_markup=keyboard.as_markup())

@antispam
@admin_only(private=True)
async def hosting_refresh_callback(call: types.CallbackQuery, user: BFGuser):
    """Обновление статуса хостинга"""
    info = get_system_info()
    
    # Обновляем клавиатуру
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(
        text="🔄 Обновить",
        callback_data="hosting_refresh"
    ))
    
    text = f"""
📊 **СТАТУС ХОСТИНГА** 📊

⏱ **Бот запущен:** {format_uptime()}
🕐 **Время старта:** {BOT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}

💻 **СИСТЕМА**
• Платформа: {info['system']['platform'][:50]}...
• Python: {info['system']['python']}
• Хост: {info['system']['hostname']}
• Процессов: {info['system']['processes']}

⚙️ **ПРОЦЕССОР**
{get_status_emoji(info['cpu']['percent'])} Загрузка: {info['cpu']['percent']}%
{get_bar(info['cpu']['percent'])} 
• Ядер: {info['cpu']['count']}

🧠 **ОПЕРАТИВНАЯ ПАМЯТЬ**
{get_status_emoji(info['ram']['percent'])} Использовано: {info['ram']['used']} GB / {info['ram']['total']} GB
{get_bar(info['ram']['percent'])} 
• {info['ram']['percent']}%

💾 **SWAP (Файл подкачки)**
{get_status_emoji(info['swap']['percent'])} Использовано: {info['swap']['used']} GB / {info['swap']['total']} GB
{get_bar(info['swap']['percent'])} 
• {info['swap']['percent']}%

📀 **ДИСК**
{get_status_emoji(info['disk']['percent'])} Использовано: {info['disk']['used']} GB / {info['disk']['total']} GB
{get_bar(info['disk']['percent'])} 
• {info['disk']['percent']}%

📊 **Сводка:**
• CPU: {info['cpu']['percent']}% {get_color(info['cpu']['percent'])}
• RAM: {info['ram']['percent']}% {get_color(info['ram']['percent'])}
• DISK: {info['disk']['percent']}% {get_color(info['disk']['percent'])}
"""

    await call.message.edit_text(text, reply_markup=keyboard.as_markup())
    await call.answer()

@antispam
async def hosting_status_user_cmd(message: types.Message, user: BFGuser):
    """Упрощённая версия для обычных пользователей"""
    info = get_system_info()
    uptime = format_uptime()
    
    text = f"""
📊 **СТАТУС БОТА** 📊

⏱ **Работает:** {uptime}
🕐 **Старт:** {BOT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}

⚙️ **Загрузка:**
• CPU: {info['cpu']['percent']}% {get_color(info['cpu']['percent'])}
• RAM: {info['ram']['percent']}% {get_color(info['ram']['percent'])}
• DISK: {info['disk']['percent']}% {get_color(info['disk']['percent'])}
"""
    await message.answer(text)

# ==================== РЕГИСТРАЦИЯ ====================
def reg(dp: Dispatcher):
    """Регистрация обработчиков"""
    # Для админов
    dp.message.register(hosting_status_cmd, StartsWith('/hosting'))
    dp.message.register(hosting_status_cmd, StartsWith('/хостинг'))
    
    # Для всех (упрощённая версия)
    dp.message.register(hosting_status_user_cmd, StartsWith('/status'))
    dp.message.register(hosting_status_user_cmd, StartsWith('/статус'))
    
    # Колбэк для обновления
    dp.callback_query.register(hosting_refresh_callback, F.data == 'hosting_refresh')

# ==================== ОПИСАНИЕ МОДУЛЯ ====================
