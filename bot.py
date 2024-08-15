import os
import logging
import yadisk
import aiofiles
import audio_metadata
from telegram import Update
from telegram import error
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello and welcome to ☁️ Cloudy bot! ☁️\n\nThis bot can upload your audio files to 💿 yandex disk 💿 with partition it to subfolders\n\nTo use this bot:\n1. Send 🎵 audio files 🎵 you want to upload to your yandex disk\n2. Type /upload to ⬆️ upload ⬆️ files to your disk\n3. 🎉 Congrats! 🎉")

async def list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    music_list = "Saved list:\n"
    for f in os.listdir("./music"): music_list = music_list + f + "\n"
    if music_list != "Saved list:\n": await update.message.reply_text(music_list)
    else: await update.message.reply_text("❌ The list is empty! ❌")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for f in os.listdir("./music"): os.remove(f"./music/{f}")
    await update.message.reply_text("❌ Music list was cleared! ❌")
    await update.message.reply_sticker("CAACAgQAAxkBAAMOZr5f8VZ1GEoTTU7pyhK0DEE_Z8UAAoUDAALN9cAEVTCgAAEcHhEAATUE")

async def get_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id = update.message.audio.file_id
    file = await update.get_bot().get_file(id)
    await file.download_to_drive(f"music/{update.message.audio.file_name}")
    await update.message.reply_text(f"(🎵{update.message.audio.file_name}🎵) was succesfully saved! ✔️")

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        music_list = "Uploaded list:\n"
        client = yadisk.AsyncClient(token="<yandex token>")
        async with client:
            logging.info(client.check_token())
            for f in os.listdir("./music"):
                metadata = audio_metadata.load(f"./music/{f}")
                try:
                    await client.mkdir(f"/Music/{metadata['tags']['artist'][0]}")
                except yadisk.exceptions.DirectoryExistsError:
                    logging.warning(f"/Music/{metadata['tags']['artist'][0]} is already exist")
                try:
                    await client.mkdir(f"/Music/{metadata['tags']['artist'][0]}/{metadata['tags']['album'][0]}")
                except yadisk.exceptions.DirectoryExistsError:
                    logging.warning(f"/Music/{metadata['tags']['artist'][0]} is already exist")
                async with aiofiles.open(f"./music/{f}", "rb"):
                    try: 
                        await client.upload(f"./music/{f}", f"/Music/{metadata['tags']['artist'][0]}/{metadata['tags']['album'][0]}/{f}")
                        await update.message.reply_text(f"(🎵{f}🎵) was succesfully upload ✔️")
                        music_list = music_list + f + "\n"
                    except yadisk.exceptions.PathExistsError:
                        await update.message.reply_text(f"{f} is already exists")
                    except:
                        await update.message.reply_text(f"{f} was not uploaded")
        await update.message.reply_text(music_list)
        await update.message.reply_sticker("CAACAgIAAxkBAAMXZr5gHnFPay76C1S-irtWwtYRSvcAAnlgAAKezgsAAQUv3F8rFUQ7NQQ")
        for f in os.listdir("./music"): os.remove(f"./music/{f}")
    except error.BadRequest: 
        await update.message.reply_text("You have not sent any audio!")

if __name__ == '__main__':

    application = Application.builder().token("<tg bot token>").build()

    start_handler = CommandHandler('start', start)
    get_audio_handler = MessageHandler(filters.AUDIO, get_audio)
    upload_handler = CommandHandler('upload', upload)
    list_handler = CommandHandler('list', list)
    clear_handler = CommandHandler('clear', clear)
    application.add_handler(start_handler)
    application.add_handler(clear_handler)
    application.add_handler(list_handler)
    application.add_handler(upload_handler)
    application.add_handler(get_audio_handler)

    application.run_polling()
    