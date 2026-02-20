from aiogram import types, Dispatcher, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from assets.antispam import antispam
from commands.basic.property.lists import cars
from assets.transform import transform_int as tr
from filters.custom import StartsWith
from user import BFGuser, BFGconst
from assets.antispam import antispam, antispam_earning

# Словарь для хранения текущей страницы каждого пользователя
user_car_page = {}  # {user_id: page_number}


def get_car_keyboard(user_id: int, current_page: int, total_cars: int) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру для навигации по автосалону"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки навигации
    nav_buttons = []
    
    # Кнопка "Назад" (если не первая страница)
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"carsalon_page_{current_page-1}_{user_id}"
            )
        )
    else:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⏺️",
                callback_data="ignore"
            )
        )
    
    # Счётчик страниц
    nav_buttons.append(
        InlineKeyboardButton(
            text=f"{current_page}/{total_cars}",
            callback_data="ignore"
        )
    )
    
    # Кнопка "Вперёд" (если не последняя страница)
    if current_page < total_cars:
        nav_buttons.append(
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"carsalon_page_{current_page+1}_{user_id}"
            )
        )
    else:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⏺️",
                callback_data="ignore"
            )
        )
    
    builder.row(*nav_buttons)
    
    # Кнопка "Купить"
    builder.row(
        InlineKeyboardButton(
            text="💰 Купить этот автомобиль",
            callback_data=f"carsalon_buy_{current_page}_{user_id}"
        )
    )
    
    # Кнопка "Закрыть"
    builder.row(
        InlineKeyboardButton(
            text="❌ Закрыть",
            callback_data="carsalon_close"
        )
    )
    
    return builder.as_markup()


@antispam
async def autosalon_cmd(message: types.Message, user: BFGuser):
    """Команда /автосалон - просмотр доступных автомобилей"""
    user_id = user.id
    
    # Начинаем с первой страницы
    user_car_page[user_id] = 1
    
    # Получаем общее количество машин
    total_cars = len(cars)
    
    # Показываем первую машину
    await show_car(message, user, page=1, total_cars=total_cars)


async def show_car(message: types.Message, user: BFGuser, page: int, total_cars: int, edit: bool = False):
    """Показывает автомобиль на указанной странице"""
    
    # Получаем данные машины
    car_data = cars.get(page)
    if not car_data:
        await message.answer(f"{user.url}, автомобиль с номером {page} не найден.")
        return
    
    # Распаковываем данные
    name, speed, power, acceleration, photo_url, price = car_data
    
    # Формируем текст
    text = f"""
🚗 <b>{name}</b>

📊 <b>Характеристики:</b>
⛽️ Максимальная скорость: {speed} км/ч
🐎 Лошадиных сил: {power}
⏱ Разгон до 100 км/ч: {acceleration} сек

💰 <b>Цена:</b> {tr(price)}$)

<i>Для покупки нажмите кнопку "Купить"</i>
"""
    
    # Создаём клавиатуру
    keyboard = get_car_keyboard(user.id, page, total_cars)
    
    if edit:
        # Редактируем существующее сообщение
        await message.edit_caption(
            caption=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        # Отправляем новое сообщение с фото
        await message.answer_photo(
            photo=photo_url,
            caption=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )


@antispam_earning
async def autosalon_callback(call: types.CallbackQuery, user: BFGuser):
    """Обработчик нажатий на кнопки автосалона"""
    data = call.data.split('_')
    action = data[1]
    
    if action == "page":
        # Листание страниц
        page = int(data[2])
        target_user_id = int(data[3])
        
        # Проверяем, что это тот же пользователь
        if target_user_id != user.id:
            await call.answer("Это не ваша сессия!", show_alert=True)
            return
        
        # Сохраняем текущую страницу
        user_car_page[user.id] = page
        
        # Получаем общее количество машин
        total_cars = len(cars)
        
        # Обновляем сообщение
        await show_car(call.message, user, page, total_cars, edit=True)
        await call.answer()
    
    elif action == "buy":
        # Покупка автомобиля
        page = int(data[2])
        target_user_id = int(data[3])
        
        if target_user_id != user.id:
            await call.answer("Это не ваша сессия!", show_alert=True)
            return
        
        # Получаем данные машины
        car_data = cars.get(page)
        if not car_data:
            await call.answer("Автомобиль не найден!", show_alert=True)
            return
        
        name, speed, power, acceleration, photo_url, price = car_data
        
        # Проверяем, нет ли уже машины
        if int(user.property.car) != 0:
            await call.answer("У вас уже есть автомобиль!", show_alert=True)
            return
        
        # Проверяем баланс
        if int(user.balance) < price:
            await call.answer(f"Недостаточно денег! Нужно {tr(price)}$", show_alert=True)
            return
        
        # Покупаем
        await db.buy_property(user.id, page, "car", price)
        
        await call.message.edit_caption(
            caption=f"✅ {user.url}, вы успешно купили {name} за {tr(price)}$!\n\n"
                    f"Теперь введите команду <b>моя машина</b>, чтобы посмотреть информацию.",
            parse_mode="HTML",
            reply_markup=None
        )
        await call.answer("Поздравляем с покупкой!", show_alert=True)
    
    elif action == "close":
        # Закрываем автосалон
        await call.message.delete()
        await call.answer()


def reg(dp: Dispatcher):
    dp.message.register(autosalon_cmd, StartsWith("/автосалон"))
    dp.message.register(autosalon_cmd, StartsWith("автосалон"))
    dp.callback_query.register(autosalon_callback, F.data.startswith("carsalon_"))
