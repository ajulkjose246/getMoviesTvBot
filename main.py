import os
import threading
from flask import Flask, send_from_directory
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Load bot token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flask server
server = Flask(__name__)

@server.route('/')
def index():
    return "Telegram File-to-Link Bot is Running!"

# Serve uploaded files
@server.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a file and I'll give you a link!")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    file = await document.get_file()
    file_path = f"{UPLOAD_FOLDER}/{document.file_unique_id}_{document.file_name}"
    await file.download_to_drive(file_path)

    # Replace "your-app-name" with your actual Render app subdomain
    link = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/uploads/{os.path.basename(file_path)}"
    await update.message.reply_text(f"Here's your link: {link}")

# Run bot in a separate thread
def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.run_polling()

# Run Flask + bot
if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting server on port {port}")
    server.run(host='0.0.0.0', port=port, debug=False)
