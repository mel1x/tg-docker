# Используем официальный образ Python

FROM python:3.12

# Устанавливаем рабочую директорию

ENV LANG=ru_RU.UTF-8
ENV LANGUAGE=ru_RU:ru
ENV LC_ALL=ru_RU.UTF-8

WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY main.py .

# Запускаем бота
CMD ["python", "main.py"]


