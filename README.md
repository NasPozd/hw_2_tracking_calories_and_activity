# Фитнес-трекер Telegram Бот

Telegram бот для отслеживания физической активности, питания и прогресса в достижении фитнес-целей.

🤖 **Попробовать бота**: [@HW2TrackingBot](https://t.me/HW2TrackingBot)

## 🌟 Возможности

- 📝 **Управление профилем**
  - Установка веса, роста, возраста
  - Выбор уровня активности
  - Настройка города для погоды

- 🏃 **Отслеживание активности**
  - Запись тренировок (бег, ходьба, велосипед, плавание, силовая, йога)
  - Расчет сожженных калорий
  - Отслеживание прогресса

- 🥗 **Контроль питания**
  - Запись приемов пищи
  - Подсчет калорий
  - Рекомендации по питанию

- 💧 **Мониторинг потребления воды**
  - Отслеживание выпитой воды
  - Расчет дневной нормы
  - Напоминания о питье

- 📊 **Анализ прогресса**
  - Просмотр статистики
  - Графики прогресса
  - Рекомендации по улучшению

- 🌤 **Погода**
  - Получение текущей погоды
  - Учет погоды в рекомендациях

## 📱 Демонстрация функций

### Настройка профиля
![Настройка профиля](https://github.com/NasPozd/hw_2_tracking_calories_and_activity/blob/ea764a69f5e36d179e010eda5f6b1ce96f5586f7/img/set_profile.gif)

### Запись тренировки
![Запись тренировки](https://github.com/NasPozd/hw_2_tracking_calories_and_activity/blob/ea764a69f5e36d179e010eda5f6b1ce96f5586f7/img/log_workout.gif)

### Запись приема пищи
![Запись приема пищи](https://github.com/NasPozd/hw_2_tracking_calories_and_activity/blob/ea764a69f5e36d179e010eda5f6b1ce96f5586f7/img/log_food.gif)

### Запись потребления воды
![Запись воды]([gif/log_water.gif](https://github.com/NasPozd/hw_2_tracking_calories_and_activity/blob/ea764a69f5e36d179e010eda5f6b1ce96f5586f7/img/log_water.gif))

### Проверка прогресса
![Проверка прогресса](https://raw.githubusercontent.com/NasPozd/hw_2_tracking_calories_and_activity/refs/heads/main/img/check_progress.gif)

### Просмотр графика прогресса
![График прогресса](https://github.com/NasPozd/hw_2_tracking_calories_and_activity/blob/ea764a69f5e36d179e010eda5f6b1ce96f5586f7/img/view_progress.gif)

### Получение рекомендаций
![Получение рекомендаций](https://github.com/NasPozd/hw_2_tracking_calories_and_activity/blob/ea764a69f5e36d179e010eda5f6b1ce96f5586f7/img/get_recommendations.gif)

### Проверка погоды
![Проверка погоды](https://github.com/NasPozd/hw_2_tracking_calories_and_activity/blob/ea764a69f5e36d179e010eda5f6b1ce96f5586f7/img/weather.gif)

## 🚀 Установка и запуск

### Предварительные требования

- Python 3.11 или выше
- Docker и Docker Compose (опционально)
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))
- OpenWeather API ключ

### Локальная установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/fitness-telegram-bot.git
cd fitness-telegram-bot
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate
venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env на основе .env.example:
```bash
cp .env.example .env
```

5. Отредактируйте .env и добавьте ваши токены и ключи

6. Запустите бота:
```bash
python bot.py
```

### Запуск через Docker

1. Соберите и запустите контейнер:
```bash
docker-compose up -d --build
```

2. Проверьте логи:
```bash
docker-compose logs -f
```

## 📝 Использование

1. Найдите бота в Telegram
2. Начните с команды `/start` или `/menu`
3. Следуйте инструкциям для настройки профиля
4. Используйте доступные команды для отслеживания активности

### Основные команды

- `/menu` - Показать главное меню
- `/set_profile` - Настроить профиль
- `/log_workout` - Записать тренировку
- `/log_food` - Записать прием пищи
- `/log_water` - Записать потребление воды
- `/check_progress` - Проверить текущий прогресс
- `/view_progress` - Посмотреть график прогресса
- `/weather` - Узнать текущую погоду
- `/get_recommendations` - Получить рекомендации

## 🛠 Технологии

- [Python](https://www.python.org/) - Основной язык программирования
- [aiogram](https://docs.aiogram.dev/) - Асинхронный фреймворк для Telegram Bot API
- [SQLite](https://www.sqlite.org/) - База данных
- [Docker](https://www.docker.com/) - Контейнеризация
- [OpenWeather API](https://openweathermap.org/api) - Данные о погоде

## 📊 Структура проекта

```
fitness-telegram-bot/
├── bot.py                # Основной файл бота
├── config.py            # Конфигурация
├── database.py          # Работа с базой данных
├── requirements.txt     # Зависимости
├── Dockerfile          # Конфигурация Docker
├── docker-compose.yml  # Конфигурация Docker Compose
├── handlers/           # Обработчики команд
│   ├── __init__.py
│   ├── menu.py
│   ├── profile.py
│   ├── workout.py
│   └── ...
└── services/          # Вспомогательные сервисы
    ├── calculations.py
    ├── logger.py
    └── weather.py
```
