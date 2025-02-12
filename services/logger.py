"""
Модуль настройки логирования для Telegram бота.
Предоставляет централизованную конфигурацию логирования для всего приложения.
"""

import logging
import os
from typing import Optional
from datetime import datetime


def setup_logger(log_level: int = logging.INFO) -> logging.Logger:
    """
    Настраивает и возвращает логгер для приложения.
    
    Создает логгер с настроенным форматированием и обработчиками для
    вывода в консоль и файл. Гарантирует, что обработчики добавляются
    только один раз.

    Args:
        log_level: Уровень логирования (по умолчанию logging.INFO)
    
    Returns:
        logging.Logger: Настроенный логгер
    """
    logger = logging.getLogger('HW2_TG_BOT')
    logger.setLevel(log_level)

    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        log_file_path = 'app.log'
        ensure_log_directory(log_file_path)
        
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)

        logger.info("Логгер успешно инициализирован")

    return logger


def ensure_log_directory(log_file_path: str) -> None:
    """
    Проверяет и создает директорию для файла логов, если она не существует.

    Args:
        log_file_path: Путь к файлу логов
    """
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)


def log_error(logger: logging.Logger, error: Exception, context: Optional[str] = None) -> None:
    """
    Логирует информацию об ошибке с дополнительным контекстом.

    Args:
        logger: Настроенный логгер
        error: Объект исключения
        context: Дополнительный контекст ошибки (опционально)
    """
    error_message = f"Ошибка: {str(error)}"
    if context:
        error_message = f"{context}: {error_message}"
    
    logger.error(error_message, exc_info=True)


def log_user_action(logger: logging.Logger, user_id: int, action: str) -> None:
    """
    Логирует действие пользователя.

    Args:
        logger: Настроенный логгер
        user_id: ID пользователя в Telegram
        action: Описание действия пользователя
    """
    logger.info(f"Пользователь {user_id}: {action}")
