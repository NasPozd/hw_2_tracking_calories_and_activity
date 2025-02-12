"""
Модуль для обработки команд меню в Telegram боте.
Содержит обработчик команды /menu, который показывает доступные команды.
"""

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from services.logger import setup_logger

router = Router()
logger = setup_logger()

@router.message(Command("menu"))
async def show_menu(message: Message) -> None:
    """
    Обработчик команды /menu.
    Отправляет пользователю текстовое сообщение с доступными командами.

    Args:
        message: Объект сообщения от пользователя
    """
    menu_text = """
🤖 <b>Доступные команды:</b>

📝 Профиль:
/set_profile - Настроить профиль
/weather - Узнать текущую погоду

🏃 Активность:
    /log_workout - Записать тренировку
    Доступные типы: бег, ходьба, велосипед, плавание, силовая, йога

🥗 Питание:
/log_food - Записать прием пищи

💧 Вода:
/log_water - Записать потребление воды

📊 Прогресс:
/check_progress - Проверить текущий прогресс
/view_progress - Посмотреть график прогресса
/get_recommendations - Получить рекомендации по питанию и тренировкам

❓ Помощь:
/menu - Показать это меню
"""
    await message.answer(menu_text)
    logger.info(f"Меню показано пользователю {message.from_user.id}")
