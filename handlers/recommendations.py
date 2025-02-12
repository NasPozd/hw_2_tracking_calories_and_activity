"""
Модуль обработки команд для получения рекомендаций.
Предоставляет персонализированные рекомендации по питанию и тренировкам.
"""

from aiogram import Router, types
from aiogram.filters import Command
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

from config import settings
from database import get_user_data
from services.calculations import calculate_bmi
from services.weather import get_current_temperature
from services.logger import setup_logger, log_user_action

router = Router()
logger = setup_logger()

async def get_activity_stats(user_id: int, days: int = 7) -> Dict[str, float]:
    """
    Получает статистику активности пользователя за период.

    Args:
        user_id: ID пользователя
        days: Количество дней для анализа

    Returns:
        Dict[str, float]: Статистика активности:
            - avg_calories: среднее потребление калорий
            - avg_water: среднее потребление воды
            - avg_workouts: среднее количество тренировок
    """
    try:
        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()
            date_from = datetime.now() - timedelta(days=days)

            cursor.execute("""
                SELECT AVG(calories)
                FROM food_logs
                WHERE user_id = ? AND date >= ?
            """, (user_id, date_from))
            avg_calories = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT AVG(amount)
                FROM water_logs
                WHERE user_id = ? AND date >= ?
            """, (user_id, date_from))
            avg_water = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT COUNT(*) / ?
                FROM workout_logs
                WHERE user_id = ? AND date >= ?
            """, (days, user_id, date_from))
            avg_workouts = cursor.fetchone()[0] or 0

            return {
                'avg_calories': float(avg_calories),
                'avg_water': float(avg_water),
                'avg_workouts': float(avg_workouts)
            }

    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении статистики активности: {str(e)}")
        raise

def get_workout_recommendations(
    bmi: float,
    avg_workouts: float,
    temperature: float
) -> str:
    """
    Формирует рекомендации по тренировкам.

    Args:
        bmi: Индекс массы тела
        avg_workouts: Среднее количество тренировок в неделю
        temperature: Текущая температура

    Returns:
        str: Текст рекомендаций
    """
    recommendations = []

    if avg_workouts < 1:
        recommendations.append(
            "🎯 Рекомендуется начать с 2-3 легких тренировок в неделю"
        )
    elif avg_workouts < 3:
        recommendations.append(
            "🎯 Можно увеличить количество тренировок до 3-4 раз в неделю"
        )
    else:
        recommendations.append(
            "👍 Отличная регулярность тренировок! Продолжайте в том же духе"
        )

    if bmi < 18.5:
        recommendations.append(
            "💪 Рекомендуются силовые тренировки для набора мышечной массы"
        )
    elif bmi > 25:
        recommendations.append(
            "🏃 Рекомендуются кардио тренировки для снижения веса"
        )
    else:
        recommendations.append(
            "🔄 Рекомендуется сочетать кардио и силовые тренировки"
        )

    if temperature > 30:
        recommendations.append(
            "🌡 Из-за высокой температуры рекомендуются тренировки в помещении "
            "или ранним утром/поздним вечером"
        )
    elif temperature < 0:
        recommendations.append(
            "❄️ При низкой температуре уделите особое внимание разминке"
        )

    return "\n".join(recommendations)

def get_nutrition_recommendations(
    bmi: float,
    avg_calories: float,
    calorie_goal: float
) -> str:
    """
    Формирует рекомендации по питанию.

    Args:
        bmi: Индекс массы тела
        avg_calories: Среднее потребление калорий
        calorie_goal: Целевое потребление калорий

    Returns:
        str: Текст рекомендаций
    """
    recommendations = []

    calorie_diff = avg_calories - calorie_goal
    if abs(calorie_diff) > 300:
        if calorie_diff > 0:
            recommendations.append(
                "⚠️ Вы превышаете целевую калорийность. "
                "Попробуйте уменьшить порции или выбирать менее калорийные продукты"
            )
        else:
            recommendations.append(
                "⚠️ Вы недобираете калории. "
                "Старайтесь есть более питательную пищу и не пропускать приемы пищи"
            )
    else:
        recommendations.append(
            "👍 Ваше потребление калорий близко к целевому. Так держать!"
        )

    if bmi < 18.5:
        recommendations.append(
            "🥑 Включите в рацион больше белковой пищи и полезных жиров"
        )
    elif bmi > 25:
        recommendations.append(
            "🥗 Отдавайте предпочтение овощам и нежирным источникам белка"
        )
    else:
        recommendations.append(
            "🥗 Поддерживайте разнообразный и сбалансированный рацион"
        )

    return "\n".join(recommendations)

@router.message(Command("get_recommendations"))
async def cmd_get_recommendations(message: types.Message) -> None:
    """
    Обработчик команды /get_recommendations.
    Формирует и отправляет персонализированные рекомендации.

    Args:
        message: Объект сообщения от пользователя
    """
    try:
        user_id = message.from_user.id
        log_user_action(logger, user_id, "Запросил рекомендации")

        user_profile = get_user_data(user_id)
        if not user_profile:
            await message.answer(
                "❌ Пожалуйста, сначала настройте свой профиль с помощью /set_profile"
            )
            return

        activity_stats = await get_activity_stats(user_id)
        
        try:
            temperature = await get_current_temperature(user_profile[5])
        except Exception:
            temperature = 20

        bmi, bmi_category = calculate_bmi(user_profile[1], user_profile[2])

        workout_recs = get_workout_recommendations(
            bmi,
            activity_stats['avg_workouts'],
            temperature
        )
        
        nutrition_recs = get_nutrition_recommendations(
            bmi,
            activity_stats['avg_calories'],
            user_profile[6]
        )

        recommendations_message = (
            "🎯 Персональные рекомендации:\n\n"
            f"📊 Ваш ИМТ: {bmi:.1f} ({bmi_category})\n\n"
            f"🏋️ Тренировки:\n{workout_recs}\n\n"
            f"🍎 Питание:\n{nutrition_recs}"
        )

        await message.answer(recommendations_message)
        logger.info(f"Рекомендации отправлены пользователю {user_id}")

    except Exception as e:
        logger.error(f"Ошибка при формировании рекомендаций: {str(e)}")
        await message.answer(
            "❌ Произошла ошибка при формировании рекомендаций.\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )
