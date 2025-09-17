# Используем официальный slim-образ Python 3.12
FROM python:3.13.1

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем зависимости системы
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry

# Копируем pyproject.toml и poetry.lock для установки зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости Python с помощью Poetry
RUN poetry install --no-root

# Копируем исходный код приложения в контейнер
COPY . .

# Создаем директорию для медиафайлов
RUN mkdir -p /app/media
RUN mkdir -p /app/staticfiles && chmod -R 755 /app/staticfiles

# Пробрасываем порт, который будет использовать Django
EXPOSE 8000

# Команда для запуска приложения
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]
