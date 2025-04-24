import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

# Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    try:
        json_data = await request.json()
        logger.info(f"Received webhook data: {json_data}")  # Log the received data

        # Parse and process the update
        update = Update.de_json(json_data, application.bot)
        await application.update_queue.put(update)
        return {"status": "OK"}
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a file and I'll give you a link!")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if document:
        try:
            file = await document.get_file()
            file_path = f"{UPLOAD_FOLDER}/{document.file_unique_id}_{document.file_name}"
            await file.download_to_drive(file_path)

            link = f"{WEBHOOK_URL}/uploads/{os.path.basename(file_path)}"
            await update.message.reply_text(f"Here's your link: {link}")
            logger.info(f"File downloaded and available at {link}")
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            await update.message.reply_text("An error occurred while processing your file.")
    else:
        await update.message.reply_text("No file found in your message.")

# Initialize bot handlers
def init_bot():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

if __name__ == '__main__':
    # Initialize the bot
    init_bot()

    # Set webhook (if applicable)
    # webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}/webhook"
    # You can uncomment the following lines to set the webhook programmatically if needed.
    # response = requests.get(webhook_url)
    # logger.info(f"Webhook set response: {response.text}")

    # Start FastAPI server
    port = int(os.environ.get("PORT", 10000))
    logger.info(f"Starting server on port {port}")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
