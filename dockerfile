FROM python:3.1-slim-bookworm

# Устанавливаем ffmpeg и очищаем кеш apt для уменьшения размера образа
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Копируем только нужные файлы (улучшение для кэширования)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запуск бота
CMD ["python", "main.py"]