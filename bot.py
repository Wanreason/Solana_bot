import os
import asyncio
import logging
from aiohttp import web
from dotenv import load_dotenv

# Telegram bot framework
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Internal modules
from filters import is_token_valid
from alert import send_alert
from fetchers.raydium import fetch_raydium_pairs

# Load .env variables
load_dotenv()
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Optional fallback

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in environment variables.")

# --- Web server (for Railway ping) ---
async def handle_ping(request):
    return web.Response(text="OK")

# --- Telegram Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    logging.info(f"✅ /start command received from {user_id}")
    await update.message.reply_text("👋 Welcome! The bot is live and tracking tokens!")

async def hot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("🔥 /hot command received")
    await update.message.reply_text("🔥 Hot tokens feature coming soon!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("📡 /status command received")
    await update.message.reply_text("✅ Bot is running and monitoring tokens...")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"🔁 Echo message from user: {update.message.text}")
    await update.message.reply_text(f"🔁 You said: {update.message.text}")

# --- Telegram Bot Loop ---
async def run_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hot", hot))
    app.add_handler(CommandHandler("status", status))

    # Register fallback message handler (non-command messages)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logging.info("🤖 Telegram bot starting...")
    await app.initialize()
    await app.start()
    await app.bot.delete_webhook(drop_pending_updates=True)

    while True:
        await asyncio.sleep(3600)

# --- Token Scanner Loop ---
async def process_tokens():
    while True:
        logging.info("🔍 Fetching tokens...")
        try:
            tokens = await fetch_raydium_pairs()
            for token in tokens:
                if await is_token_valid(token):
                    chat_id = int(CHAT_ID) if CHAT_ID else 123456789
                    await send_alert(token, chat_id)
        except Exception as e:
            logging.error(f"❌ Error in token loop: {e}")
        await asyncio.sleep(60)

# --- Main Entry Point ---
async def main():
    # Web server for Railway keep-alive
    app = web.Application()
    app.add_routes([web.get('/', handle_ping)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logging.info("🌐 Web server running on port 8080")

    # Run both bot and token processing concurrently
    await asyncio.gather(
        run_telegram_bot(),
        process_tokens()
    )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
