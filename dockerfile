FROM python:3.12-slim-bookworm

# 1. Устанавливаем FFmpeg и зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev && \
    rm -rf /var/lib/apt/lists/*

# 2. Проверяем установку FFmpeg
RUN ffmpeg -version

# 3. Устанавливаем Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем код
COPY . .

# 5. Запускаем бота
CMD ["python", "main.py"]