"""
Модуль обработки команд погоды в Telegram боте.
Предоставляет функционал для получения информации о погоде.
"""

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from services.weather import (
    get_weather_details,
    format_weather_message,
    WeatherServiceError,
    CityNotFoundError
)
from database import get_user_city
from services.logger import setup_logger, log_user_action

router = Router()
logger = setup_logger()

@router.message(Command("weather"))
async def show_weather(message: Message) -> None:
    """
    Обработчик команды /weather.
    Показывает текущую погоду для города пользователя.

    Если город не установлен в профиле, предлагает его установить.
    При возникновении ошибок отправляет пользователю понятное сообщение.

    Args:
        message: Объект сообщения от пользователя
    """
    try:
        user_id = message.from_user.id
        log_user_action(logger, user_id, "Запросил погоду")

        city = get_user_city(user_id)
        
        if not city:
            await message.answer(
                "⚠️ Город не установлен!\n\n"
                "Пожалуйста, установите город в профиле с помощью команды /set_profile"
            )
            logger.warning(f"Пользователь {user_id} запросил погоду без установленного города")
            return

        weather_data = await get_weather_details(city)
        
        weather_message = (
            f"🌍 Погода в городе {city}:\n\n"
            f"{format_weather_message(weather_data)}"
        )
        
        await message.answer(weather_message)
        logger.info(f"Погода успешно отправлена пользователю {user_id} для города {city}")

    except CityNotFoundError:
        error_message = (
            "❌ Город не найден!\n\n"
            "Пожалуйста, проверьте правильность названия города "
            "в профиле и попробуйте снова."
        )
        await message.answer(error_message)
        logger.error(f"Город не найден для пользователя {user_id}: {city}")

    except WeatherServiceError as e:
        error_message = (
            "❌ Извините, произошла ошибка при получении данных о погоде.\n"
            "Пожалуйста, попробуйте позже."
        )
        await message.answer(error_message)
        logger.error(f"Ошибка погодного сервиса для пользователя {user_id}: {str(e)}")

    except Exception as e:
        error_message = (
            "❌ Произошла непредвиденная ошибка.\n"
            "Пожалуйста, попробуйте позже."
        )
        await message.answer(error_message)
        logger.error(f"Непредвиденная ошибка для пользователя {user_id}: {str(e)}")
