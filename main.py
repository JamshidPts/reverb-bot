import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7516714864:AAHHlcjWA02MBK_ZaN0wrCvt_wAAAN6TWDY"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🎵 Привет! Отправь мне аудиофайл (MP3), "
        "и я добавлю эффект концертного зала!\n"
        "Максимальный размер файла - 20 МБ."
    )

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем файл (аудио или голосовое сообщение)
    if update.message.audio:
        file = await update.message.audio.get_file()
        original_title = update.message.audio.title or "Audio"
    else:
        file = await update.message.voice.get_file()
        original_title = "Voice Message"

    input_path = "input.ogg"
    output_path = "output.mp3"

    # Скачиваем файл
    await file.download_to_drive(input_path)

    # Применяем эффект реверберации через ffmpeg
    command = [
        "attached_assets/ffmpeg-7.0.2-amd64-static/ffmpeg",
        "-i", input_path,
        "-af", "aecho=0.8:0.88:60:0.4",
        "-codec:a", "libmp3lame",
        "-y",
        output_path
    ]
    subprocess.run(command, check=True)

    # Формируем новый заголовок
    new_title = f"{original_title} (Reverb FX)"

    # Отправляем обработанное аудио
    with open(output_path, 'rb') as audio:
        await update.message.reply_audio(
            audio=audio,
            filename="reverb.mp3",
            title=new_title,
            performer="Audio Processor Bot"
        )

    # Удаляем временные файлы
    os.remove(input_path)
    os.remove(output_path)

# Создаем и запускаем бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_audio))
app.run_polling()