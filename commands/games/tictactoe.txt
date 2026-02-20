import asyncio
import random
import time
from decimal import Decimal
from aiogram import types, Dispatcher, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from assets.antispam import antispam, antispam_earning, new_earning_msg
from assets.transform import transform_int as tr
from commands.games.db import gXX, update_balance
from commands.db import url_name, cursor, conn
from filters.custom import StartsWith
from user import BFGuser, BFGconst
from bot import bot

# Словари для хранения игр
games = []  # Активные игры
waiting = {}  # Ожидающие игры


def creat_start_kb() -> InlineKeyboardMarkup:
    """Клавиатура для принятия вызова"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🤯 Принять вызов", callback_data="tictactoe_start"))
    return builder.as_markup()


class Game:
    """Класс игры Крестики-нолики"""
    def __init__(self, chat_id: int, user_id: int, summ: int, message_id: int):
        self.chat_id = chat_id
        self.user_id = user_id
        self.chips = {}
        self.r_id = 0
        self.move = random.choice(['cross', 'zero'])
        self.message_id = message_id
        self.summ = summ
        self.board = [['  ' for _ in range(3)] for _ in range(3)]
        self.last_time = time.time()
    
    def start(self):
        """Начало игры после принятия вызова"""
        self.last_time = time.time()
        players = [self.user_id, self.r_id]
        random.shuffle(players)
        self.chips['cross'] = players[0]
        self.chips['zero'] = players[1]
    
    def get_user_chips(self, user_id: int) -> str:
        """Определяет, какими фишками играет пользователь"""
        if self.chips.get('cross') == user_id:
            return 'cross'
        return 'zero'
        
    def make_move(self, x: int, y: int, user_id: int) -> str:
        """Совершение хода"""
        if self.board[x][y] != '  ':
            return "not empty"
        
        marker = self.get_user_chips(user_id)
        marker = '❌' if marker == 'cross' else '⭕️'
        
        self.last_time = time.time()
        self.board[x][y] = marker
        
        self.move = 'zero' if self.move == 'cross' else 'cross'
        return "ok"
    
    def check_winner(self):
        """Проверка победителя"""
        win_combinations = [
            # горизонтали
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            # вертикали
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            # диагонали
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)]
        ]
        
        for combo in win_combinations:
            symbols = [self.board[x][y] for x, y in combo]
            if symbols[0] != '  ' and symbols[0] == symbols[1] == symbols[2]:
                return symbols[0]
        
        if all(self.board[i][j] != '  ' for i in range(3) for j in range(3)):
            return 'draw'
        
        return None
    
    def get_kb(self) -> InlineKeyboardMarkup:
        """Создание клавиатуры игрового поля"""
        builder = InlineKeyboardBuilder()
        for i in range(3):
            row = []
            for j in range(3):
                row.append(
                    InlineKeyboardButton(
                        text=self.board[i][j],
                        callback_data=f"tictactoe_move_{i}_{j}"
                    )
                )
            builder.row(*row, width=3)
        return builder.as_markup()


def find_waiting(chat_id: int, message_id: int):
    """Поиск ожидающей игры по ID сообщения"""
    for game in waiting.keys():
        if game.chat_id == chat_id and game.message_id == message_id:
            return game
    return None


def find_game_by_mid(chat_id: int, message_id: int):
    """Поиск активной игры по ID сообщения"""
    for game in games:
        if game.chat_id == chat_id and game.message_id == message_id:
            return game
    return None


def find_game_by_userid(user_id: int):
    """Поиск игры по ID пользователя"""
    for game in games:
        if game.user_id == user_id or game.r_id == user_id:
            return game
    return None


@antispam
async def tictactoe_cmd(message: types.Message, user: BFGuser):
    """Команда для начала игры в крестики-нолики"""
    win, lose = BFGconst.emj()
    
    # Проверяем, что игра происходит в супергруппе
    if message.chat.type not in ['group', 'supergroup']:
        await message.answer(f"{user.url}, играть можно только в группах! 🎮")
        return
    
    # Проверяем, нет ли уже активной игры
    if find_game_by_userid(user.user_id):
        await message.answer(f'{user.url}, у вас уже есть активная игра {lose}')
        return
        
    # Определяем ставку
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.answer(f'{user.url}, вы не ввели ставку для игры {lose}')
            return
            
        if args[1].lower() in ['все', 'всё']:
            summ = int(user.balance)
        else:
            summ = int(float(args[1].replace('е', 'e')))
    except:
        await message.answer(f'{user.url}, неверный формат ставки {lose}')
        return
    
    if summ < 10:
        await message.answer(f'{user.url}, минимальная ставка - 10$ {lose}')
        return
    
    if summ > int(user.balance):
        await message.answer(f'{user.url}, у вас недостаточно денег {lose}')
        return
    
    # Создаём игру
    msg = await message.answer(
        f"❌⭕️ {user.url} хочет сыграть в крестики-нолики\n"
        f"💰 Ставка: {tr(summ)}$\n"
        f"⏳ <i>Ожидаю противника в течении 3 минут</i>",
        reply_markup=creat_start_kb()
    )
    
    game = Game(msg.chat.id, user.user_id, summ, msg.message_id)
    await new_earning_msg(msg.chat.id, msg.message_id)
    
    # Списываем ставку
    await gXX(user.user_id, summ, 0)
    
    waiting[game] = int(time.time()) + 180


@antispam_earning
async def tictactoe_start_callback(call: types.CallbackQuery, user: BFGuser):
    """Обработка принятия вызова"""
    game = find_waiting(call.message.chat.id, call.message.message_id)
    
    if not game or user.user_id == game.user_id:
        await call.answer()
        return
    
    # Проверяем баланс
    if int(user.balance) < game.summ:
        await call.answer('❌ У вас недостаточно денег.', show_alert=True)
        return
    
    # Добавляем в активные игры
    games.append(game)
    waiting.pop(game)
    
    game.r_id = user.user_id
    game.start()
    
    # Списываем ставку у второго игрока
    await gXX(user.user_id, game.summ, 0)
    
    # Получаем имена игроков
    cross = await url_name(game.chips['cross'])
    zero = await url_name(game.chips['zero'])
    
    crossp, zerop = ('ᅠ ', '👉') if game.move == 'zero' else ('👉', 'ᅠ ')
    
    text = f'''<b>Игра крестики-нолики</b>
💰 Ставка: {tr(game.summ)}$

{crossp}❌ {cross}
{zerop}⭕️ {zero}'''
    
    await call.message.edit_text(text, reply_markup=game.get_kb(), parse_mode="HTML")
    await call.answer()


@antispam_earning
async def tictactoe_move_callback(call: types.CallbackQuery, user: BFGuser):
    """Обработка хода в игре"""
    game = find_game_by_mid(call.message.chat.id, call.message.message_id)
    
    if not game:
        await call.answer("Игра не найдена")
        return
    
    # Проверяем, что игрок участвует
    if game.r_id != user.user_id and game.user_id != user.user_id:
        await call.answer('💩 Вы не можете нажать на эту кнопку.')
        return
    
    # Проверяем, чей ход
    if game.get_user_chips(user.user_id) != game.move:
        await call.answer('❌ Не ваш ход.')
        return
    
    # Получаем координаты
    data = call.data.split('_')
    x = int(data[2])
    y = int(data[3])
    
    result = game.make_move(x, y, user.user_id)
    
    if result == 'not empty':
        await call.answer('❌ Эта клетка уже занята.')
        return
    
    # Обновляем отображение
    cross = await url_name(game.chips['cross'])
    zero = await url_name(game.chips['zero'])
    
    crossp, zerop = ('ᅠ ', '👉') if game.move == 'zero' else ('👉', 'ᅠ ')
    
    text = f'''<b>Игра крестики-нолики</b>
💰 Ставка: {tr(game.summ)}$

{crossp}❌ {cross}
{zerop}⭕️ {zero}'''
    
    await call.message.edit_text(text, reply_markup=game.get_kb(), parse_mode="HTML")
    
    # Проверяем результат
    winner = game.check_winner()
    if winner:
        if winner == 'draw':
            await call.message.answer(
                f'🥸 У вас ничья!\n<i>Деньги возвращены.</i>',
                reply_to_message_id=game.message_id
            )
            # Возвращаем ставки
            await gXX(game.user_id, game.summ, 1)
            await gXX(game.r_id, game.summ, 1)
        else:
            move = 'zero' if winner == '⭕️' else 'cross'
            win_id = game.chips[move]
            win_name = await url_name(win_id)
            await call.message.answer(
                f'🎊 {win_name} поздравляем с победой!\n<i>💰 Приз: {tr(game.summ*2)}$</i>',
                reply_to_message_id=game.message_id
            )
            # Начисляем выигрыш (сумма * 2, так как ставка уже была)
            await gXX(win_id, game.summ * 2, 1)
        
        games.remove(game)
    
    await call.answer()


async def check_waiting():
    """Проверка ожидающих игр"""
    while True:
        current_time = time.time()
        to_remove = []
        
        for game, expire_time in list(waiting.items()):
            if current_time > expire_time:
                to_remove.append(game)
                try:
                    await bot.send_message(
                        game.chat_id,
                        f'❌ Не удалось найти противника.',
                        reply_to_message_id=game.message_id
                    )
                    # Возвращаем деньги
                    await gXX(game.user_id, game.summ, 1)
                except:
                    pass
        
        for game in to_remove:
            waiting.pop(game, None)
        
        await asyncio.sleep(30)


async def check_game():
    """Проверка активных игр на бездействие"""
    while True:
        current_time = time.time()
        to_remove = []
        
        for game in games:
            if current_time > game.last_time + 60:
                to_remove.append(game)
                try:
                    # Определяем победителя (противник не ходил)
                    winner_id = game.chips['zero'] if game.move == 'cross' else game.chips['cross']
                    winner_name = await url_name(winner_id)
                    
                    await bot.send_message(
                        game.chat_id,
                        f'⚠️ <b>От противника давно не было активности</b>\n'
                        f'{winner_name} поздравляем с победой!\n'
                        f'<i>💰 Приз: {tr(game.summ*2)}$</i>',
                        reply_to_message_id=game.message_id
                    )
                    
                    await gXX(winner_id, game.summ * 2, 1)
                    
                except:
                    pass
        
        for game in to_remove:
            games.remove(game)
        
        await asyncio.sleep(30)


# Запуск фоновых задач
loop = asyncio.get_event_loop()
loop.create_task(check_waiting())
loop.create_task(check_game())


def reg(dp: Dispatcher):
    dp.message.register(tictactoe_cmd, lambda msg: msg.text and msg.text.startswith("кн "))
    dp.callback_query.register(tictactoe_start_callback, F.data == "tictactoe_start")
    dp.callback_query.register(tictactoe_move_callback, F.data.startswith("tictactoe_move_"))
