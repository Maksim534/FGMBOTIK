import random
import asyncio
from bot import bot
from aiogram import types, Dispatcher
from assets.transform import transform_int as tr
from commands.games.db import *
from assets.antispam import antispam
from assets.gettime import gametime
from filters.custom import StartsWith
from user import BFGuser, BFGconst


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






def reg(dp: Dispatcher):
    dp.message.register(oxota, StartsWith("охота"))
    dp.message.register(darts_cmd, StartsWith("дартс"))
    dp.message.register(dice_cmd, StartsWith("кубик"))
    dp.message.register(basketball_cmd, StartsWith("баскетбол"))
    dp.message.register(football_cmd, StartsWith("футбол"))
    dp.message.register(bowling_cmd, StartsWith("боулинг"))
    dp.message.register(casino_cmd, StartsWith("казино"))
    dp.message.register(spin_cmd, StartsWith("спин"))
    dp.message.register(trade_cmd, StartsWith("трейд вверх", "трейд вниз"))
   
