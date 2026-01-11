import random
import re


from assets import keyboards as kb
from aiogram import Dispatcher, types
from assets.antispam import antispam
from commands.db import get_colvo_users, setname
from assets.gettime import bonustime, kaznatime, lucktime
from assets.transform import transform_int as tr
import config as cfg
from filters.custom import StartsWith, TextIn
from user import BFGuser, BFGconst


@antispam
async def shar_cmd(message: types.Message, user: BFGuser):
    list = ["Мой ответ - нет", "Мне кажется - да", "Сейчас нельзя предсказать", "Мне кажется - нет",
            "Знаки говорят - нет", "Да", "Нет", "Можешь быть уверен в этом"]
    await message.answer(random.choice(list))


@antispam
async def vibor_cmd(message: types.Message, user: BFGuser):
    list = ["Первый варинат лучше", "Однозначно первый", "Второй варинат лучше", "Однозначно второй"]
    await message.answer(random.choice(list))


@antispam
async def shans_cmd(message: types.Message, user: BFGuser):
    await message.answer(f'Шанс этого - {random.randint(1, 100)}%')


@antispam
async def set_name_cmd(message: types.Message, user: BFGuser):
    user_id = message.from_user.id
    win, lose = BFGconst.emj()
    
    try:
        name = " ".join(message.text.split()[2:])
    except:
        await message.answer(f'{user.url}, ваш ник не может быть короче 5 символов {lose}')
        return

    climit = {0: 20, 1: 25, 2: 30, 3: 45, 4: 50}.get(user.status, 20)

    if re.search(r'<|>|@|t\.me|http', name):
        await message.answer(f'{user.url}, ваш ник содержит запрещённые символы {lose}')
        return

    if len(name) < 5:
        await message.answer(f'{user.url}, ваш ник не может быть короче 5 символов {lose}')
        return

    if len(name) > climit:
        await message.answer(f'{user.url}, ваш ник не может быть длиннее {climit} символов {lose}')
        return

    await setname(name, user_id)
    await message.answer(f'Ваш ник изменён на «{name}»')


@antispam
async def kazna_cmd(message: types.Message, user: BFGuser):
    await message.answer(f'💰 На данный момент казна штата составляет 98.894.419.531.599.545$')


@antispam
async def ogr_kazna(message: types.Message, user: BFGuser):
    user_id = message.from_user.id
    bt, left = await kaznatime(user_id)
    
    if bt == 1:
        await message.answer(f'{user.url}, вы уже грабили казну сегодня. Бегите скорее, полиция уже в пути 🚫')
        return

    if random.randint(1, 3) == 1:
        await message.answer(f'{user.url}, к сожалению вам не удалось ограбить казну ❎')
        return

    summ = random.randint(30_000, 60_000)

    await user.balance.upd(summ, '+')
    await message.answer(f'{user.url}, вы успешно ограбили казну. На ваш баланс зачислено {tr(summ)} ✅')


@antispam
async def try_luck_cmd(message: types.Message, user: BFGuser):
    user_id = message.from_user.id
    bt, left = await lucktime(user_id)
    
    if bt == 1:
        hours = left // 3600
        minutes = (left % 3600) // 60
        txt = f'{hours}ч {minutes}м' if hours > 0 else f'{minutes}м'
        await message.answer(f'{user.url}, ты уже испытывал свою удачу, следующий раз ты сможешь через {txt}')
        return

    summ = random.randint(20_000, 50_000)

    await user.biores.upd(summ, '+')
    await message.answer(f'✅ Вы успешно испытали удачу и получили {tr(summ)}кг биоресурса ☣️')


@antispam
async def bonus_cmd(message: types.Message, user: BFGuser):
    user_id = message.from_user.id
    bt, left = await bonustime(user_id)
    
    if bt == 1:
        hours = left // 3600
        minutes = (left % 3600) // 60
        txt = f'{hours}ч {minutes}м' if hours > 0 else f'{minutes}м'
        await message.answer(f'{user.url}, ты уже получал(-а) ежедневный бонус, следующий бонус ты сможешь получить через {txt}')
        return

    i = random.randint(1, 4)
    
    if i == 1:
        summ = random.randint(10_000, 40_000)
        await user.balance.upd(summ, '+')
        txt = f'{tr(summ)}$ 💰'
    elif i == 2:
        summ = random.randint(100, 950)
        await user.rating.upd(summ, '+')
        txt = f'{summ} рейтинга 👑'
    elif i == 3:
        summ = random.randint(1, 10)
        await user.case[1].upd(summ, '+')
        txt = f'обычный кейс  - {summ} 📦'
    else:
        summ = random.randint(1, 10)
        await user.mine.matter.upd(summ, '+')
        txt = f'{summ} материи 🌌'
        
    await message.answer(f'{user.url}, вам был выдан ежедневный бонус в размере {txt}')


@antispam
async def stats_cmd(message: types.Message, user: BFGuser):
    users, chats, uchats = await get_colvo_users()

    await message.answer(f'''📊 Кол-во пользователей бота: {tr(users)}
📊 Общее кол-во чатов: {tr(chats)}
📊 Общее кол-во игроков в беседах: {tr(uchats)}''')


@antispam
async def chat_list(message: types.Message, user: BFGuser):
    await message.answer(f'''💭 Официальная беседа бота: {cfg.chat}
💭 Официальный канал разработки: {cfg.channel}
🏆 Официальный чат с розыгрышами: ...''', disable_web_page_preview=True)


@antispam
async def my_name(message: types.Message, user: BFGuser):
    await message.answer(f'🗂 Ваш ник - «{user.name}»')
    

async def update_balance(user_id: int, amount: int | str | Decimal, operation='subtract') -> None:
	balance = cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]
	
	if operation == 'add':
		new_balance = Decimal(str(balance)) + Decimal(str(amount))
	else:
		new_balance = Decimal(str(balance)) - Decimal(str(amount))
	
	new_balance = "{:.0f}".format(new_balance)
	cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (str(new_balance), user_id))
	conn.commit()


class Game:
	def __init__(self, chat_id, user_id, summ):
		self.chat_id = chat_id
		self.user_id = user_id
		self.message_id = 0
		self.summ = summ
		self.grid = [['🍀'] * 5 for _ in range(4)] + [['◾️', '◾️', '🐸', '◾️', '◾️']]
		self.place_traps()
		self.player = [4, 2]
		self.last_time = time.time()
	
	def place_traps(self):
		trap_counts = [4, 3, 2, 1]
		for row in range(4):
			positions = [i for i in range(5)]
			for _ in range(trap_counts[row]):
				pos = random.choice(positions)
				self.grid[row][pos] = '🌀'
				positions.remove(pos)
	
	def get_x(self, n):
		return {3: 1.23, 2: 2.05, 1: 5.11, 0: 25.96}.get(n, 1)
	
	def get_pole(self, stype, txt=''):
		if stype == 'game':
			grid = [['🍀'] * 5 for _ in range(4)] + [['◾️', '◾️', '🍀', '◾️', '◾️']]
			grid = [['🍀' if cell == '🐸️' else cell for cell in row] for row in grid]
			grid[self.player[0]][self.player[1]] = '🐸️'
		else:
			grid = self.grid
			if stype == 'lose':
				grid[self.player[0]][self.player[1]] = '🔵'
			
		multiplier = [25.96, 5.11, 2.05, 1.23, 1]
		for i, row in enumerate(grid):
			txt += f"<code>{'|'.join(row)}</code>| ({multiplier[i]}x)\n"
		
		return txt
	
	def make_move(self, x):
		self.grid[self.player[0]][self.player[1]] = '🍀'
		self.player = [self.player[0]-1, x]
		position = self.grid[self.player[0]][self.player[1]]
		self.grid[self.player[0]][self.player[1]] = '🐸️'
		
		if position == '🌀':
			return 'lose'
		if self.player[0] == 0:
			return 'win'
		
	async def stop_game(self):
		x = self.get_x(self.player[0])
		summ = Decimal(str(self.summ)) * Decimal(str(x))
		await update_balance(self.user_id, summ, operation='add')
			
	def get_text(self, stype):
		txt = ''
		if stype == 'win':
			txt += '🤑 {}, <b>ты успешно забрал приз!</b>'
		elif stype == 'stop':
			txt += '❌ {}, <b> вы отменили игру!</b>'
		elif stype == 'lose':
			txt += '💥 {}, <b> ты проиграл!\nВ следующий раз повезет!</b>'
		else:
			txt += '🐸 {}, <b>ты начал игру Frog Time!</b>'
			
		pole = self.get_pole(stype)
		next_win = self.get_x(self.player[0]-1)
		nsumm = trt(int(self.summ*next_win))
		
		txt += f'\n<code>·····················</code>\n💸 <b>Ставка:</b> {trt(self.summ)}$'
		
		if stype == 'game':
			txt += f'\n🍀 <b>Сл. кувшин:</b> х{next_win} / {nsumm}$'
			
		txt += '\n\n' + pole
		return txt
	
	def get_kb(self):
		keyboard = InlineKeyboardMarkup(row_width=5)
		buttons = []
		for i in range(5):
			buttons.append(InlineKeyboardButton('🍀', callback_data=f"kwak_{i}|{self.user_id}"))
		keyboard.add(*buttons)
		txt = '💰 Забрать' if self.player[0] != 4 else '❌ Отменить'
		keyboard.add(InlineKeyboardButton(txt, callback_data=f"kwak-stop|{self.user_id}"))
		return keyboard


@antispam
async def start(message: types.Message, user: BFGuser):
	win, lose = BFGconst.emj()
	
	if user.user_id in games:
		await message.answer(f'{user.url}, у вас уже есть активная игра {lose}')
		return
	
	try:
		if message.text.lower().split()[1] in ['все', 'всё']:
			summ = int(user.balance)
		else:
			summ = message.text.split()[1].replace('е', 'e')
			summ = int(float(summ))
	except:
		await message.answer(f'{user.url}, вы не ввели ставку для игры {lose}')
		return
	
	if summ < 10:
		await message.answer(f'{user.url}, минимальная ставка - 10$ {lose}')
		return
	
	if summ > int(user.balance):
		await message.answer(f'{user.url}, у вас недостаточно денег {lose}')
		return
	
	game = Game(message.chat.id, user.user_id, summ)
	games[user.user_id] = game
	
	await update_balance(user.user_id, summ, operation='subtract')
	msg = await message.answer(game.get_text('game').format(user.url), reply_markup=game.get_kb())
	await new_earning_msg(msg.chat.id, msg.message_id)
	game.message_id = msg.message_id


@antispam_earning
async def game_kb(call: types.CallbackQuery, user: BFGuser):
	user_id = call.from_user.id
	chat_id = call.message.chat.id
	message_id = call.message.message_id
	game = games.get(user_id, None)

	if not game or game.chat_id != chat_id or game.message_id != message_id:
		await bot.answer_callback_query(call.id, '🐸 Игра не найдена.')
		return
	
	x = int(call.data.split('_')[1].split('|')[0])
	result = game.make_move(x)

	if result == 'lose':
		await call.message.edit_text(game.get_text('lose').format(user.url))
		games.pop(user_id)
	elif result == 'win':
		await call.message.edit_text(game.get_text('win').format(user.url))
		games.pop(user_id)
	else:
		await call.message.edit_text(game.get_text('game').format(user.url), reply_markup=game.get_kb())


@antispam_earning
async def game_stop(call: types.CallbackQuery, user: BFGuser):
	user_id = call.from_user.id
	chat_id = call.message.chat.id
	message_id = call.message.message_id
	game = games.get(user_id, None)
	
	if not game or game.chat_id != chat_id or game.message_id != message_id:
		await bot.answer_callback_query(call.id, '🐸 Игра не найдена.')
		return
	
	await game.stop_game()
	txt = 'stop' if game.player[0] == 4 else 'win'
	await call.message.edit_text(game.get_text(txt).format(user.url))
	games.pop(user_id)


async def check_game():
	while True:
		for user_id, game in list(games.items()):
			if int(time.time()) > int(game.last_time + 60):
				games.pop(user_id)
				try:
					await game.stop_game()
					txt = f'⚠️ <b>От вас давно не было активности!</b>\nИгра отменена! На ваш баланс возвращено {tr(game.summ)}$'
					await bot.send_message(game.chat_id, txt, reply_to_message_id=game.message_id)
				except:
					pass
		await asyncio.sleep(15)



def reg(dp: Dispatcher):
    dp.register_message_handler(start, lambda message: message.text.lower().startswith('квак'))
	dp.register_callback_query_handler(game_kb, text_startswith='kwak_')
	dp.register_callback_query_handler(game_stop, text_startswith='kwak-stop')
    dp.message.register(shar_cmd, StartsWith("шар "))
    dp.message.register(vibor_cmd, StartsWith("выбери "))
    dp.message.register(shans_cmd, StartsWith("шанс "))
    dp.message.register(set_name_cmd, StartsWith("сменить ник"))
    dp.message.register(kazna_cmd, TextIn("казна"))
    dp.message.register(stats_cmd, TextIn("статистика бота"))
    dp.message.register(bonus_cmd, TextIn("ежедневный бонус"))
    dp.message.register(try_luck_cmd, TextIn("испытать удачу"))
    dp.message.register(ogr_kazna, TextIn("ограбить казну", "ограбить мерию"))
    dp.message.register(my_name, TextIn("мой ник"))
    dp.message.register(chat_list, TextIn("!беседа"))
