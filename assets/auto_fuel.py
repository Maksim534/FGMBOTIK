from commands.db import cursor, conn

def auto_fuel():
    """Уменьшение топлива у всех машин"""
    try:
        cursor.execute("UPDATE property SET fuel = max(0, fuel - 1) WHERE car > 0 AND fuel > 0")
        conn.commit()
    except Exception:
        pass
