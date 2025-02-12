"""
Модуль обработки команд для записи еды.
Позволяет пользователям логировать потребление приемов пищи.
"""

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import aiohttp
from datetime import datetime
import json

from config import settings
from database import save_food_log
from services.logger import setup_logger, log_user_action

router = Router()
logger = setup_logger()

class FoodStates(StatesGroup):
    """Состояния для процесса записи еды."""
    WAITING_PRODUCT = State()
    WAITING_AMOUNT = State()
    CONFIRM_FOOD = State()

async def search_food_product(product_name: str) -> dict:
    """
    Ищет информацию о продукте в базе OpenFoodFacts.

    Args:
        product_name: Название продукта для поиска

    Returns:
        dict: Информация о продукте или None, если продукт не найден

    Raises:
        aiohttp.ClientError: При ошибке запроса к API
        json.JSONDecodeError: При ошибке парсинга ответа
    """
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{settings.OPENFOODFACTS_API_URL}={product_name}&json=true"
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"API вернул статус {response.status}")
                    return None
                    
                data = await response.json()
                if not data.get('products'):
                    return None
                    
                product = data['products'][0]
                return {
                    'name': product.get('product_name', 'Неизвестный продукт'),
                    'calories': float(product.get('nutriments', {}).get('energy-kcal', 0)),
                    'proteins': float(product.get('nutriments', {}).get('proteins', 0)),
                    'fats': float(product.get('nutriments', {}).get('fat', 0)),
                    'carbs': float(product.get('nutriments', {}).get('carbohydrates', 0))
                }
                
    except (aiohttp.ClientError, json.JSONDecodeError) as e:
        logger.error(f"Ошибка при поиске продукта: {str(e)}")
        return None

@router.message(Command("log_food"))
async def cmd_log_food(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /log_food.
    Начинает процесс записи еды.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    log_user_action(logger, message.from_user.id, "Начал запись еды")
    
    await message.answer(
        "Введите название продукта или блюда:"
    )
    await state.set_state(FoodStates.WAITING_PRODUCT)

@router.message(FoodStates.WAITING_PRODUCT)
async def process_food_name(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод названия продукта.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    product_name = message.text.strip()
    if len(product_name) < 2:
        await message.answer(
            "❌ Название продукта должно содержать минимум 2 символа"
        )
        return

    product_info = await search_food_product(product_name)
    if not product_info:
        await message.answer(
            "❌ Продукт не найден в базе данных.\n"
            "Пожалуйста, попробуйте другой продукт или уточните название."
        )
        return

    await state.update_data(
        product_name=product_info['name'],
        calories_per_100=product_info['calories']
    )
    
    await message.answer(
        f"Найден продукт: {product_info['name']}\n"
        f"Калорийность: {product_info['calories']:.0f} ккал/100г\n\n"
        f"Введите количество в граммах:"
    )
    await state.set_state(FoodStates.WAITING_AMOUNT)

@router.message(FoodStates.WAITING_AMOUNT)
async def process_food_amount(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает ввод количества продукта и сохраняет данные.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    try:
        amount = float(message.text)
        if amount <= 0 or amount > 2000:
            raise ValueError("Недопустимое количество")

        user_data = await state.get_data()
        calories = (amount / 100) * user_data['calories_per_100']

        save_food_log(
            user_id=message.from_user.id,
            product_name=user_data['product_name'],
            amount=amount,
            calories=calories,
            date=datetime.now()
        )

        await message.answer(
            f"✅ Прием пищи записан!\n\n"
            f"📊 Статистика:\n"
            f"🔸 Продукт: {user_data['product_name']}\n"
            f"🔸 Количество: {amount:.0f} г\n"
            f"🔸 Калории: {calories:.0f} ккал"
        )

        log_user_action(
            logger,
            message.from_user.id,
            f"Записал прием пищи: {user_data['product_name']}, {amount:.0f}г"
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите корректное количество "
            "(число от 1 до 2000 грамм)"
        )
    except Exception as e:
        logger.error(f"Ошибка при записи приема пищи: {str(e)}")
        await message.answer(
            "❌ Произошла ошибка при записи приема пищи.\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )
        await state.clear()
