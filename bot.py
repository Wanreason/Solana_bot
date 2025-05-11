import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from jupiter_trade import execute_trade, auto_sell_if_needed
from jupiter_utils import fetch_token_info, get_hot_memecoins

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Solana trading bot is online!")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /buy <symbol_or_address>")
        return

    symbol_or_address = context.args[0].upper()
    token_data = await fetch_token_info(symbol_or_address)

    if not token_data:
        await update.message.reply_text(f"Token not found: {symbol_or_address}")
        return

    result = await execute_trade(token_data["address"], 10, token_data["symbol"], token_data["price"])  # Buy $10 worth
    if result["success"]:
        await update.message.reply_text(
            f"✅ Bought {result['token']} for ${result['amount_usdc']}\nTX: {result['tx_hash']}"
        )
    else:
        await update.message.reply_text(f"❌ Buy failed: {result['error']}")

async def hot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tokens = await get_hot_memecoins()
    if not tokens:
        await update.message.reply_text("No hot memecoins found.")
        return

    msg = "🔥 Hot Memecoins:\n"
    for token in tokens[:10]:
        msg += f"- {token['symbol']} @ ${token['price']:.6f}\n"
    await update.message.reply_text(msg)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("hot", hot))

    print("🤖 Bot started.")
    app.run_polling()

if __name__ == "__main__":
    main()
