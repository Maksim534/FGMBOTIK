from decimal import Decimal
from commands.db import conn, cursor

# Добавьте эту функцию для создания поля fuel (выполнить один раз)
async def add_fuel_column():
    try:
        cursor.execute("ALTER TABLE property ADD COLUMN fuel INTEGER DEFAULT 100")
        conn.commit()
        print("✅ Поле fuel добавлено в таблицу property")
    except:
        pass  # Поле уже существует


async def buy_property(user_id: int, num: int, column: str, summ: int | str) -> None:
    balance = cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    summ = int(Decimal(balance) - Decimal(summ))

    cursor.execute(f"UPDATE users SET balance = ? WHERE user_id = ?", (str(summ), user_id))
    
    # Если покупаем машину, устанавливаем топливо 100%
    if column == 'car':
        cursor.execute(f"UPDATE property SET {column} = ?, fuel = 100 WHERE user_id = ?", (num, user_id))
    else:
        cursor.execute(f"UPDATE property SET {column} = ? WHERE user_id = ?", (num, user_id))
    conn.commit()


async def sell_property(user_id: int, column: str, summ: int | str) -> None:
    balance = cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
    summ = int(Decimal(balance) + Decimal(summ))

    cursor.execute(f"UPDATE users SET balance = ? WHERE user_id = ?", (str(summ), user_id))
    cursor.execute(f"UPDATE property SET {column} = ? WHERE user_id = ?", (0, user_id))
    # При продаже сбрасываем топливо
    if column == 'car':
        cursor.execute(f"UPDATE property SET fuel = 0 WHERE user_id = ?", (user_id,))
    conn.commit()


async def update_fuel(user_id: int, fuel_change: int) -> int:
    """Обновление топлива (положительное или отрицательное значение)"""
    current = cursor.execute("SELECT fuel FROM property WHERE user_id = ?", (user_id,)).fetchone()
    if current:
        new_fuel = max(0, min(100, current[0] + fuel_change))
        cursor.execute("UPDATE property SET fuel = ? WHERE user_id = ?", (new_fuel, user_id))
        conn.commit()
        return new_fuel
    return 0


async def get_fuel(user_id: int) -> int:
    """Получение текущего уровня топлива"""
    result = cursor.execute("SELECT fuel FROM property WHERE user_id = ?", (user_id,)).fetchone()
    return result[0] if result else 0


async def get_car_price(user_id: int) -> int:
    """Получение цены автомобиля пользователя (обычного или эксклюзивного)"""
    car_num = cursor.execute("SELECT car FROM property WHERE user_id = ?", (user_id,)).fetchone()
    if not car_num or car_num[0] == 0:
        return 0
    
    car_id = car_num[0]
    
    # Проверяем эксклюзивные машины
    from commands.basic.property.lists import exclusive_cars
    if car_id in exclusive_cars:
        return exclusive_cars[car_id][5]  # Цена эксклюзивной
    
    # Если не эксклюзивная, проверяем обычные
    from commands.basic.property.lists import cars
    car_data = cars.get(car_id)
    return car_data[5] if car_data else 0
