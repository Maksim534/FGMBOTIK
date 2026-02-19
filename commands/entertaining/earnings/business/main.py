from aiogram import Dispatcher, types

from assets import keyboards as kb
from assets.transform import transform_int as tr
from assets.antispam import antispam_earning, new_earning, antispam
from commands.entertaining.earnings.business import db
from filters.custom import TextIn, StartsWith
from user import BFGuser, BFGconst

# Максимальный уровень территории бизнеса
MAX_BSTERRITORY = 15

@antispam
async def business_info(message: types.Message, user: BFGuser):
    await message.answer(f'''{user.url}, теперь ты можешь принимать решения сам и влиять на свой бизнес.

🪓 Для начала я проведу тебе маленький инструктаж по поводу данных бизнесов, ты не можешь просто купить бизнес и начать зарабатывать на нём. Теперь вам предоставлена возможность самому влиять на доход, увеличить территорию бизнеса, закупать продукты и платить налоги в казну штата.

🏗 Для начала вам потребуется построить площадку для того чтобы возвести на ней свой бизнес. Для этого используйте команду "Построить бизнес", после этого вами будет куплена маленькая территория под бизнес.

💫 Далее вы можете при помощи команд управлять бизнесом, увеличивать его доход, покупать улучшения и прочее. Чтобы узнать все команды введите команду "Помощь" и выберите соответствующую кнопку.''')


@antispam
async def my_business(message: types.Message, user: BFGuser):
    business = user.business
    win, lose = BFGconst.emj()
    
    if not business:
        await message.answer(f'{user.url}, у вас нет своего бизнеса чтобы построить введите команду "Построить бизнес" {lose}')
        return

    await upd_business_text(message, user, action='send')


async def upd_business_text(call: types.CallbackQuery | types.Message, user: BFGuser, action='edit'):
    business = user.business
    
    if action == 'edit':
        await user.update()

    dox = int(400000 * business.bsterritory.get() / 15)
    ch = int(50000 * (1 + 0.15) ** (business.territory.get() - 4))
    
    current_bsterritory = business.bsterritory.get()
    
    # Стоимость следующего улучшения бизнеса
    if current_bsterritory < MAX_BSTERRITORY:
        ch2 = int(40000 * (1 + 0.15) ** (current_bsterritory - 1))
        next_level_text = f"🆙 до {current_bsterritory + 1} м²: {tr(ch2)}$"
    else:
        next_level_text = "✅ Достигнут максимум!"

    txt = f'''{user.url}, информация о вашем бизнесе "Бизнес":
🧱 Территория участка: {business.territory.tr()} м²
🆙 следующая: {tr(ch)}$

🏢 Территория бизнеса: {current_bsterritory}/{MAX_BSTERRITORY} м²
{next_level_text}

💷 Доход: {tr(dox)}$
💸 Налоги: {business.nalogs.tr()}$/5.000.000$
💰 Прибыль: {business.balance.tr()}$'''
    
    try:
        if action == 'edit':
            await call.message.edit_text(text=txt, reply_markup=kb.business(user.id))
        else:
            msg = await call.answer(text=txt, reply_markup=kb.business(user.id))
            await new_earning(msg)
    except:
        return


@antispam
async def buy_business(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    business = user.business

    if business:
        await message.answer(f'{user.url}, у вас уже есть построенная территория под бизнес. Чтобы узнать подробнее, введите "Мой бизнес" {lose}')
        return

    if int(user.balance) < 100_000:   # при изменении стоимости, меняйте ее также в бд...
        await message.answer(f'{user.url}, у вас недостаточно денег для постройки территории бизнеса. Её стоимость 100.000$ {lose}')
        return

    await db.buy_business(user.id)  # <- тута
    await message.answer(f'{user.url}, вы успешно построили свой бизнес для подробностей введите "Мой бизнес" {win}')


@antispam_earning
async def buy_territory(call: types.CallbackQuery, user: BFGuser):
    win, lose = BFGconst.emj()
    business = user.business

    if not business:
       return

    ch = int(50000 * (1 + 0.15) ** (business.territory.get() - 4))

    if int(user.balance) < ch:
        await call.answer(f'{user.name}, у вас недостаточно денег на балансе чтобы увеличить территорию бизнеса {lose}')
        return
        
    await db.buy_territory(user.id, ch)
    await call.answer(f'{user.name}, вы успешно увеличили территорию бизнеса на 1 м² за {tr(ch)}$ {win}')
    await upd_business_text(call, user)


@antispam_earning
async def buy_bsterritory(call: types.CallbackQuery, user: BFGuser):
    win, lose = BFGconst.emj()
    business = user.business

    if not business:
        return

    # Проверка на максимальный уровень
    current_level = business.bsterritory.get()
    if current_level >= MAX_BSTERRITORY:
        await call.answer(
            f'{user.name}, вы уже достигли максимального уровня территории бизнеса ({MAX_BSTERRITORY} м²)! {lose}',
            show_alert=True
        )
        return

    if business.territory.get() <= current_level:
        await call.answer(
            f'{user.name}, чтобы увеличить бизнес для начала увеличьте его территорию {lose}',
            show_alert=True
        )
        return

    ch = int(40000 * (1 + 0.15) ** (current_level - 1))

    if int(user.balance) < ch:
        await call.answer(
            f'{user.name}, у вас недостаточно денег на балансе чтобы увеличить бизнес. Нужно {tr(ch)}$ {lose}',
            show_alert=True
        )
        return

    await db.buy_bsterritory(user.id, ch)
    await call.answer(
        f'{user.name}, вы успешно увеличили бизнес до {current_level + 1} м² за {tr(ch)}$ {win}',
        show_alert=True
    )
    await upd_business_text(call, user)


@antispam_earning
async def withdraw_profit(call: types.CallbackQuery, user: BFGuser):
    win, lose = BFGconst.emj()
    business = user.business

    if not business:
        return

    if business.balance.get() == 0:
        await call.answer(f'{user.name}, на данный момент на балансе вашего бизнеса нет прибыли {lose}')
        return

    await db.withdraw_profit(user.id, business.balance.get())
    await call.answer(f'{user.name}, вы успешно сняли {business.balance.tr()}$ с баланса вашего бизнеса {win}')
    await upd_business_text(call, user)


@antispam_earning
async def payment_taxes(call: types.CallbackQuery, user: BFGuser):
    win, lose = BFGconst.emj()
    business = user.business
    
    if not business:
        return

    if int(user.balance) < int(business.nalogs):
        await call.answer(f'{user.name}, у вас недостаточно денег чтоб оплатить налоги {lose}')
        return

    if business.nalogs.get() == 0:
        await call.answer(f'{user.name}, у вас нет налогов чтобы их оплатить {win}')
        return

    await db.payment_taxes(user.id, business.nalogs.get())
    await call.answer(f'{user.name}, вы успешно оплатили налоги на сумму {business.nalogs.tr()}$ с вашего игрового баланса {win}')
    await upd_business_text(call, user)
    
    
@antispam
async def sell_business(message: types.Message, user: BFGuser):
    win, lose = BFGconst.emj()
    business = user.business
    
    if not business:
        await message.answer(f'{user.url}, у вас нет своего бизнеса чтобы построить введите команду "Построить бизнес" {lose}')
        return
    
    summ = 100_000  # Половина стоимости бизнеса
    
    for i in range(6, business.territory.get() + 1):  # Компенсация за территорию (50%)
        summ += int(400_000 * (1 + 0.15) ** (i - 4)) // 2
        
    for i in range(6, business.bsterritory.get() + 1):  # Компенсация за территорию бизнеса (50%)
        summ += int(400_000 * (1 + 0.15) ** (i - 1))
    
    await db.sell_business(user.id, summ)
    await message.answer(f'{user.url}, Вы успешно продали свой бизнес за {tr(summ)}$ {win}')


def reg(dp: Dispatcher):
    dp.message.register(my_business, TextIn("мой бизнес"))
    dp.message.register(business_info, TextIn("бизнес"))
    dp.message.register(buy_business, TextIn("построить бизнес"))
    dp.callback_query.register(withdraw_profit, StartsWith("business-sobrat"))
    dp.callback_query.register(buy_territory, StartsWith("business-ter"))
    dp.callback_query.register(buy_bsterritory, StartsWith("business-bis"))
    dp.callback_query.register(payment_taxes, StartsWith("business-nalog"))
    dp.message.register(sell_business, TextIn("продать бизнес"))
