"""
Модуль для работы с API OpenWeather.
Предоставляет функции для получения текущей погоды.
"""

import requests
from typing import Dict, Union
from config import settings

class WeatherServiceError(Exception):
    """Базовый класс для исключений сервиса погоды."""
    pass

class WeatherAPIError(WeatherServiceError):
    """Исключение при ошибках API погоды."""
    pass

class CityNotFoundError(WeatherServiceError):
    """Исключение, когда город не найден."""
    pass

async def get_current_temperature(city: str) -> float:
    """
    Получает текущую температуру для указанного города.

    Args:
        city: Название города

    Returns:
        float: Текущая температура в градусах Цельсия

    Raises:
        CityNotFoundError: Если город не найден
        WeatherAPIError: При ошибках API
        WeatherServiceError: При других ошибках сервиса
    """
    try:
        url = (f"http://api.openweathermap.org/data/2.5/weather"
               f"?q={city}&appid={settings.OPENWEATHER_API_KEY}&units=metric")
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        if response.status_code == 404:
            raise CityNotFoundError(f"Город {city} не найден")
            
        return float(data['main']['temp'])
        
    except requests.exceptions.RequestException as e:
        raise WeatherAPIError(f"Ошибка при запросе к API погоды: {str(e)}")
    except (KeyError, ValueError) as e:
        raise WeatherServiceError(f"Ошибка при обработке данных погоды: {str(e)}")

async def get_weather_details(city: str) -> Dict[str, Union[float, str]]:
    """
    Получает детальную информацию о погоде для указанного города.

    Args:
        city: Название города

    Returns:
        Dict с информацией о погоде:
            - temperature: температура в °C
            - description: описание погоды
            - humidity: влажность в %
            - wind_speed: скорость ветра в м/с

    Raises:
        CityNotFoundError: Если город не найден
        WeatherAPIError: При ошибках API
        WeatherServiceError: При других ошибках сервиса
    """
    try:
        url = (f"http://api.openweathermap.org/data/2.5/weather"
               f"?q={city}&appid={settings.OPENWEATHER_API_KEY}&units=metric&lang=ru")
        
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        if response.status_code == 404:
            raise CityNotFoundError(f"Город {city} не найден")
            
        return {
            'temperature': float(data['main']['temp']),
            'description': data['weather'][0]['description'],
            'humidity': float(data['main']['humidity']),
            'wind_speed': float(data['wind']['speed'])
        }
        
    except requests.exceptions.RequestException as e:
        raise WeatherAPIError(f"Ошибка при запросе к API погоды: {str(e)}")
    except (KeyError, ValueError) as e:
        raise WeatherServiceError(f"Ошибка при обработке данных погоды: {str(e)}")

def format_weather_message(weather_data: Dict[str, Union[float, str]]) -> str:
    """
    Форматирует данные о погоде в читаемое сообщение.

    Args:
        weather_data: Словарь с данными о погоде

    Returns:
        str: Отформатированное сообщение о погоде
    """
    return (
        f"🌡 Температура: {weather_data['temperature']}°C\n"
        f"☁️ Погода: {weather_data['description']}\n"
        f"💧 Влажность: {weather_data['humidity']}%\n"
        f"💨 Скорость ветра: {weather_data['wind_speed']} м/с"
    )
