import os
import asyncio
import logging
from aiohttp import web
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from filters import is_token_valid
from alert import send_alert
from fetchers.birdeye import fetch_token_info_birdeye  # Keep Birdeye
from fetchers.jup import fetch_jupiter_tokens  # Use Jupiter to list tokens

load_dotenv()
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in environment variables.")

# --- Web server (for Railway/Fly.io) ---
async def handle_ping(request):
    return web.Response(text="OK")

# --- Telegram Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot is live and tracking Solana tokens!")

async def hot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Hot tokens feature coming soon!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running...")

# --- Run Telegram Bot ---
async def run_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hot", hot))
    app.add_handler(CommandHandler("status", status))

    logging.info("🤖 Telegram bot starting...")
    await app.initialize()
    await app.start()
    await app.bot.delete_webhook(drop_pending_updates=True)

    while True:
        await asyncio.sleep(3600)

# --- Token Monitoring ---
async def process_tokens():
    while True:
        logging.info("🔍 Fetching tokens...")
        try:
            tokens = await fetch_jupiter_tokens()
            for token in tokens:
                if isinstance(token, dict) and await is_token_valid(token):
                    chat_id = int(CHAT_ID) if CHAT_ID else 123456789
                    await send_alert(token, chat_id)
                else:
                    logging.warning("⚠️ Skipping invalid token entry (not a dict)")
        except Exception as e:
            logging.error(f"❌ Error in token processing: {e}")
        await asyncio.sleep(60)

# --- Main Entry Point ---
async def main():
    app = web.Application()
    app.add_routes([web.get('/', handle_ping)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logging.info("🌐 Web server running on port 8080")

    await asyncio.gather(
        run_telegram_bot(),
        process_tokens()
    )

if __name__ == "__main__":
    asyncio.run(main())
