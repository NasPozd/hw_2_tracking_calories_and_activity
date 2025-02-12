"""
Пакет обработчиков команд для Telegram бота.
Объединяет все маршрутизаторы команд в единый роутер.
"""

from aiogram import Router
from typing import List

from .menu import router as menu_router
from .recommendations import router as recommendations_router
from .profile import router as profile_router
from .water import router as water_router
from .food import router as food_router
from .workout import router as workout_router
from .progress import router as progress_router
from .weather import router as weather_router

# Создаем основной роутер
router = Router()

def setup_routers() -> Router:
    """
    Настраивает и объединяет все роутеры команд.
    
    Returns:
        Router: Основной роутер с включенными подроутерами
    """
    # Список всех роутеров в порядке приоритета
    routers: List[Router] = [
        menu_router,          # Базовые команды меню
        profile_router,       # Команды профиля
        water_router,         # Команды учета воды
        food_router,         # Команды учета питания
        workout_router,      # Команды учета тренировок
        progress_router,     # Команды просмотра прогресса
        recommendations_router,  # Команды рекомендаций
        weather_router,      # Команды погоды
    ]

    # Включаем все роутеры в основной
    for router_item in routers:
        router.include_router(router_item)

    return router

# Инициализируем роутеры при импорте пакета
router = setup_routers()

# Экспортируем только основной роутер
__all__ = ['router']
