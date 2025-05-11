import os
import logging
import asyncio
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

from jupiter_trade import execute_trade, auto_sell_if_needed, fetch_token_and_price
from jupiter_utils import get_hot_memecoins

# Setup
logging.basicConfig(level=logging.INFO)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# --- Telegram command handlers ---

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Solana Trading Bot is live!")

def hot(update: Update, context: CallbackContext):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tokens = loop.run_until_complete(get_hot_memecoins())
    
    message = "🔥 Hot Memecoins:\n"
    for t in tokens:
        message += f"{t['symbol']} - {t['address']}\n"
    
    update.message.reply_text(message)

def price(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /price <symbol_or_address>")
        return

    token = context.args[0]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(fetch_token_and_price(token))
    
    if not data:
        update.message.reply_text("❌ Token not found.")
    else:
        update.message.reply_text(f"{data['symbol']} price: ${data['price']}")

def buy(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        update.message.reply_text("Usage: /buy <symbol_or_address> <amount_usdc>")
        return

    token = context.args[0]
    amount = float(context.args[1])

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    token_data = loop.run_until_complete(fetch_token_and_price(token))

    if not token_data:
        update.message.reply_text("❌ Token not found.")
        return

    result = loop.run_until_complete(execute_trade(token_data["address"], amount, token_data["symbol"], token_data["price"]))
    if result["success"]:
        update.message.reply_text(f"✅ Bought {result['token']} for ${result['amount_usdc']}!\nTx: {result['tx_hash']}")
    else:
        update.message.reply_text(f"❌ Error: {result['error']}")

def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("hot", hot))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CommandHandler("buy", buy))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
