import os
import asyncio
import logging
from dotenv import load_dotenv
from aiohttp import web

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from fetchers.dexscreener import fetch_dexscreener_data
from filters import is_token_valid
from alert import send_alert

# --- Load .env ---
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is missing in environment variables.")

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Global State ---
user_chat_ids = set()
alerted_tokens = set()

# --- Telegram Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_chat_ids.add(chat_id)
    logging.info(f"/start command from chat ID: {chat_id}")
    await update.message.reply_text("👋 Welcome! You'll now receive Solana token alerts here!")

async def hot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Hot tokens feature coming soon!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running and watching the Solana market!")

# --- Telegram Bot ---
async def run_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hot", hot))
    app.add_handler(CommandHandler("status", status))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logging.info("🤖 Telegram bot started...")
    await app.updater.idle()

# --- Alert Processing Loop ---
async def process_tokens():
    while True:
        try:
            print("🔍 Fetching tokens...")
            tokens = await fetch_dexscreener_data()
            for token in tokens:
                token_id = token.get("pairAddress") or token.get("url") or token.get("name")
                if not token_id or token_id in alerted_tokens:
                    continue
                if await is_token_valid(token):
                    # Send alert to all active users
                    for chat_id in user_chat_ids:
                        await send_alert(token, chat_id)
                    alerted_tokens.add(token_id)
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"❌ Error in token processor: {e}")
            await asyncio.sleep(30)

# --- HTTP Ping (for Railway) ---
async def handle_ping(request):
    return web.Response(text="OK")

async def run_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle_ping)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    logging.info("🌐 Web server running on port 8080")

# --- Entry Point ---
async def main():
    await asyncio.gather(
        run_web_server(),
        run_telegram_bot(),
        process_tokens()
    )

if __name__ == "__main__":
    asyncio.run(main())
