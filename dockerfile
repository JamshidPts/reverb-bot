FROM debian:bookworm-slim

# Установка Python 3.13 и FFmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    build-essential \
    ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Скачиваем и устанавливаем Python 3.13
RUN wget https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tar.xz && \
    tar -xf Python-3.13.0.tar.xz && \
    cd Python-3.13.0 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make install && \
    cd .. && \
    rm -rf Python-3.13.0*

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Запускаем бота
CMD ["python", "main.py"]