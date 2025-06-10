import os
import subprocess
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # 1. Получаем файл
        file = await (update.message.audio or update.message.voice).get_file()
        file_type = "audio" if update.message.audio else "voice"
        logger.info(f"Received {file_type} file")

        # 2. Скачиваем файл
        input_path = "/tmp/input.ogg"
        await file.download_to_drive(input_path)
        logger.info(f"File saved to {input_path}")

        # 3. Обработка FFmpeg
        output_path = "/tmp/output.mp3"
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-af", "aecho=0.8:0.88:60:0.4",
            "-y",  # Перезаписать если существует
            output_path
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg failed: {result.stderr}")
            await update.message.reply_text("❌ Ошибка обработки аудио")
            return

        # 4. Проверяем результат
        if not os.path.exists(output_path):
            logger.error("Output file not created")
            await update.message.reply_text("❌ Файл не был создан")
            return

        # 5. Отправляем результат
        with open(output_path, 'rb') as f:
            await update.message.reply_audio(
                audio=f,
                title="Processed Audio",
                timeout=30
            )
        logger.info("Audio sent successfully")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        await update.message.reply_text(f"⚠️ Ошибка: {str(e)}")
    finally:
        # 6. Удаляем временные файлы
        for path in [input_path, output_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except:
                pass

if __name__ == "__main__":
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio))
        app.run_polling()
    except Exception as e:
        logger.critical(f"Bot failed: {str(e)}", exc_info=True)