FROM python:3.12-slim-bookworm

# 1. Устанавливаем FFmpeg и все зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libx264-dev && \
    rm -rf /var/lib/apt/lists/*

# 2. Проверяем что FFmpeg установлен
RUN ffmpeg -version

# 3. Копируем зависимости отдельно для кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем код
COPY . .

# 5. Запускаем бота
CMD ["python", "main.py"]