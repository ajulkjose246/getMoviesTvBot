import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = "https://getmoviestvbot.onrender.com"  # Your specific Render URL
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# FastAPI server
app = FastAPI()

# Initialize bot application globally
application = ApplicationBuilder().token(BOT_TOKEN).build()

@app.get("/")
async def index():
    return "Telegram File-to-Link Bot is Running!"

# Serve uploaded files
@app.get("/uploads/{filename}")
async def uploaded_file(filename: str):
    return FileResponse(os.path.join(UPLOAD_FOLDER, filename))

# Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, application.bot)
    await application.update_queue.put(update)
    return {"status": "OK"}

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

if __name__ == '__main__':
    # Initialize the bot
    init_bot()
    
    # Set webhook
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting server on port {port}")

    # Start FastAPI server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
