from datetime import datetime, timedelta

from aiogram import Dispatcher, types

from assets.antispam import antispam
from commands.basic.bank.db import *
from assets.transform import transform_int as tr
from filters.custom import StartsWith, TextIn
from user import BFGuser, BFGconst


async def bank_pc(status):
    status_info = {
        0: {"p": 6, "c": 5, "st": "Обычный"},
        1: {"p": 8, "c": 4.5, "st": "Standart VIP"},
        2: {"p": 10, "c": 3.5, "st": "Gold VIP"},
        3: {"p": 12, "c": 3, "st": "Platinum VIP"},
        4: {"p": 15, "c": 2.5, "st": "Администратор"}
    }

    info = status_info.get(status, status_info[0])
    return info["p"], info["c"], info["st"]


async def dep_comsa(status):
    status_info = {
        0: {"c": 0.05, "p": 5},
        1: {"c": 0.045, "p": 4.5},
        2: {"c": 0.035, "p": 3.5},
        3: {"c": 0.03, "p": 3},
        4: {"c": 0.025, "p": 2.5}
    }

    info = status_info.get(status, {"c": 0, "p": 0})
    return info["c"], info["p"]


async def get_summ(msg, balance):
    if msg[2] in ['все', 'всё']:
        return balance
    else:
        summ = msg[2].replace('е', 'e')
        return int(float(summ))


@antispam
async def bank_cmd(message: types.Message, user: BFGuser):
    p, c, st = await bank_pc(user.status)

    if int(user.depozit) == 0:
        timedepozit = 'Нет депозита'
    else:
        timedepozit = datetime.fromtimestamp(user.depozit_time)
        timedepozit += timedelta(days=3)
        timedepozit = timedepozit.strftime('%Y-%m-%d в %H:%M:%S')

    await message.answer(f'''{user.url}, ваш банковский счёт:
👤 Владелец: {user.name}
━━━━━━━━━━━━━━━━━━━━━
💰 Банковский счет: {user.bank.tr()}$
💎 статус: {st}
━━━━━━━━━━━━━━━━━━━━━
📊 условия по депозиту:
   〽️ Процентная ставка: {p}%
   💱 Банковская комиссия: {c}%
━━━━━━━━━━━━━━━━━━━━━
💵 текущий депозит: {user.depozit.tr()}$
⏳ доступно к снятию: {timedepozit}

{BFGconst.ads}''')


@antispam
async def put_bank_cmd(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()

    try:
        msg = message.text.split()
        if len(msg) < 3:
            return
        summ = await get_summ(msg, user.balance)
    except:
        return

    summ, balance = Decimal(str(summ)), Decimal(str(user.balance))

    if summ > balance:
        await message.answer(f'{user.url}, вы не можете положить в банк больше чем у вас на балансе {lose}')
        return

    if summ <= 0:
        await message.answer(f'{user.url}, вы не можете положить в банк отрицательную сумму денег {lose}')
        return

    await user.balance.upd(summ, '-')
    await user.bank.upd(summ, '+')
    await message.answer(f'{user.url}, вы успешно положили на банковский счёт {tr(summ)}$ {win}')


@antispam
async def takeoff_bank_cmd(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()

    try:
        msg = message.text.split()
        if len(msg) < 3:
            return
        summ = await get_summ(msg, user.bank)
    except:
        return

    summ, balance = Decimal(str(summ)), Decimal(str(user.bank))

    if summ > balance:
        await message.answer(f'{user.url}, вы не можете снять с банка больше чем у вас есть {lose}')
        return

    if summ <= 0:
        await message.answer(f'{user.url}, вы не можете снять с банка отрицательную сумму денег {lose}')
        return

    await user.bank.upd(summ, '-')
    await user.balance.upd(summ, '+')
    await message.answer(f'{user.url}, вы успешно сняли с банковского счёта {tr(summ)}$ {win}')


@antispam
async def put_depozit_cmd(message: types.Message, user: BFGuser):
    p, c, st = await bank_pc(user.status)
    win, lose = BFGconst.emj()

    try:
        msg = message.text.split()
        if len(msg) < 3:
            return
        summ = await get_summ(msg, user.balance)
    except:
        return

    if summ < 1000:
        await message.answer(f'{user.url}, ваш взнос не может быть меньше 1000$ {lose}')
        return

    if int(user.depozit) != 0:
        await message.answer(f'{user.url}, у вас уже открыт депозит. Вы не можете дополнить его {lose}')
        return

    if summ > int(user.balance):
        await message.answer(f'{user.url}, вы не можете положить на депозит больше чем у вас на балансе {lose}')
        return

    comsa = int(summ * 0.15)
    csumm = int(summ - comsa)

    dt = int(datetime.now().timestamp())
    
    await putdep_db(user.user_id, dt)
    await user.balance.upd(summ, '-')
    await user.depozit.upd(csumm, '+')

    await message.answer(f'{user.url}, вы успешно положили на депозитный счёт {tr(summ)}$ под {p}% {win}.\n\n'
                         f'Вы заплатили комиссию в размере {tr(comsa)}$ (1.5%) за использование банковских услуг.')


@antispam
async def takeoff_depozit_cmd(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    balance = int(user.depozit)

    timedepozit = datetime.fromtimestamp(user.depozit_time)
    timedepozit += timedelta(days=3)
    dt = datetime.now().timestamp()

    c, p = await dep_comsa(user.status)

    try:
        msg = message.text.split()
        if len(msg) < 3:
            return
        summ = await get_summ(msg, balance)
    except:
        return

    if int(timedepozit.timestamp()) > dt:
        await message.answer(f'{user.url}, у вас уже открыт депозит. Вы не можете снять с него деньги раньше времени {lose}')
        return

    if summ > balance:
        await message.answer(f'{user.url}, вы не можете снять с депозита больше чем у вас есть {lose}')
        return

    if summ <= 0:
        await message.answer(f'{user.url}, вы не можете снять с депозита отрицательную сумму денег {lose}')
        return

    if summ < 100:
        await message.answer(f'{user.url}, вы не можете снять меньше 100$ {lose}')
        return
    
    await user.depozit.upd(0)

    if summ < balance:
        ost = balance - summ
        await user.bank.upd(ost, '+')

    comsa = int(summ * float(c))
    csumm = int(summ - comsa)

    await user.balance.upd(csumm, '+')
    await message.answer(f'''{user.url}, вы успешно сняли с депозитного счёта {tr(csumm)}$ 😁

Учтите, сняв деньги вы закрыли свой депозитный счёт. Чтобы его вновь активировать положите под депозит любую сумму.

Вы заплатили налог в размере {tr(comsa)}$ ({p}%) за снятие денег с депозита.''')


def reg(dp: Dispatcher):
    dp.message.register(put_bank_cmd, StartsWith("банк положить"))
    dp.message.register(takeoff_bank_cmd, StartsWith("банк снять"))
    dp.message.register(put_depozit_cmd, StartsWith("депозит положить"))
    dp.message.register(takeoff_depozit_cmd, StartsWith("депозит снять"))
    dp.message.register(bank_cmd, TextIn("банк"))
