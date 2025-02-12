"""
Модуль обработки команд для записи тренировок.
Позволяет пользователям логировать свои тренировки и отслеживать активность.
"""

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from database import get_user_data, save_workout_log
from services.calculations import calculate_calories_burned
from services.logger import setup_logger, log_user_action

router = Router()
logger = setup_logger()

class WorkoutStates(StatesGroup):
    """Состояния для процесса записи тренировки."""
    WAITING_TYPE = State()
    WAITING_DURATION = State()

def create_workout_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру для выбора типа тренировки.

    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопками типов тренировок
    """
    keyboard = [
        [KeyboardButton(text="Бег")],
        [KeyboardButton(text="Ходьба")],
        [KeyboardButton(text="Велосипед")],
        [KeyboardButton(text="Плавание")],
        [KeyboardButton(text="Силовая")],
        [KeyboardButton(text="Йога")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(Command("log_workout"))
async def cmd_log_workout(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /log_workout.
    Начинает процесс записи тренировки.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    log_user_action(logger, message.from_user.id, "Начал запись тренировки")
    keyboard = create_workout_keyboard()
    await message.answer(
        "Выберите тип тренировки:",
        reply_markup=keyboard
    )
    await state.set_state(WorkoutStates.WAITING_TYPE)

@router.message(WorkoutStates.WAITING_TYPE)
async def process_workout_type(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает выбор типа тренировки.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    workout_types = ["бег", "ходьба", "велосипед", "плавание", "силовая", "йога"]
    
    if message.text.lower() not in workout_types:
        await message.answer(
            "❌ Пожалуйста, выберите тип тренировки, используя кнопки на клавиатуре"
        )
        return

    await state.update_data(workout_type=message.text.lower())
    await message.answer(
        "Введите продолжительность тренировки в минутах (например: 30):",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(WorkoutStates.WAITING_DURATION)

@router.message(WorkoutStates.WAITING_DURATION)
async def process_workout_duration(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод продолжительности тренировки и сохраняет данные.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    try:
        duration = int(message.text)
        if duration <= 0 or duration > 600:
            raise ValueError("Недопустимая продолжительность")

        user_data = await state.get_data()
        user_id = message.from_user.id
        
        user_profile = get_user_data(user_id)
        if not user_profile:
            await message.answer(
                "❌ Пожалуйста, сначала настройте свой профиль с помощью /set_profile"
            )
            await state.clear()
            return

        weight = user_profile[1]
        
        calories_burned = calculate_calories_burned(
            weight=weight,
            duration=duration,
            activity_type=user_data['workout_type']
        )

        save_workout_log(
            user_id=user_id,
            workout_type=user_data['workout_type'],
            duration=duration,
            calories_burned=calories_burned,
            date=datetime.now()
        )

        await message.answer(
            f"✅ Тренировка записана!\n\n"
            f"📊 Статистика:\n"
            f"🔸 Тип: {user_data['workout_type']}\n"
            f"🔸 Продолжительность: {duration} минут\n"
            f"🔸 Сожжено калорий: {calories_burned:.0f} ккал"
        )

        log_user_action(
            logger,
            user_id,
            f"Записал тренировку: {user_data['workout_type']}, {duration} минут"
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите корректную продолжительность "
            "(целое число от 1 до 600 минут)"
        )
    except Exception as e:
        logger.error(f"Ошибка при записи тренировки: {str(e)}")
        await message.answer(
            "❌ Произошла ошибка при записи тренировки.\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )
        await state.clear()
