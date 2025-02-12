"""
Модуль обработки команд для отслеживания прогресса.
Позволяет пользователям просматривать статистику потребления воды, калорий и физической активности.
"""

import io
import sqlite3
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from config import settings
from services.logger import setup_logger

router = Router()
logger = setup_logger()


class ProgressStates(StatesGroup):
    """
    Состояния для процесса просмотра прогресса.
    
    States:
        waiting_for_days: Ожидание ввода количества дней для отображения статистики
    """
    waiting_for_days = State()


@router.message(Command("view_progress"))
async def view_progress(message: Message, state: FSMContext):
    """
    Обработчик команды /view_progress.
    Начинает процесс просмотра прогресса за определенный период.

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    await message.answer("За какой период хотите отобразить прогресс? (введите количество дней)")
    await state.set_state(ProgressStates.waiting_for_days)


@router.message(ProgressStates.waiting_for_days)
async def process_days(message: Message, state: FSMContext):
    """
    Обрабатывает ввод количества дней и создает график прогресса.
    
    Создает визуализацию прогресса пользователя, включая:
    - Потребление калорий
    - Сожженные калории
    - Потребление воды

    Args:
        message: Объект сообщения от пользователя
        state: Объект для управления состоянием диалога
    """
    try:
        days = int(message.text)
        if days <= 0:
            await message.answer("Пожалуйста, введите положительное число дней.")
            return

        user_id = message.from_user.id
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)

        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()
            dates, calories_consumed, calories_burned, water_intake = [], [], [], []
            
            current_date = start_date
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                dates.append(current_date)

                cursor.execute("""
                    SELECT COALESCE(SUM(calories), 0) 
                    FROM food_logs 
                    WHERE user_id = ? 
                    AND strftime('%Y-%m-%d', date) = ?
                """, (user_id, date_str))
                calories_consumed.append(cursor.fetchone()[0])

                cursor.execute("""
                    SELECT COALESCE(SUM(calories_burned), 0) 
                    FROM workout_logs 
                    WHERE user_id = ? 
                    AND strftime('%Y-%m-%d', date) = ?
                """, (user_id, date_str))
                calories_burned.append(cursor.fetchone()[0])

                cursor.execute("""
                    SELECT COALESCE(SUM(amount), 0) 
                    FROM water_logs 
                    WHERE user_id = ? 
                    AND strftime('%Y-%m-%d', date) = ?
                """, (user_id, date_str))
                water_intake.append(cursor.fetchone()[0] / 1000)

                current_date += timedelta(days=1)

            if not any(calories_consumed) and not any(calories_burned) and not any(water_intake):
                await message.answer("За выбранный период нет данных для отображения.")
                await state.clear()
                return

            fig, ax1 = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('white')
            ax1.set_facecolor('white')
            ax2 = ax1.twinx()

            ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d.%m'))
            ax1.xaxis.set_major_locator(plt.matplotlib.dates.DayLocator())

            ax1.plot(dates, calories_consumed, '-o', 
                    label='Потребленные калории', 
                    linewidth=2, color='#FF6B6B', markersize=6)
            ax1.plot(dates, calories_burned, '-s', 
                    label='Сожженные калории', 
                    linewidth=2, color='#4ECDC4', markersize=6)
            ax2.plot(dates, water_intake, '-^', 
                    label='Вода (л)', 
                    linewidth=2, color='#45B7D1', markersize=6)

            ax1.set_ylabel('Калории (ккал)', color='#333333', fontsize=12, labelpad=10)
            ax2.set_ylabel('Вода (л)', color='#45B7D1', fontsize=12, labelpad=10)
            ax1.set_xlabel('Дата', labelpad=10, fontsize=12)

            ax1.set_title(f'Прогресс за последние {days} дней', 
                         pad=20, fontsize=14, fontweight='bold')
            ax1.grid(True, linestyle='--', alpha=0.3, color='gray')

            ax1.tick_params(axis='x', rotation=45, labelsize=10)
            ax1.tick_params(axis='y', labelsize=10)
            ax2.tick_params(axis='y', labelsize=10)
            plt.xticks(dates)

            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2,
                      bbox_to_anchor=(0.5, -0.2), loc='upper center', ncol=3,
                      fontsize=10, frameon=True, facecolor='white', edgecolor='gray')

            plt.subplots_adjust(bottom=0.2, right=0.9)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plt.close()

            await message.answer_photo(
                types.BufferedInputFile(
                    buf.getvalue(),
                    filename="progress.png"
                ),
                caption=f"📊 Ваш прогресс за последние {days} дней"
            )

        await state.clear()

    except ValueError:
        await message.answer("Пожалуйста, введите корректное число дней.")
    except Exception as e:
        logger.error(f"Error in process_days: {str(e)}")
        await message.answer("Произошла ошибка при создании графика. Попробуйте позже.")
        await state.clear()


@router.message(Command("check_progress"))
async def check_progress(message: Message):
    """
    Обработчик команды /check_progress.
    Отображает текущий прогресс пользователя за сегодняшний день.

    Args:
        message: Объект сообщения от пользователя

    Returns:
        None: Отправляет сообщение с информацией о прогрессе пользователя
    """
    user_id = message.from_user.id
    logger.info(f"User ID: {user_id}")
    
    try:
        with sqlite3.connect(settings.DB_NAME) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT water_goal, calorie_goal FROM users WHERE user_id = ?", 
                (user_id,)
            )
            user_goals = cursor.fetchone()

            if user_goals is None:
                await message.answer("Пожалуйста, сначала настройте свой профиль.")
                return

            water_goal, calorie_goal = user_goals
            today = datetime.now().strftime('%Y-%m-%d')

            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) 
                FROM water_logs 
                WHERE user_id = ? 
                AND strftime('%Y-%m-%d', date) = ?
            """, (user_id, today))
            water_intake = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COALESCE(SUM(calories), 0) 
                FROM food_logs 
                WHERE user_id = ? 
                AND strftime('%Y-%m-%d', date) = ?
            """, (user_id, today))
            calories_consumed = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COALESCE(SUM(calories_burned), 0) 
                FROM workout_logs 
                WHERE user_id = ? 
                AND strftime('%Y-%m-%d', date) = ?
            """, (user_id, today))
            calories_burned = cursor.fetchone()[0]

            water_progress = min(100, int((water_intake / water_goal) * 100)) if water_goal > 0 else 0
            calorie_progress = min(100, int((calories_consumed / calorie_goal) * 100)) if calorie_goal > 0 else 0

            progress_bar = lambda p: "▓" * (p // 10) + "░" * ((100 - p) // 10)

            output = (
                "� Ваш прогресс на сегодня:\n\n"
                f"💧 Вода: {water_intake:.0f} мл / {water_goal:.0f} мл\n"
                f"{progress_bar(water_progress)} {water_progress}%\n\n"
                f"🍎 Калории: {calories_consumed:.0f} ккал / {calorie_goal:.0f} ккал\n"
                f"{progress_bar(calorie_progress)} {calorie_progress}%\n\n"
                f"🔥 Сожжено калорий: {calories_burned:.0f} ккал\n"
            )

            await message.answer(output)

    except Exception as e:
        logger.error(f"Error in check_progress: {str(e)}")
        await message.answer("Произошла ошибка при получении прогресса. Попробуйте позже.")
