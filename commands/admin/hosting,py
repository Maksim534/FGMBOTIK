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

# Цвета для индикаторов
def get_color(percent: float) -> str:
    """Возвращает цвет в зависимости от процента"""
    if percent < 50:
        return "🟢"  # Зелёный - хорошо
    elif percent < 80:
        return "🟡"  # Жёлтый - средне
    else:
        return "🔴"  # Красный - плохо

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
    """Собирает информацию о системе"""
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    cpu_freq_current = cpu_freq.current if cpu_freq else 0
    
    # RAM
    memory = psutil.virtual_memory()
    ram_used = memory.used / (1024**3)  # в GB
    ram_total = memory.total / (1024**3)
    ram_percent = memory.percent
    
    # Swap
    swap = psutil.swap_memory()
    swap_used = swap.used / (1024**3)
    swap_total = swap.total / (1024**3)
    swap_percent = swap.percent
    
    # Диск
    disk = psutil.disk_usage('/')
    disk_used = disk.used / (1024**3)
    disk_total = disk.total / (1024**3)
    disk_percent = disk.percent
    
    # Сеть
    net = psutil.net_io_counters()
    net_sent = net.bytes_sent / (1024**2)  # в MB
    net_recv = net.bytes_recv / (1024**2)
    
    # Процессы
    processes = len(psutil.pids())
    
    # Температура (не везде доступно)
    try:
        temps = psutil.sensors_temperatures()
        cpu_temp = temps.get('coretemp', [{}])[0].get('current', 0) if temps else 0
    except:
        cpu_temp = 0
    
    return {
        'cpu': {
            'percent': cpu_percent,
            'count': cpu_count,
            'freq': cpu_freq_current / 1000  # в GHz
        },
        'ram': {
            'used': round(ram_used, 2),
            'total': round(ram_total, 2),
            'percent': ram_percent
        },
        'swap': {
            'used': round(swap_used, 2),
            'total': round(swap_total, 2),
            'percent': swap_percent
        },
        'disk': {
            'used': round(disk_used, 2),
            'total': round(disk_total, 2),
            'percent': disk_percent
        },
        'net': {
            'sent': round(net_sent, 2),
            'recv': round(net_recv, 2)
        },
        'system': {
            'platform': platform.platform(),
            'python': platform.python_version(),
            'hostname': platform.node(),
            'processes': processes,
            'cpu_temp': round(cpu_temp, 1)
        }
    }

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
• Платформа: {info['system']['platform'][:30]}...
• Python: {info['system']['python']}
• Хост: {info['system']['hostname']}
• Процессов: {info['system']['processes']}
• Температура CPU: {info['system']['cpu_temp']}°C

⚙️ **ПРОЦЕССОР**
{get_status_emoji(info['cpu']['percent'])} Загрузка: {info['cpu']['percent']}%
{get_bar(info['cpu']['percent'])} 
• Ядер: {info['cpu']['count']}
• Частота: {info['cpu']['freq']} GHz

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

🌐 **СЕТЬ (с момента запуска)**
• Отправлено: {info['net']['sent']} MB
• Получено: {info['net']['recv']} MB

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
    
    # Формируем сообщение (тот же текст)
    text = f"""
📊 **СТАТУС ХОСТИНГА** 📊

⏱ **Бот запущен:** {format_uptime()}
🕐 **Время старта:** {BOT_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}

💻 **СИСТЕМА**
• Платформа: {info['system']['platform'][:30]}...
• Python: {info['system']['python']}
• Хост: {info['system']['hostname']}
• Процессов: {info['system']['processes']}
• Температура CPU: {info['system']['cpu_temp']}°C

⚙️ **ПРОЦЕССОР**
{get_status_emoji(info['cpu']['percent'])} Загрузка: {info['cpu']['percent']}%
{get_bar(info['cpu']['percent'])} 
• Ядер: {info['cpu']['count']}
• Частота: {info['cpu']['freq']} GHz

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

🌐 **СЕТЬ (с момента запуска)**
• Отправлено: {info['net']['sent']} MB
• Получено: {info['net']['recv']} MB

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
