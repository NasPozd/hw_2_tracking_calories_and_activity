"""
Модуль конфигурации для Telegram бота.
Использует pydantic для управления настройками и валидации переменных окружения.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Настройки и конфигурация приложения.
    
    Атрибуты:
        TELEGRAM_TOKEN (str): Токен API Telegram бота
        OPENWEATHER_API_KEY (str): Ключ API OpenWeather
        OPENFOODFACTS_API_URL (str): URL для API OpenFoodFacts
        DB_NAME (str): Путь к файлу базы данных SQLite
    """
    
    TELEGRAM_TOKEN: str
    OPENWEATHER_API_KEY: str
    OPENFOODFACTS_API_URL: str = "https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms"
    DB_NAME: str = "fitness.db/fitness.sqlite"
    
    class Config:
        """Конфигурационный класс Pydantic."""
        env_file = ".env"
        case_sensitive = True


settings = Settings()
