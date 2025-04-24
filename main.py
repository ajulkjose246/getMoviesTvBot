from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

BOT_TOKEN = os.environ.get("7082831105:AAFesRCvibCeyUR4WfP5bEtoLyTlvoGxv00")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a file and I’ll give you a link!")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    file = await document.get_file()
    file_path = f"{UPLOAD_FOLDER}/{document.file_unique_id}_{document.file_name}"
    await file.download_to_drive(file_path)

    # This is a fake link — for real hosting, integrate cloud or expose folder publicly
    fake_link = f"https://your-app-name.onrender.com/uploads/{os.path.basename(file_path)}"
    await update.message.reply_text(f"Here’s your link: {fake_link}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.run_polling()
