import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")  # Берем токен из переменных окружения

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Привет! Отправь мне аудиофайл, и я добавлю эффект концертного зала!\n"
        "Максимальный размер файла - 20 МБ."
    )

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Получаем файл
        file = await (update.message.audio or update.message.voice).get_file()
        original_title = update.message.audio.title if update.message.audio else "Voice Message"

        # Создаем временные файлы
        input_path = "input.ogg"
        output_path = "output.mp3"
        await file.download_to_drive(input_path)

        # Обработка FFmpeg (используем системный ffmpeg)
        subprocess.run([
            "ffmpeg",
            "-i", input_path,
            "-af", "aecho=0.8:0.88:60:0.4",
            "-codec:a", "libmp3lame",
            output_path
        ], check=True)

        # Отправка результата
        await update.message.reply_audio(
            audio=open(output_path, "rb"),
            title=f"{original_title} (Reverb FX)",
            performer="Audio Bot"
        )

    finally:
        # Удаление временных файлов
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio))
    app.run_polling()