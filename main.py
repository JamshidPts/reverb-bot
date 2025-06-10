import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Скачивание файла
        file = await (update.message.audio or update.message.voice).get_file()
        input_path = "input.ogg"
        await file.download_to_drive(input_path)

        # Абсолютный путь к выходному файлу
        output_path = os.path.abspath("output.mp3")

        # Команда FFmpeg с полным путем
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-af", "aecho=0.8:0.88:60:0.4",
            "-y",  # Перезаписать если существует
            output_path
        ]

        # Запуск с обработкой ошибок
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")

        # Проверка существования файла
        if not os.path.exists(output_path):
            raise Exception("Output file not created")

        # Отправка файла
        with open(output_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                title="Processed Audio",
                timeout=30
            )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
    finally:
        # Удаление временных файлов
        for f in [input_path, output_path]:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except:
                pass

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio))
app.run_polling()