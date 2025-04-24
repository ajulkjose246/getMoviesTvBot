import os
from flask import Flask, request, send_from_directory
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Your Render URL + /webhook
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flask server
server = Flask(__name__)
# Initialize bot application globally
application = ApplicationBuilder().token(BOT_TOKEN).build()

@server.route('/')
def index():
    return "Telegram File-to-Link Bot is Running!"

# Serve uploaded files
@server.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Webhook endpoint
@server.route('/webhook', methods=['POST'])
async def webhook():
    await application.update_queue.put(Update.de_json(request.get_json(), application.bot))
    return 'OK'

# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a file and I'll give you a link!")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    file = await document.get_file()
    file_path = f"{UPLOAD_FOLDER}/{document.file_unique_id}_{document.file_name}"
    await file.download_to_drive(file_path)

    link = f"{WEBHOOK_URL}/uploads/{os.path.basename(file_path)}"
    await update.message.reply_text(f"Here's your link: {link}")

# Initialize bot handlers
def init_bot():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    return application

if __name__ == '__main__':
    # Initialize the bot
    app = init_bot()
    
    # Set webhook
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting server on port {port}")
    
    # Start the webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=f"{WEBHOOK_URL}/webhook",
        drop_pending_updates=True
    )
