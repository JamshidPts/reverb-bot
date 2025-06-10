import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Отправьте аудиофайл для обработки")

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Скачивание файла
        file = await (update.message.audio or update.message.voice).get_file()
        original_title = update.message.audio.title if update.message.audio else "Voice Message"
        
        input_path = "input.ogg"
        output_path = "output.mp3"
        
        await file.download_to_drive(custom_path=input_path)
        
        # Проверка что файл скачался
        if not os.path.exists(input_path):
            await update.message.reply_text("❌ Ошибка при загрузке файла")
            return

        # Обработка FFmpeg с проверкой ошибок
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-i", input_path,
                    "-af", "aecho=0.8:0.88:60:0.4",
                    "-codec:a", "libmp3lame",
                    "-y",  # Перезаписать если файл существует
                    output_path
                ],
                check=True,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode('utf-8') if e.stderr else "Неизвестная ошибка FFmpeg"
            await update.message.reply_text(f"❌ Ошибка обработки аудио:\n{error_msg}")
            return

        # Проверка что файл создан
        if not os.path.exists(output_path):
            await update.message.reply_text("❌ Обработанный файл не создан")
            return

        # Отправка файла с проверкой размера
        file_size = os.path.getsize(output_path)
        if file_size > 50 * 1024 * 1024:  # 50MB лимит Telegram
            await update.message.reply_text("❌ Файл слишком большой после обработки")
        else:
            with open(output_path, 'rb') as audio_file:
                await update.message.reply_audio(
                    audio=audio_file,
                    title=f"{original_title} (Reverb FX)",
                    performer="Audio Bot",
                    timeout=30  # Увеличенный таймаут
                )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Произошла ошибка: {str(e)}")
    finally:
        # Очистка временных файлов
        for file_path in [input_path, output_path]:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio))
    app.run_polling()