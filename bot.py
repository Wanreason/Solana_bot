import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive
from jupiter_utils import get_hot_memecoins

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Use /hot to see trending Solana memecoins.")

# /hot command to get trending memecoins
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

# Main function
def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hot", hot))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
