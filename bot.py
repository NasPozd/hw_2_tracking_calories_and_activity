"""
Основной модуль Telegram бота.
Обрабатывает инициализацию бота и маршрутизацию команд/сообщений.
"""

import logging
import asyncio
from typing import List

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers import router
from config import settings
from database import init_db
from services.logger import setup_logger


def setup_bot_commands() -> List[types.BotCommand]:
    """
    Создает список команд бота с описаниями.
    
    Returns:
        List[types.BotCommand]: Список команд бота
    """
    return [
        types.BotCommand(command="menu", description="Показать меню команд"),
        types.BotCommand(command="set_profile", description="Настроить профиль"),
        types.BotCommand(command="log_workout", description="Записать тренировку"),
        types.BotCommand(command="log_food", description="Записать прием пищи"),
        types.BotCommand(command="log_water", description="Записать потребление воды"),
        types.BotCommand(command="check_progress", description="Проверить текущий прогресс"),
        types.BotCommand(command="view_progress", description="Посмотреть график прогресса"),
        types.BotCommand(command="weather", description="Узнать текущую погоду"),
        types.BotCommand(command="get_recommendations", 
                        description="Получить рекомендации по питанию и тренировкам")
    ]


async def main() -> None:
    """
    Основная функция запуска бота.
    Настраивает логирование, инициализирует базу данных и запускает бота.
    """
    logger = setup_logger()
    logger.info("Бот запускается...")

    try:
        init_db()
        
        bot = Bot(
            token=settings.TELEGRAM_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        dp = Dispatcher()
        dp.include_router(router)
        
        await bot.set_my_commands(setup_bot_commands())
        
        logger.info("Бот успешно запущен и готов к работе")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Произошла ошибка при запуске бота: {e}")
        raise


if __name__ == "__main__":
    try:
        if not asyncio.get_event_loop().is_running():
            asyncio.run(main())
        else:
            logging.info("Event loop уже запущен. Останавливаем все процессы.")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        logging.error("Выключаем бота.")
