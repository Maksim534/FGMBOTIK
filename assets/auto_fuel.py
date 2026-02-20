
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from commands.db import cursor, conn

# Создаём планировщик (или используем существующий из auto.py)
scheduler = AsyncIOScheduler()

def auto_fuel():
    """Уменьшение топлива у всех машин (синхронная функция)"""
    try:
        cursor.execute("UPDATE property SET fuel = max(0, fuel - 1) WHERE car > 0 AND fuel > 0")
        conn.commit()
    except Exception:
        pass

def start_auto_fuel():
    """Запуск задачи в планировщике (синхронная функция)"""
    scheduler.add_job(auto_fuel, 'interval', minutes=10)
