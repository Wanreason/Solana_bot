import os
import asyncio
import logging
from aiohttp import web
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from filters import is_token_valid
from alert import send_alert
from fetchers.jup import fetch_jupiter_tokens  # Fetch token list from Jupiter

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in environment variables.")

# --- Web server (for Railway or Fly.io) ---
async def handle_ping(request):
    return web.Response(text="OK")

# --- Telegram Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot is live and tracking Solana tokens!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is running...")

async def hot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("🔥 Received /hot command")
    await update.message.reply_text("🔥 Scanning top hot tokens, please wait...")

    try:
        tokens = await fetch_jupiter_tokens()
        hot_tokens = []

        # Check only first 30 tokens for performance
        for token in tokens[:30]:
            if await is_token_valid(token):
                symbol = token.get("symbol", "???")
                address = token.get("address", "N/A")
                hot_tokens.append(f"• {symbol} — {address}")

            if len(hot_tokens) >= 5:
                break

        if hot_tokens:
            response = "🔥 Top Hot Tokens:\n\n" + "\n".join(hot_tokens)
        else:
            response = "⚠️ No hot tokens found."

        await update.message.reply_text(response)

    except Exception as e:
        logging.error(f"❌ Error in /hot command: {e}")
        await update.message.reply_text("❌ Failed to fetch hot tokens.")

# --- Telegram Bot Runtime ---
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

# --- Token Monitoring Loop ---
async def process_tokens():
    while True:
        logging.info("🔍 Fetching tokens...")
        try:
            tokens = await fetch_jupiter_tokens()
            for token in tokens:
                if await is_token_valid(token):
                    chat_id = int(CHAT_ID) if CHAT_ID else 123456789
                    await send_alert(token, chat_id)
        except Exception as e:
            logging.error(f"❌ Error in token processing: {e}")
        await asyncio.sleep(60)

# --- Main Entrypoint ---
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
