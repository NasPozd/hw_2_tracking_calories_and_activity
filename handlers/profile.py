"""
Модуль обработки команд профиля пользователя в Telegram боте.
Управляет настройкой и обновлением профиля пользователя.
"""

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State

from database import update_user
from services.calculations import calculate_water_norm, calculate_daily_calories
from services.logger import setup_logger, log_user_action

router = Router()
logger = setup_logger()

class ProfileStates(StatesGroup):
    """Состояния для процесса настройки профиля."""
    WAITING_WEIGHT = State()
    WAITING_HEIGHT = State()
    WAITING_AGE = State()
    WAITING_ACTIVITY = State()
    WAITING_CITY = State()

def create_activity_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру для выбора уровня активности.

    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопками уровней активности
    """
    keyboard = [
        [KeyboardButton(text="1 - Сидячий образ жизни")],
        [KeyboardButton(text="2 - Легкая активность (1-3 раза в неделю)")],
        [KeyboardButton(text="3 - Умеренная активность (3-5 раз в неделю)")],
        [KeyboardButton(text="4 - Высокая активность (6-7 раз в неделю)")],
        [KeyboardButton(text="5 - Очень высокая активность")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(Command("set_profile"))
async def cmd_set_profile(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /set_profile.
    Начинает процесс настройки профиля пользователя.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    log_user_action(logger, message.from_user.id, "Начал настройку профиля")
    await message.answer(
        "Давайте настроим ваш профиль!\n"
        "Для начала, укажите ваш вес (кг):"
    )
    await state.set_state(ProfileStates.WAITING_WEIGHT)

@router.message(ProfileStates.WAITING_WEIGHT)
async def process_weight(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод веса пользователя.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    try:
        weight = float(message.text)
        if weight <= 0 or weight > 300:
            raise ValueError("Недопустимое значение веса")
            
        await state.update_data(weight=weight)
        await message.answer(
            "Отлично! Теперь укажите ваш рост (см):"
        )
        await state.set_state(ProfileStates.WAITING_HEIGHT)
        
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите корректное значение веса "
            "(число от 1 до 300, например: 70.5)"
        )

@router.message(ProfileStates.WAITING_HEIGHT)
async def process_height(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод роста пользователя.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    try:
        height = float(message.text)
        if height <= 0 or height > 250:
            raise ValueError("Недопустимое значение роста")
            
        await state.update_data(height=height)
        await message.answer(
            "Хорошо! Укажите ваш возраст:"
        )
        await state.set_state(ProfileStates.WAITING_AGE)
        
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите корректное значение роста "
            "(число от 1 до 250, например: 175)"
        )

@router.message(ProfileStates.WAITING_AGE)
async def process_age(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод возраста пользователя.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    try:
        age = int(message.text)
        if age < 12 or age > 120:
            raise ValueError("Недопустимое значение возраста")
            
        await state.update_data(age=age)
        keyboard = create_activity_keyboard()
        await message.answer(
            "Выберите ваш уровень физической активности:",
            reply_markup=keyboard
        )
        await state.set_state(ProfileStates.WAITING_ACTIVITY)
        
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите корректный возраст "
            "(целое число от 12 до 120)"
        )

@router.message(ProfileStates.WAITING_ACTIVITY)
async def process_activity(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает выбор уровня активности пользователя.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    try:
        activity_level = int(message.text[0])
        if activity_level < 1 or activity_level > 5:
            raise ValueError("Недопустимый уровень активности")
            
        await state.update_data(activity=activity_level)
        await message.answer(
            "И последнее, укажите ваш город:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(ProfileStates.WAITING_CITY)
        
    except (ValueError, IndexError):
        await message.answer(
            "❌ Пожалуйста, выберите уровень активности, "
            "используя кнопки на клавиатуре"
        )

@router.message(ProfileStates.WAITING_CITY)
async def process_city(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод города пользователя и завершает настройку профиля.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    try:
        user_data = await state.get_data()
        user_data.update({
            'user_id': message.from_user.id,
            'city': message.text
        })

        calorie_goal = calculate_daily_calories(
            user_data['weight'],
            user_data['height'],
            user_data['age'],
            user_data['activity']
        )
        water_goal = calculate_water_norm(
            user_data['weight'],
            30 * user_data['activity'],
            20
        )

        user_data.update({
            'calorie_goal': calorie_goal,
            'water_goal': water_goal
        })

        update_user(user_data)
        
        await message.answer(
            "✅ Профиль успешно настроен!\n\n"
            f"📊 Ваши рекомендуемые нормы:\n"
            f"🔸 Калории: {calorie_goal:.0f} ккал/день\n"
            f"🔸 Вода: {water_goal:.0f} мл/день\n\n"
            "Используйте /menu чтобы увидеть доступные команды."
        )
        
        log_user_action(
            logger,
            message.from_user.id,
            f"Завершил настройку профиля (вес:{user_data['weight']}, "
            f"рост:{user_data['height']}, возраст:{user_data['age']})"
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении профиля: {str(e)}")
        await message.answer(
            "❌ Произошла ошибка при сохранении профиля.\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )
        await state.clear()
