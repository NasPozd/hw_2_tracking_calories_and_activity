"""
Модуль базы данных для Telegram бота.
Обрабатывает все операции с базой данных, включая инициализацию,
создание таблиц и доступ к данным.
"""

import sqlite3
import os
from typing import Dict, Optional, Tuple, Any
from datetime import datetime

from config import settings
from services.logger import setup_logger

logger = setup_logger()

def ensure_db_directory() -> None:
    """
    Проверяет существование директории базы данных.
    Создает директорию, если она не существует.
    """
    db_dir = os.path.dirname(settings.DB_NAME)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"Создана директория для базы данных: {db_dir}")


def create_users_table() -> None:
    """
    Создает таблицу пользователей, если она не существует.
    Хранит информацию профиля пользователя, включая физические параметры и цели.
    """
    try:
        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    weight REAL,
                    height REAL,
                    age INTEGER,
                    activity INTEGER,
                    city TEXT,
                    calorie_goal REAL,
                    water_goal REAL
                )
            ''')
            conn.commit()
            logger.info("Таблица users успешно создана или уже существует")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при создании таблицы users: {str(e)}")
        raise


def create_food_logs_table() -> None:
    """
    Создает таблицу журнала питания, если она не существует.
    Хранит записи о приеме пищи пользователя с информацией о питательности.
    """
    try:
        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS food_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    product_name TEXT,
                    calories REAL,
                    amount REAL,
                    date DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            conn.commit()
            logger.info("Таблица food_logs успешно создана или уже существует")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при создании таблицы food_logs: {str(e)}")
        raise


def create_water_logs_table() -> None:
    """
    Создает таблицу журнала потребления воды, если она не существует.
    Хранит записи о потреблении воды пользователем.
    """
    try:
        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS water_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    date DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            conn.commit()
            logger.info("Таблица water_logs успешно создана или уже существует")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при создании таблицы water_logs: {str(e)}")
        raise


def create_workout_logs_table() -> None:
    """
    Создает таблицу журнала тренировок, если она не существует.
    Хранит записи о тренировках пользователя, включая тип, продолжительность
    и потраченные калории.
    """
    try:
        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workout_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    workout_type TEXT,
                    duration INTEGER,
                    calories_burned REAL,
                    date DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            conn.commit()
            logger.info("Таблица workout_logs успешно создана или уже существует")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при создании таблицы workout_logs: {str(e)}")
        raise


def update_user(user_data: Dict[str, Any]) -> None:
    """
    Обновляет или добавляет данные профиля пользователя.

    Аргументы:
        user_data: Словарь, содержащий информацию профиля пользователя
            Обязательные ключи: user_id, weight, height, age, activity,
                              city, calorie_goal, water_goal
    
    Raises:
        sqlite3.Error: Если операция с базой данных не удалась
    """
    try:
        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users (
                    user_id,
                    weight,
                    height,
                    age,
                    activity,
                    city,
                    calorie_goal,
                    water_goal
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['user_id'],
                user_data['weight'],
                user_data['height'],
                user_data['age'],
                user_data['activity'],
                user_data['city'],
                user_data['calorie_goal'],
                user_data['water_goal']
            ))
            conn.commit()
            logger.info(f"Обновлены данные пользователя {user_data['user_id']}")
    except sqlite3.Error as e:
        error_msg = f"Не удалось обновить данные пользователя: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def get_user_city(user_id: int) -> Optional[str]:
    """
    Получает город пользователя.

    Args:
        user_id: ID пользователя Telegram

    Returns:
        str или None: Город пользователя, если найден, иначе None
    
    Raises:
        Exception: При ошибке работы с БД
    """
    try:
        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT city FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                logger.info(f"Получен город пользователя {user_id}: {result[0]}")
            else:
                logger.warning(f"Город не найден для пользователя {user_id}")
            return result[0] if result else None
    except sqlite3.Error as e:
        error_msg = f"Не удалось получить город пользователя: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def get_user_data(user_id: int) -> Optional[Tuple]:
    """
    Получает все данные профиля пользователя.

    Args:
        user_id: ID пользователя Telegram

    Returns:
        tuple или None: Данные профиля пользователя, если найдены, иначе None
    
    Raises:
        Exception: При ошибке работы с БД
    """
    try:
        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            if result:
                logger.info(f"Получены данные пользователя {user_id}")
            else:
                logger.warning(f"Данные не найдены для пользователя {user_id}")
            return result
    except sqlite3.Error as e:
        error_msg = f"Не удалось получить данные пользователя: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def get_daily_progress(date: datetime) -> Optional[Tuple]:
    """
    Получает ежедневный прогресс пользователя за определенную дату.

    Args:
        date: Дата, за которую нужно получить прогресс

    Returns:
        tuple или None: Данные о прогрессе за день, если найдены, иначе None
            (потребление воды, потребленные калории, сожженные калории)
    
    Raises:
        Exception: При ошибке работы с БД
    """
    try:
        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    water_intake,
                    calories_consumed,
                    calories_burned
                FROM daily_progress
                WHERE date = ?
            """, (date,))
            result = cursor.fetchone()
            if result:
                logger.info(f"Получен прогресс за {date}")
            else:
                logger.info(f"Прогресс не найден за {date}")
            return result
    except sqlite3.Error as e:
        error_msg = f"Не удалось получить ежедневный прогресс: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def save_water_log(
    user_id: int,
    amount: float,
    date: datetime
) -> None:
    """
    Сохраняет запись о потреблении воды.

    Args:
        user_id: ID пользователя
        amount: Количество выпитой воды в мл
        date: Дата и время записи
    
    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    try:
        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO water_logs (user_id, amount, date)
                VALUES (?, ?, ?)
            """, (user_id, amount, date))
            conn.commit()
            logger.info(f"Сохранена запись о воде для пользователя {user_id}: {amount}мл")
    except sqlite3.Error as e:
        error_msg = f"Ошибка при сохранении записи о воде: {str(e)}"
        logger.error(error_msg)
        raise


def save_food_log(
    user_id: int,
    product_name: str,
    amount: float,
    calories: float,
    date: datetime
) -> None:
    """
    Сохраняет запись о приеме пищи.

    Args:
        user_id: ID пользователя
        product_name: Название продукта
        amount: Количество в граммах
        calories: Количество калорий
        date: Дата и время записи
    
    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    try:
        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO food_logs (
                    user_id,
                    product_name,
                    amount,
                    calories,
                    date
                )
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, product_name, amount, calories, date))
            conn.commit()
            logger.info(
                f"Сохранена запись о еде для пользователя {user_id}: "
                f"{product_name}, {amount}г, {calories}ккал"
            )
    except sqlite3.Error as e:
        error_msg = f"Ошибка при сохранении записи о еде: {str(e)}"
        logger.error(error_msg)
        raise


def save_workout_log(
    user_id: int,
    workout_type: str,
    duration: int,
    calories_burned: float,
    date: datetime
) -> None:
    """
    Сохраняет запись о тренировке.

    Args:
        user_id: ID пользователя
        workout_type: Тип тренировки
        duration: Продолжительность в минутах
        calories_burned: Сожженные калории
        date: Дата и время записи
    
    Raises:
        sqlite3.Error: При ошибке работы с БД
    """
    try:
        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO workout_logs (
                    user_id,
                    workout_type,
                    duration,
                    calories_burned,
                    date
                )
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, workout_type, duration, calories_burned, date))
            conn.commit()
            logger.info(
                f"Сохранена запись о тренировке для пользователя {user_id}: "
                f"{workout_type}, {duration}мин, {calories_burned}ккал"
            )
    except sqlite3.Error as e:
        error_msg = f"Ошибка при сохранении записи о тренировке: {str(e)}"
        logger.error(error_msg)
        raise


def init_db() -> None:
    """
    Инициализирует базу данных, создавая все необходимые таблицы.
    Должна вызываться при запуске приложения.
    """
    logger.info("Начало инициализации базы данных")
    ensure_db_directory()
    create_users_table()
    create_food_logs_table()
    create_water_logs_table()
    create_workout_logs_table()
    logger.info("База данных успешно инициализирована")
