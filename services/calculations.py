"""
Модуль для расчетов различных показателей здоровья и фитнеса.
Содержит функции для расчета норм воды, калорий и других параметров.
"""

from typing import Tuple
from services.logger import setup_logger

logger = setup_logger()

def calculate_water_norm(
    weight: float,
    activity_min: int,
    temperature: float
) -> float:
    """
    Рассчитывает дневную норму потребления воды.

    Учитывает:
    - Базовую потребность в воде на основе веса
    - Дополнительную потребность от физической активности
    - Корректировку на основе температуры окружающей среды

    Args:
        weight: Вес пользователя в кг
        activity_min: Длительность физической активности в минутах
        temperature: Температура окружающей среды в градусах Цельсия

    Returns:
        float: Рекомендуемое количество воды в мл
    """
    try:
        base = weight * 30
        
        activity_add = (activity_min // 30) * 250
        temp_add = max(0, ((temperature - 20) // 5) * 200)
        
        total = base + activity_add + temp_add
        logger.info(f"Рассчитана норма воды: {total}мл (базовая:{base}, "
                   f"активность:{activity_add}, температура:{temp_add})")
        
        return total
        
    except Exception as e:
        logger.error(f"Ошибка при расчете нормы воды: {str(e)}")
        raise

def calculate_calories_burned(
    weight: float,
    duration: int,
    activity_type: str
) -> float:
    """
    Рассчитывает количество сожженных калорий за тренировку.

    Args:
        weight: Вес пользователя в кг
        duration: Продолжительность тренировки в минутах
        activity_type: Тип активности (бег, ходьба, велосипед и т.д.)

    Returns:
        float: Количество сожженных калорий
    """
    met_values = {
        'бег': 8.0,
        'ходьба': 3.5,
        'велосипед': 7.0,
        'плавание': 6.0,
        'силовая': 5.0,
        'йога': 3.0
    }
    
    try:
        met = met_values.get(activity_type.lower(), 4.0)
        hours = duration / 60
        calories = met * weight * hours
        
        logger.info(f"Рассчитаны калории: {calories}ккал "
                   f"(активность:{activity_type}, МЕТ:{met})")
        
        return round(calories, 2)
        
    except Exception as e:
        logger.error(f"Ошибка при расчете калорий: {str(e)}")
        raise

def calculate_bmi(weight: float, height: float) -> Tuple[float, str]:
    """
    Рассчитывает индекс массы тела (ИМТ) и определяет категорию.

    Args:
        weight: Вес в кг
        height: Рост в см

    Returns:
        Tuple[float, str]: (значение ИМТ, категория)
    """
    try:
        height_m = height / 100
        bmi = weight / (height_m * height_m)
        
        if bmi < 18.5:
            category = "недостаточный вес"
        elif bmi < 25:
            category = "нормальный вес"
        elif bmi < 30:
            category = "избыточный вес"
        else:
            category = "ожирение"
            
        logger.info(f"Рассчитан ИМТ: {bmi:.1f} ({category})")
        return round(bmi, 1), category
        
    except Exception as e:
        logger.error(f"Ошибка при расчете ИМТ: {str(e)}")
        raise

def calculate_daily_calories(
    weight: float,
    height: float,
    age: int,
    activity_level: int,
    goal: str = "maintain"
) -> float:
    """
    Рассчитывает дневную норму калорий с учетом цели.

    Args:
        weight: Вес в кг
        height: Рост в см
        age: Возраст в годах
        activity_level: Уровень активности (1-5)
        goal: Цель ('lose' - похудение, 'maintain' - поддержание, 'gain' - набор)

    Returns:
        float: Рекомендуемое количество калорий в день
    """
    try:
        bmr = (10 * weight) + (6.25 * height) - (5 * age)
        
        activity_factors = {
            1: 1.2,
            2: 1.375,
            3: 1.55,
            4: 1.725,
            5: 1.9
        }
        
        factor = activity_factors.get(activity_level, 1.2)
        tdee = bmr * factor
        
        if goal == "lose":
            calories = tdee - 500
        elif goal == "gain":
            calories = tdee + 500
        else:
            calories = tdee
            
        logger.info(f"Рассчитаны дневные калории: {calories:.0f}ккал "
                   f"(БОВ:{bmr:.0f}, активность:{factor}, цель:{goal})")
        
        return round(calories)
        
    except Exception as e:
        logger.error(f"Ошибка при расчете дневных калорий: {str(e)}")
        raise
