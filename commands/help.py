from aiogram import types, Dispatcher, F
from aiogram.filters import Command
from assets.antispam import antispam, antispam_earning, new_earning_msg, admin_only  # 👈 ИСПРАВЛЕНО
from filters.custom import TextIn, StartsWith
from user import BFGuser
from assets import keyboards as kb
import config as cfg

# ==================== КОНФИГУРАЦИЯ ====================
adm_us = cfg.admin_username.replace('@', '')
adm = f'<a href="t.me/{adm_us}">{cfg.admin_username}</a>'

# ==================== КРАСИВЫЕ ТЕКСТЫ ПОМОЩИ ====================
HELP_TEXTS = {
    "main": """✨ <b>ЦЕНТР ПОМОЩИ</b> ✨

Привет, {0}! Я — твой верный помощник в мире экономики и развлечений. 
Выбери категорию, чтобы узнать все доступные команды:

━━━━━━━━━━━━━━━━━━━━
🏠 <b>ГЛАВНОЕ МЕНЮ</b>
━━━━━━━━━━━━━━━━━━━━

💼 <b>Экономика</b> — баланс, банк, переводы, бизнес
🎮 <b>Игры</b> — казино, спин, кости и другие
🎭 <b>Развлечения</b> — кейсы, браки, приключения
⚔️ <b>Кланы</b> — создай клан и захвати мир
👑 <b>Админ</b> — для избранных (только для админов)

━━━━━━━━━━━━━━━━━━━━
📬 <b>ПОЛЕЗНЫЕ ССЫЛКИ</b>
━━━━━━━━━━━━━━━━━━━━

💬 <b>Чат:</b> {1}
📢 <b>Канал:</b> {2}
🆘 <b>Поддержка:</b> {3}
━━━━━━━━━━━━━━━━━━━━

<i>Нажми на кнопку ниже, чтобы продолжить 👇</i>""",

    "economy": """💼 <b>ЭКОНОМИКА И ФИНАНСЫ</b> 💼

━━━━━━━━━━━━━━━━━━━━
💰 <b>БАЛАНС И ПРОФИЛЬ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>баланс</code> / <code>б</code> — проверить баланс
• <code>профиль [id]</code> — посмотреть профиль
• <code>мой статус</code> — информация о привилегии
• <code>статусы</code> — список всех статусов

━━━━━━━━━━━━━━━━━━━━
🏦 <b>БАНК И ДЕПОЗИТЫ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>банк</code> — информация о банке
• <code>банк положить [сумма]</code> — положить деньги
• <code>банк снять [сумма]</code> — снять деньги
• <code>депозит положить [сумма]</code> — открыть депозит
• <code>депозит снять [сумма]</code> — закрыть депозит

━━━━━━━━━━━━━━━━━━━━
💸 <b>ПЕРЕВОДЫ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>дать [id] [сумма]</code> — перевести деньги
• <code>мой лимит</code> — проверить дневной лимит
• <code>выдать [id] [сумма]</code> — (админ) выдать деньги

━━━━━━━━━━━━━━━━━━━━
🏭 <b>БИЗНЕСЫ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>мой бизнес</code> — управление бизнесом
• <code>построить бизнес</code> — создать бизнес
• <code>продать бизнес</code> — продать бизнес

<i>Чтобы вернуться, нажми кнопку назад 👇</i>""",

    "games": """🎮 <b>ИГРЫ И РАЗВЛЕЧЕНИЯ</b> 🎮

━━━━━━━━━━━━━━━━━━━━
🎰 <b>КАЗИНО И СЛОТЫ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>казино [ставка]</code> — сыграть в казино
• <code>спин [ставка]</code> — покрутить слоты

━━━━━━━━━━━━━━━━━━━━
🎲 <b>КЛАССИЧЕСКИЕ ИГРЫ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>дартс [ставка]</code> — дротики
• <code>кости [число] [ставка]</code> — угадай число
• <code>баскетбол [ставка]</code> — баскетбол
• <code>футбол [ставка]</code> — футбол
• <code>боулинг [ставка]</code> — боулинг

━━━━━━━━━━━━━━━━━━━━
⚔️ <b>ЭКШН ИГРЫ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>охота [ставка]</code> — охота на зверей
• <code>квак [ставка]</code> — прыгающая лягушка
• <code>трейд [вверх/вниз] [ставка]</code> — биржевая игра

━━━━━━━━━━━━━━━━━━━━
💣 <b>МИНЫ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>мины [ставка]</code> — легендарная игра в мины

<i>Удачи и крупных выигрышей! 💰</i>""",

    "entertainment": """🎭 <b>РАЗВЛЕЧЕНИЯ И КЕЙСЫ</b> 🎭

━━━━━━━━━━━━━━━━━━━━
🔮 <b>МАГИЯ И ПРЕДСКАЗАНИЯ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>шар [фраза]</code> — магический шар ответит
• <code>выбери [А] или [Б]</code> — помочь с выбором
• <code>инфа [фраза]</code> — узнать вероятность

━━━━━━━━━━━━━━━━━━━━
💒 <b>БРАКИ И ОТНОШЕНИЯ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>свадьба [id]</code> — предложить руку и сердце
• <code>развод</code> — расторгнуть брак
• <code>мой брак</code> — информация о браке

━━━━━━━━━━━━━━━━━━━━
📦 <b>КЕЙСЫ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>купить кейс [номер] [кол-во]</code> — приобрести кейс
• <code>открыть кейс [номер] [кол-во]</code> — открыть кейс

━━━━━━━━━━━━━━━━━━━━
🌳 <b>САДЫ И ЗЕЛЬЯ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>мой сад</code> — информация о саде
• <code>сад полить</code> — полить растения
• <code>зелья</code> — список зелий
• <code>создать зелье [номер]</code> — создать зелье

<i>Волшебство уже близко! ✨</i>""",

    "clans": """⚔️ <b>КЛАНЫ И ВОЙНЫ</b> ⚔️

━━━━━━━━━━━━━━━━━━━━
🏰 <b>УПРАВЛЕНИЕ КЛАНОМ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>клан создать [название]</code> — создать клан (1 трлн$)
• <code>мой клан</code> — информация о клане
• <code>клан топ</code> — топ кланов
• <code>клан удалить</code> — распустить клан
• <code>клан выйти</code> — покинуть клан

━━━━━━━━━━━━━━━━━━━━
👥 <b>УЧАСТНИКИ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>клан пригласить [id]</code> — пригласить игрока
• <code>клан вступить [id]</code> — вступить в клан
• <code>клан исключить [id]</code> — исключить игрока
• <code>клан повысить [id]</code> — повысить в должности
• <code>клан понизить [id]</code> — понизить в должности

━━━━━━━━━━━━━━━━━━━━
💰 <b>КАЗНА И НАСТРОЙКИ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>клан казна</code> — состояние казны
• <code>клан казна [сумма]</code> — снять деньги
• <code>клан название [название]</code> — сменить название
• <code>клан настройки</code> — настройки прав

━━━━━━━━━━━━━━━━━━━━
⚔️ <b>КЛАНОВЫЕ ВОЙНЫ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>клан война [id]</code> — объявить войну
• <code>клан атака [id]</code> — атаковать участника
• <code>клан перемирие</code> — заключить мир

<i>Единство — наша сила! 💪</i>""",

    "admin": """👑 <b>АДМИНИСТРИРОВАНИЕ</b> 👑

━━━━━━━━━━━━━━━━━━━━
🚨 <b>МОДЕРАЦИЯ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>/banb [id] [время] [причина]</code> — заблокировать
• <code>/unbanb [id]</code> — разблокировать
• <code>/sql [запрос]</code> — выполнить SQL запрос
• <code>/restartb</code> — перезапустить бота

━━━━━━━━━━━━━━━━━━━━
💰 <b>УПРАВЛЕНИЕ БАЛАНСОМ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>выдать [id] [сумма]</code> — выдать деньги
• <code>забрать [сумма]</code> — забрать деньги
• <code>обнулить</code> — обнулить прогресс
• <code>бдать [id] [сумма]</code> — выдать B-Coins

━━━━━━━━━━━━━━━━━━━━
📊 <b>МОНИТОРИНГ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>/hosting</code> — статус сервера
• <code>айди</code> — показать ID пользователя

━━━━━━━━━━━━━━━━━━━━
🎁 <b>ПРОМО И ДОНАТ</b>
━━━━━━━━━━━━━━━━━━━━
• <code>/refsetting</code> — настройки рефералов

<i>С великой властью приходит великая ответственность! ⚡</i>"""
}


@antispam
async def help_cmd(message: types.Message, user: BFGuser):
    """Главная команда помощи"""
    text = HELP_TEXTS["main"].format(
        user.url,
        cfg.chat,
        cfg.channel,
        adm
    )
    msg = await message.answer(
        text,
        reply_markup=kb.help_menu(user.id),  # 👈 ИСПРАВЛЕНО
        disable_web_page_preview=True,
        parse_mode="HTML"
    )
    await new_earning_msg(msg.chat.id, msg.message_id)


@antispam_earning
async def help_category_callback(call: types.CallbackQuery, user: BFGuser):
    """Обработка кнопок категорий"""
    category = call.data.split('_')[1]
    
    if category in HELP_TEXTS:
        text = HELP_TEXTS[category].format(user.url)
        await call.message.edit_text(
            text,
            reply_markup=kb.help_back(user.id),  # 👈 ИСПРАВЛЕНО
            parse_mode="HTML"
        )
    await call.answer()


@antispam_earning
async def help_back_callback(call: types.CallbackQuery, user: BFGuser):
    print(f"🔙 help_back_callback вызван! Data: {call.data}")  # ОТЛАДКА
    print(f"👤 Пользователь: {user.id}")
    """Возврат в главное меню помощи"""
    text = HELP_TEXTS["main"].format(
        user.url,
        cfg.chat,
        cfg.channel,
        adm
    )
    await call.message.edit_text(
        text,
        reply_markup=kb.help_menu(user.id),  # 👈 ИСПРАВЛЕНО
        disable_web_page_preview=True,
        parse_mode="HTML"
    )
    await call.answer()



@antispam
async def help_game_msg(message: types.Message, user: BFGuser):
    """Отдельная команда для игр"""
    await message.answer(HELP_TEXTS["games"].format(user.url), parse_mode="HTML")


@antispam
@admin_only(private=False)
async def help_adm(message: types.Message):
    """Админская помощь (публичная или приватная)"""
    await message.answer(HELP_TEXTS["admin"].format('Admin'), parse_mode="HTML")


def reg(dp: Dispatcher):
    dp.message.register(help_adm, Command("help_adm"))
    dp.message.register(help_cmd, TextIn("/help", "помощь", "help"))
    dp.message.register(help_game_msg, TextIn("игры"))
    
    dp.callback_query.register(help_category_callback, StartsWith("help_"))
    dp.callback_query.register(help_back_callback, F.data == "help_back")
