import asyncio
from commands.db import cursor, conn

async def auto_fuel():
    """Уменьшение топлива у всех машин каждые 10 минут"""
    while True:
        try:
            cursor.execute("UPDATE property SET fuel = max(0, fuel - 1) WHERE car > 0 AND fuel > 0")
            conn.commit()# 10 минут

# Запуск в основном файле
async def start_auto_fuel():
    asyncio.create_task(auto_fuel())
