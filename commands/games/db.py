from decimal import Decimal
from commands.db import conn, cursor

async def update_balance(user_id: int, amount: int | str, operation="subtract") -> None:
	balance = cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]
	
	if operation == 'add':
		new_balance = Decimal(str(balance)) + Decimal(str(amount))
	else:
		new_balance = Decimal(str(balance)) - Decimal(str(amount))
	
	new_balance = "{:.0f}".format(new_balance)
	cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (str(new_balance), user_id))
	cursor.execute('UPDATE users SET games = games + 1 WHERE user_id = ?', (user_id,))
	conn.commit()


async def upgames(user_id: int) -> None:
    cursor.execute(f'UPDATE users SET games = games + 1 WHERE user_id = ?', (user_id,))
    conn.commit()


async def gXX(user_id: int, summ: int | str, res: int) -> None:
    balance = cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]

    if res == 1:
        summ = Decimal(balance) + Decimal(summ)
    else:
        summ = Decimal(balance) - Decimal(summ)

    cursor.execute("UPDATE users SET balance = ? where user_id = ?", (str(int(summ)), user_id))
    cursor.execute("UPDATE users SET games = games + 1 where user_id = ?", (user_id,))
    conn.commit()
