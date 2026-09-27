from commands.db import conn, cursor
from datetime import datetime
import time
from commands.db import conn, cursor


async def get_wedlock(user_id: int) -> tuple:
    return cursor.execute('SELECT * FROM wedlock WHERE user1 = ? OR user2 = ?', (user_id, user_id)).fetchone()


async def get_new_wedlock(user_id: int, rid: int) -> str:
    if cursor.execute('SELECT * FROM wedlock WHERE user1 = ? OR user2 = ?', (user_id, user_id)).fetchone():
        return 'u_not'
    if cursor.execute('SELECT * FROM wedlock WHERE user1 = ? OR user2 = ?', (rid, rid)).fetchone():
        return 'r_not'


async def new_wedlock(user_id: int, rid: int) -> bool:
    data1 = cursor.execute('SELECT * FROM wedlock WHERE user1 = ? OR user2 = ?', (user_id, user_id)).fetchone()
    data2 = cursor.execute('SELECT * FROM wedlock WHERE user1 = ? OR user2 = ?', (rid, rid)).fetchone()
    if data1 or data2:
        return True

    cursor.execute('INSERT INTO wedlock (user1, user2, rtime) VALUES (?, ?, ?)', (user_id, rid, datetime.now().timestamp()))
    conn.commit()


async def divorce_db(user_id: int) -> None:
    cursor.execute('DELETE FROM wedlock WHERE user1 = ? OR user2 = ?', (user_id, user_id))
    conn.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS couple_levels (
    couple_id TEXT PRIMARY KEY,  -- составной ключ вида "user1_user2" (меньший ID первым)
    level INTEGER DEFAULT 1,
    sparks INTEGER DEFAULT 0,
    total_sparks INTEGER DEFAULT 0,
    last_action INTEGER
)''')
conn.commit()

# Названия уровней
LEVEL_NAMES = {
    1: "👋 Знакомые",
    2: "🤝 Друзья", 
    3: "💕 Близкие",
    4: "🔥 Интрижка",
    5: "💞 Отношения"
}

async def get_couple_key(user1: int, user2: int) -> str:
    """Создаёт ключ для пары (меньший ID первым)"""
    return f"{min(user1, user2)}_{max(user1, user2)}"

async def get_couple_level(user1: int, user2: int) -> dict:
    """Получает уровень пары"""
    couple_key = await get_couple_key(user1, user2)
    data = cursor.execute(
        "SELECT level, sparks, total_sparks FROM couple_levels WHERE couple_id = ?",
        (couple_key,)
    ).fetchone()
    
    if not data:
        return {"level": 1, "sparks": 0, "total_sparks": 0}
    
    return {"level": data[0], "sparks": data[1], "total_sparks": data[2]}

async def add_sparks(user1: int, user2: int, amount: int = 1) -> dict:
    """Добавляет искры паре и обновляет уровень"""
    couple_key = await get_couple_key(user1, user2)
    
    # Проверяем, существует ли запись
    existing = cursor.execute(
        "SELECT level, sparks, total_sparks FROM couple_levels WHERE couple_id = ?",
        (couple_key,)
    ).fetchone()
    
    current_time = int(time.time())
    
    if existing:
        level, sparks, total_sparks = existing
        new_sparks = sparks + amount
        new_total = total_sparks + amount
        
        # Определяем новый уровень (каждые 10 искр)
        new_level = level
        if new_total >= 40 and level < 5:
            new_level = 5
        elif new_total >= 30 and level < 4:
            new_level = 4
        elif new_total >= 20 and level < 3:
            new_level = 3
        elif new_total >= 10 and level < 2:
            new_level = 2
        
        cursor.execute('''UPDATE couple_levels 
            SET sparks = ?, level = ?, total_sparks = ?, last_action = ?
            WHERE couple_id = ?''',
            (new_sparks, new_level, new_total, current_time, couple_key))
    else:
        new_level = 1
        if amount >= 10:
            new_level = 2
        elif amount >= 20:
            new_level = 3
        elif amount >= 30:
            new_level = 4
        elif amount >= 40:
            new_level = 5
        
        cursor.execute('''INSERT INTO couple_levels 
            (couple_id, level, sparks, total_sparks, last_action)
            VALUES (?, ?, ?, ?, ?)''',
            (couple_key, new_level, amount, amount, current_time))
    
    conn.commit()
    
    return {
        "level": new_level,
        "sparks": amount,
        "total": new_total if existing else amount
    }
    
