import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from keep_alive import keep_alive
from jupiter_utils import get_hot_memecoins

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Your personal Telegram ID

alerted_tokens = set()  # Keeps track of already-alerted token addresses

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /hot to see trending Solana memecoins.")

# /hot command
async def hot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = get_hot_memecoins()
    if not coins:
        await update.message.reply_text("No hot memecoins found right now.")
        return

    message = "🔥 *Top Trending Solana Memecoins:*\n\n"
    for coin in coins:
        message += (
            f"*{coin['symbol']}* ({coin['name']})\n"
            f"Price: `${coin['price']:.6f}`\n"
            f"24h Volume: `${coin['volume24h']:,}`\n"
            f"Liquidity: `${coin['liquidity']:,}`\n"
            f"[Swap on Jupiter](https://jup.ag/swap/SOL-{coin['address']})\n\n"
        )
    await update.message.reply_text(message, parse_mode="Markdown")

# Auto alert function
async def auto_alert(app):
    coins = get_hot_memecoins()
    for coin in coins:
        if coin['address'] in alerted_tokens:
            continue

        # Filter logic
        if coin['volume24h'] > 50000 and coin['liquidity'] > 20000:
            message = (
                f"🚨 *New Hot Token Detected!*\n\n"
                f"*{coin['symbol']}* ({coin['name']})\n"
                f"Price: `${coin['price']:.6f}`\n"
                f"24h Volume: `${coin['volume24h']:,}`\n"
                f"Liquidity: `${coin['liquidity']:,}`\n"
                f"[Swap on Jupiter](https://jup.ag/swap/SOL-{coin['address']})"
            )
            await app.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
            alerted_tokens.add(coin['address'])

# Main function
def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hot", hot))

    # Scheduler setup
    scheduler = AsyncIOScheduler()
    scheduler.add_job(auto_alert, "interval", seconds=60, args=[app])
    scheduler.start()

    print("Bot is running with auto alerts...")
    app.run_polling()

if __name__ == '__main__':
    main()
