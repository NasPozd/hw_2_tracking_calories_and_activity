"""
Модуль обработки команд для записи потребления воды.
Позволяет пользователям отслеживать потребление воды и получать рекомендации.
"""

from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from database import get_user_data, save_water_log
from services.calculations import calculate_water_norm
from services.weather import get_current_temperature
from services.logger import setup_logger, log_user_action

router = Router()
logger = setup_logger()

class WaterStates(StatesGroup):
    """Состояния для процесса записи потребления воды."""
    WAITING_AMOUNT = State()

def create_water_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с быстрыми вариантами количества воды.

    Returns:
        ReplyKeyboardMarkup: Клавиатура с кнопками объемов воды
    """
    keyboard = [
        [KeyboardButton(text="250 мл"), KeyboardButton(text="500 мл")],
        [KeyboardButton(text="750 мл"), KeyboardButton(text="1000 мл")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

@router.message(Command("log_water"))
async def cmd_log_water(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /log_water.
    Начинает процесс записи потребления воды.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    log_user_action(logger, message.from_user.id, "Начал запись потребления воды")
    
    keyboard = create_water_keyboard()
    await message.answer(
        "Введите количество выпитой воды в миллилитрах "
        "или выберите из предложенных вариантов:",
        reply_markup=keyboard
    )
    await state.set_state(WaterStates.WAITING_AMOUNT)

@router.message(WaterStates.WAITING_AMOUNT)
async def process_water_amount(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод количества выпитой воды и сохраняет данные.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    try:
        amount_text = message.text.split()[0]
        amount = float(amount_text)
        
        if amount <= 0 or amount > 3000:
            raise ValueError("Недопустимое количество воды")

        user_id = message.from_user.id
        
        user_profile = get_user_data(user_id)
        if not user_profile:
            await message.answer(
                "❌ Пожалуйста, сначала настройте свой профиль с помощью /set_profile"
            )
            await state.clear()
            return

        try:
            temperature = await get_current_temperature(user_profile[5])
        except Exception:
            temperature = 20

        daily_norm = calculate_water_norm(
            weight=user_profile[1],
            activity_min=30 * user_profile[4],
            temperature=temperature
        )

        save_water_log(user_id, amount, datetime.now())

        progress_message = (
            f"✅ Вода записана!\n\n"
            f"📊 Статистика:\n"
            f"🔸 Добавлено: {amount:.0f} мл\n"
            f"🔸 Дневная норма: {daily_norm:.0f} мл\n"
            # f"🔸 Всего за сегодня: {total_today:.0f} мл\n"
            # f"🔸 Осталось до нормы: {remaining:.0f} мл"
        )

        await message.answer(
            progress_message,
            reply_markup=ReplyKeyboardRemove()
        )

        log_user_action(
            logger,
            user_id,
            f"Записал потребление воды: {amount:.0f} мл"
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите корректное количество воды "
            "(число от 1 до 3000 мл)"
        )
    except Exception as e:
        logger.error(f"Ошибка при записи потребления воды: {str(e)}")
        await message.answer(
            "❌ Произошла ошибка при записи потребления воды.\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )
        await state.clear()
