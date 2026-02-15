import random
import asyncio
import time
from bot import bot
from aiogram import types, Dispatcher
from assets.transform import transform_int as tr
from commands.games.db import *
from assets.antispam import antispam
from assets.antispam import antispam, antispam_earning, new_earning_msg
from assets.gettime import gametime
from filters.custom import StartsWith
from user import BFGuser, BFGconst
from assets.keyboards.game import kwak_game
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_summ(message: types.Message, balance: int, index: int) -> int:
    if message.text.lower().split()[index] in ['все', 'всё']:
        return balance

    summ = message.text.split()[index].replace('е', 'e')
    return int(float(summ))


async def game_check(message: types.Message, user: BFGuser, index=1) -> int | None:
    win, lose = BFGconst.emj()

    try:
        summ = get_summ(message, int(user.balance), index)
    except:
        await message.answer(f'{user.url}, вы не ввели ставку для игры {lose}')
        return None

    if int(user.balance) < summ:
        await message.answer(f'{user.url}, ваша ставка не может быть больше вашего баланса {lose}')
        return None

    if summ < 10:
        await message.answer(f'{user.url}, ваша ставка не может быть меньше 10$ {lose}')
        return None

    gt = await gametime(user.id)

    if gt == 1:
        await message.answer(f'{user.url}, играть можно каждые 5 секунды. Подождите немного {lose}')
        return None

    return summ


@antispam
async def darts_cmd(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    summ = await game_check(message, user, index=1)
    
    if not summ:
        return

    rx1 = await message.reply_dice(emoji="🎯")
    rx = rx1.dice.value

    if int(rx) == 5:
        await message.answer(f'{user.url}, вы были на волоске от победы! 🎯\n💰 Ваши средства в безопасности! (х1)')

    elif int(rx) == 6:
        c = round(Decimal(summ * 2))
        await gXX(user.id, c, 1)
        await message.answer(f'{user.url}, в яблочко! 🎯\n💰 Ваш приз: {tr(c)}$!')

    else:
        await gXX(user.id, summ, 0)
        await message.answer(f'{lose} | К сожалению Ваша победа ускользнула от Вас! 🎯️')


@antispam
async def dice_cmd(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()

    try:
        ch = int(message.text.split()[1])
        summ = await game_check(message, user, index=2)
        if not summ:
            return
    except:
        await message.answer(f'{lose} | Ошибка. Вы не ввели ставку для игры.')
        return

    if ch not in range(1, 7):
        t = 'меньше 0' if ch < 1 else 'больше 6'
        await message.answer(f'{lose} | Ошибка. Вы не можете поставить на число {t}.')
        return
        
    rx1 = await message.reply_dice(emoji="🎲")
    rx = rx1.dice.value

    if int(rx) == ch:
        c = round(Decimal(summ * 4))
        await gXX(user.id, c, 1)
        await message.answer(f'{win} | Поздравляю! Вы угадали число. Ваш выигрыш составил - {tr(c)}$')
        return
    else:
        await gXX(user.id, summ, 0)
        await message.answer(f'{win} | К сожалению вы не угадали число! 🎲')
        return


@antispam
async def basketball_cmd(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    summ = await game_check(message, user, index=1)

    if not summ:
        return
    
    rx1 = await message.reply_dice(emoji="🏀")
    rx = rx1.dice.value

    if int(rx) == 5:
        c = round(Decimal(summ * 2))
        await gXX(user.id, c, 1)
        await message.answer(f'{user.url}, мяч в кольце, ура! 🏀\n💰 Ваш приз: {tr(c)}$!')

    elif int(rx) == 4:
        await message.answer(f'{user.url}, бросок оказался на грани фола! 🏀\n💰 Ваши средства в безопасности! (х1)')
    else:
        await gXX(user.id, summ, 0)
        await message.answer(f'{win} | К сожалению вы не попали в кольцо! 🏀')


@antispam
async def football_cmd(message: types.Message, user: BFGuser):
    summ = await game_check(message, user, index=1)

    if not summ:
        return
    
    rx1 = await message.reply_dice(emoji="⚽️")
    rx = rx1.dice.value
    
    if int(rx) in [3, 5]:
        c = round(Decimal(summ * 2))
        await gXX(user.id, c, 1)
        await message.answer(f'{user.url}, мяч в воротах, ура! ⚽️\n💰 Ваш приз: {tr(c)}$!')
    
    elif int(rx) == 4:
        await message.answer(f'{user.url}, мяч попал в штангу, но не в ворота! 😱\n💔 Удача в следующий раз!')
    else:
        await gXX(user.id, summ, 0)
        await message.answer(f'{user.url}, вы пробили по мячу, но он пролетел мимо! ⚽️💨')


@antispam
async def bowling_cmd(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    summ = await game_check(message, user, index=1)

    if not summ:
        return
        
    rx1 = await message.reply_dice(emoji="🎳️")
    rx = rx1.dice.value

    if int(rx) == 6:
        c = round(Decimal(summ * 2))
        await gXX(user.id, c, 1)
        await message.answer(f'{user.url}, страйк! Полная победа! 🎳️\n💰 Ваш приз: {tr(c)}$!')

    elif int(rx) == 5:
        await message.answer(f'{user.url}, так близко к победе! 🎳\n💰 Ваши средства в безопасности! (х1)')
    else:
        await gXX(user.id, summ, 0)
        await message.answer(f'{win} | К сожалению мимо всех кеглей! 🎳')


@antispam
async def casino_cmd(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    summ = await game_check(message, user, index=1)

    coff_dict = {
        0: [2, 1.75, 1.5, 1.25, 0.75, 0.5, 0.25, 0.1],
        1: [2, 1.75, 1.5, 1.25, 0.75, 0.5, 0.25],
        4: [2.25, 1.75, 1.5, 1.25, 0.75, 0.5, 0.25],
    }  # иксы которые может выиграть человек с n статусом

    if not summ:
        return
        
    coff = coff_dict.get(user.status, coff_dict[1])
    x = random.choice(coff)

    if x > 1:
        c = int(summ * x)
        c2 = int(c - summ)
        await message.answer(f'{user.url}, вы выиграли {tr(c)}$ (x{x})  {win}')
        await gXX(user.id, c2, 1)
    else:
        c = summ - int(summ * x)
        await message.answer(f'{user.url}, вы проиграли {tr(c)}$ (x{x})  {win}')
        await gXX(user.id, c, 0)


@antispam
async def spin_cmd(message: types.Message, user: BFGuser):
    summ = await game_check(message, user, index=1)

    if not summ:
        return

    emojis = ['🎰', '🍓', '🍒', '💎', '🍋', '🌕', '🖕', '💰', '🍎', '🎁', '💎', '💩', '🍩', '🍗', '🍏', '🔥', '🍊']

    emojis = [random.choice(emojis) for _ in range(3)]
    emj = '|{}|{}|{}|'.format(*emojis)

    payout = 0
    unique_emojis = set(emojis)
    
    for emoji in unique_emojis:
        if emoji == '💎' or emoji == '🍋':
            payout += summ * 0.25
        elif emoji == '🎰':
            payout += summ
            
    if len(unique_emojis) == 1:
        payout += summ * 5

    if payout != 0:
        c2 = tr(int(summ + payout))
        await gXX(user.id, payout, 1)
        await message.answer(f'{user.url}\n{emj} выигрыш: {c2}$')
    else:
        await message.answer(f'{user.url}\n{emj} Удача не на твоей стороне. Выигрыш: 0$')
        await gXX(user.id, summ, 0)


@antispam
async def trade_cmd(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()

    try:
        action = message.text.split()[1]
        summ = await game_check(message, user, index=2)

        if not summ or action.lower() not in ['вверх', 'вниз']:
            return
    except:
        await message.answer(f'{user.url}, вы не ввели ставку для игры {lose}')
        return

    random_number = random.randint(0, 100)
    random_direction = random.randint(1, 2)

    if random_direction == 1:
        result = 'вверх' if action.lower() == 'вверх' else 'вниз'
    else:
        result = 'вниз' if action.lower() == 'вверх' else 'вверх'

    if action.lower() == result:
        payout = int(summ * random_number / 100)
        await message.answer(f'{user.url}\n📈 Курс пошёл {result} на {random_number}%\n✅ Ваш выигрыш составил - {tr(payout)}$')
        await gXX(user.id, payout, 1)
    else:
        payout = int(summ - (summ * random_number / 100))
        await message.answer(f'{user.url}\n📈 Курс пошёл {result} на {random_number}%\n❌ Вы проиграли - {tr(payout)}$')
        await gXX(user.id, payout, 0)

@antispam
async def oxota(message: types.Message, user: BFGuser):
    summ = await game_check(message, user, index=1)
    
    if not summ:
        return
    
    wins = [
        "💥🐗 | Отлично! Вы попали в кабана, вот ваша награда: {}$",
        "💥🐊 | Отлично! Вы попали в крокодила, вот ваша награда: {}$",
        "💥🐿️🌲 | Отлично! Вы попали в бобра, вот ваша награда: {}$",
        "💥🐰 | Отлично! Вы попали в зайца, вот ваша награда: {}$",
        "💥🐅 | Отлично! Вы попали в рысь, вот ваша награда: {}$",
        "💥🐘 | Отлично! Вы попали в слона, вот ваша награда: {}$"
    ]
    
    losses = [
        "💥🦔 | Звезда этот ёжик! Вы даже не сообразили, что точно попали в цель. Но вот теперь стоит держать свое оружие и идти дальше, ведь зазвездился - проиграл!",
        "💥😷 | Вот к черту, вы заразились в больнице! Этот раунд лучше пропустить, сидите дома и лечитесь.",
        "💥💀 | Попали по нефору... Теперь у вас дурной привык, и вы тусите каждый вечер в одной из местных грязных бардаков.",
        "💥🐻 | Большой и сильный медведь... только кажется, что попадания не было. Но вот он, на вас смотрит глазами, наполненными гневом!",
        "💥🐺 | Волки - наши братья меньшие. На этот раз вам не удалось их победить, но можно попробовать еще разок.",
        "💥🦊 | Попадание в лису - это успех! Но будет лучше, если вы не смените свое направление и не пойдете на охоту на этих милых зверьков в нашем мире."
    ]
    
    chance = random.random()
    
    if chance < 0.45:
        su = int(summ * 0.5)
        txt = random.choice(wins).format(tr(su))
        await update_balance(user.user_id, su, operation='add')
    elif chance < 0.5:
        txt = '💥❎ | Вы промазали...  деньги остаются при вас.'
    else:
        txt = random.choice(losses)
        await update_balance(user.user_id, summ, operation='subtract')
    
    msg = await message.answer("💥 | Выстрел... посмотрим в кого вы попали")
    await asyncio.sleep(2)
    await bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=txt)


@antispam
async def crash(message: types.Message, user: BFGuser):
	win, lose = BFGconst.emj()
	summ = await game_check(message, user, index=1)
	
	if not summ:
		return
	
	try:
		bet = round(float(message.text.lower().split()[2]), 2)
		if not (1.01 <= bet <= 10):
			await message.answer(f'''🥶 {user.url}, <i>ты ввел что-то неправильно!</i>
<code>·····················</code>
📈 <b>Краш [ставка] [1.01-10]</b>

Пример: <code>краш 100 1.1</code>
Пример: <code>краш 100 4</code>''')
			return
		
	except:
		await message.answer(f'{user.url}, вы не ввели ставку для игры {lose}')
		return
	
	bet2 = bet if bet < 2 else (bet+3 if bet <= 7 else 10)
	rnumber = round(random.uniform(1, bet2), 2)
	
	if bet < rnumber:
		summ = int(bet*summ)
		await message.answer(f'🚀 {user.url}, ракета остановилась на x{rnumber} 📈\n✅ Ты выиграл! Твой выигрыш составил {tr(summ)}$')
		await update_balance(user.user_id, summ, operation='add')
	else:
		await message.answer(f'🚀 {user.url}, ракета упала на x{rnumber} 📉\n❌ Ты проиграл {tr(summ)}$')
		await update_balance(user.user_id, summ, operation='subtract')


# ==================== ИГРА "КВАК" ====================
games = {}  # Словарь для хранения активных игр

class Game:
    """Класс игры Квак"""
    def __init__(self, chat_id: int, user_id: int, summ: int):
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_id = 0
        self.summ = summ
        self.grid = [['🍀'] * 5 for _ in range(4)] + [['◾️', '◾️', '🐸', '◾️', '◾️']]
        self.place_traps()
        self.player = [4, 2]  # [row, col]
        self.last_time = time.time()

    def place_traps(self):
        """Размещение ловушек на поле"""
        trap_counts = [4, 3, 2, 1]
        for row in range(4):
            positions = [i for i in range(5)]
            for _ in range(trap_counts[row]):
                if positions:
                    pos = random.choice(positions)
                    self.grid[row][pos] = '🌀'
                    positions.remove(pos)

    def get_x(self, n: int) -> float:
        """Получение множителя для ряда"""
        return {3: 1.23, 2: 2.05, 1: 5.11, 0: 25.96}.get(n, 1)

    def get_pole(self, stype: str, txt: str = '') -> str:
        """Формирование текстового отображения поля"""
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

    def make_move(self, x: int) -> str:
        """Совершение хода в указанную позицию"""
        self.grid[self.player[0]][self.player[1]] = '🍀'
        self.player = [self.player[0]-1, x]
        position = self.grid[self.player[0]][self.player[1]]
        self.grid[self.player[0]][self.player[1]] = '🐸️'

        if position == '🌀':
            return 'lose'
        if self.player[0] == 0:
            return 'win'
        return 'continue'

    async def stop_game(self) -> int:
        """Завершение игры с возвратом выигрыша"""
        x = self.get_x(self.player[0])
        win_sum = int(self.summ * x)
        # Добавляем чистый выигрыш
        await gXX(self.user_id, win_sum - self.summ, 1)
        return win_sum

    def get_text(self, stype: str) -> str:
        """Получение текста для сообщения"""
        win, lose = BFGconst.emj()

        messages = {
            'win': f'{win} {{}}, <b>ты успешно забрал приз!</b>',
            'stop': f'❌ {{}}, <b>вы отменили игру!</b>',
            'lose': f'{lose} {{}}, <b>ты проиграл!\nВ следующий раз повезет!</b>',
            'game': f'🐸 {{}}, <b>ты начал игру Frog Time!</b>'
        }

        txt = messages.get(stype, messages['game'])
        pole = self.get_pole(stype)
        next_win = self.get_x(self.player[0]-1) if self.player[0] > 0 else 0

        txt += f'\n<code>·····················</code>\n💸 <b>Ставка:</b> {tr(self.summ)}$'

        if stype == 'game' and next_win:
            nsumm = int(self.summ * next_win)
            txt += f'\n🍀 <b>Сл. кувшин:</b> х{next_win} / {tr(nsumm)}$'

        txt += '\n\n' + pole
        return txt

    def get_kb(self):
        """Получение клавиатуры с учётом текущего ряда"""
        from assets.keyboards.game import kwak_game
        return kwak_game(self.user_id, self.player[0])


@antispam
async def kwak_cmd(message: types.Message, user: BFGuser):
    """Основная команда для запуска игры Квак"""
    win, lose = BFGconst.emj()

    if user.user_id in games:
        await message.answer(f'{user.url}, у вас уже есть активная игра {lose}')
        return

    # Используем вашу стандартную проверку ставки
    summ = await game_check(message, user, index=1)
    if not summ:
        return

    # Создаем игру
    game = Game(message.chat.id, user.user_id, summ)
    games[user.user_id] = game

    # Списываем ставку
    await gXX(user.id, summ, 0)

    msg = await message.answer(
        game.get_text('game').format(user.url),
        reply_markup=game.get_kb()
    )
    await new_earning_msg(msg.chat.id, msg.message_id)
    game.message_id = msg.message_id


@antispam_earning
async def kwak_callback(call: types.CallbackQuery, user: BFGuser):
    """Обработка нажатий на кнопки игры"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    game = games.get(user_id, None)

    if not game or game.chat_id != chat_id or game.message_id != message_id:
        await bot.answer_callback_query(call.id, '🐸 Игра не найдена.')
        return

    try:
        x = int(call.data.split('_')[1].split('|')[0])
    except:
        await call.answer('❌ Ошибка хода')
        return

    result = game.make_move(x)

    if result == 'lose':
        await call.message.edit_text(game.get_text('lose').format(user.url))
        games.pop(user_id)
    elif result == 'win':
        win_sum = await game.stop_game()
        await call.message.edit_text(
            game.get_text('win').format(user.url) + f'\n💰 Выигрыш: {tr(win_sum)}$'
        )
        games.pop(user_id)
    else:
        await call.message.edit_text(
            game.get_text('game').format(user.url),
            reply_markup=game.get_kb()
        )

    await call.answer()


@antispam_earning
async def kwak_stop_callback(call: types.CallbackQuery, user: BFGuser):
    """Обработка нажатия на кнопку остановки"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    game = games.get(user_id, None)

    if not game or game.chat_id != chat_id or game.message_id != message_id:
        await bot.answer_callback_query(call.id, '🐸 Игра не найдена.')
        return

    win_sum = await game.stop_game() if game.player[0] != 4 else 0
    txt = 'stop' if game.player[0] == 4 else 'win'

    if game.player[0] != 4:
        await call.message.edit_text(
            game.get_text(txt).format(user.url) + f'\n💰 Выигрыш: {tr(win_sum)}$'
        )
    else:
        await call.message.edit_text(game.get_text(txt).format(user.url))

    games.pop(user_id)
    await call.answer()


async def check_game():
    """Проверка неактивных игр"""
    while True:
        current_time = time.time()
        for user_id, game in list(games.items()):
            if current_time > game.last_time + 60:
                games.pop(user_id)
                try:
                    win_sum = await game.stop_game()
                    txt = f'⚠️ <b>От вас давно не было активности!</b>\nИгра отменена! На ваш баланс возвращено {tr(win_sum)}$'
                    await bot.send_message(game.chat_id, txt, reply_to_message_id=game.message_id)
                except:
                    pass
        await asyncio.sleep(15)


# Запуск фоновой проверки
loop = asyncio.get_event_loop()
if not loop.is_running():
    loop.create_task(check_game())
else:
    asyncio.create_task(check_game())


# Регистрация хэндлеров (aiogram 3.x)
def register_frog_handlers(dp: Dispatcher):
    dp.message.register(kwak_cmd, lambda message: message.text.lower().startswith('квак'))
    dp.callback_query.register(kwak_callback, lambda call: call.data.startswith('kwak_'))
    dp.callback_query.register(kwak_stop_callback, lambda call: call.data.startswith('kwak-stop'))



def reg(dp: Dispatcher):
	dp.message.register(kwak_cmd, StartsWith('квак'))
	dp.callback_query.register(kwak_callback, lambda call: call.data.startswith('kwak_'))
	dp.callback_query.register(kwak_stop_callback, lambda call: call.data.startswith('kwak-stop'))
	dp.message.register(oxota, StartsWith("охота"))
	dp.message.register(darts_cmd, StartsWith("дартс"))
	dp.message.register(dice_cmd, StartsWith("кубик"))
	dp.message.register(basketball_cmd, StartsWith("баскетбол"))
	dp.message.register(football_cmd, StartsWith("футбол"))
	dp.message.register(bowling_cmd, StartsWith("боулинг"))
	dp.message.register(casino_cmd, StartsWith("казино"))
	dp.message.register(spin_cmd, StartsWith("спин"))
	dp.message.register(trade_cmd, StartsWith("трейд вверх", "трейд вниз"))
