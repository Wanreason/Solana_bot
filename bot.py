import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from keep_alive import keep_alive
from jupiter_utils import get_hot_memecoins
from jupiter_trade import execute_trade, check_stop_loss_take_profit

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
alerted_tokens = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Welcome to Solana Auto Trader!\nUse /hot to see top tokens.")

async def hot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = get_hot_memecoins()
    if not coins:
        await update.message.reply_text("No hot tokens now.")
        return

    message = "🔥 *Top Trending Solana Memecoins:*\n\n"
    for coin in coins:
        message += (
            f"*{coin['symbol']}* ({coin['name']})\n"
            f"Price: `${coin['price']:.6f}`\n"
            f"Volume: `${coin['volume24h']:,}`\n"
            f"Liquidity: `${coin['liquidity']:,}`\n"
            f"[Swap](https://jup.ag/swap/SOL-{coin['address']})\n\n"
        )
    await update.message.reply_text(message, parse_mode="Markdown")

async def auto_alert(app):
    coins = get_hot_memecoins()
    for coin in coins:
        if coin['address'] in alerted_tokens:
            continue
        if coin['volume24h'] > 50000 and coin['liquidity'] > 20000:
            symbol = coin['symbol']
            message = (
                f"🚨 *{symbol}* ({coin['name']}) is trending!\n"
                f"Price: `${coin['price']:.6f}`\n"
                f"Volume: `${coin['volume24h']:,}`\n"
                f"Liquidity: `${coin['liquidity']:,}`\n"
            )

            # Inline button
            keyboard = [[InlineKeyboardButton(f"🛒 Buy {symbol}", callback_data=f"buy_{symbol}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await app.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown", reply_markup=reply_markup)

            # Auto trade
            await execute_trade(coin['address'], 10.0, symbol, coin['price'])
            alerted_tokens.add(coin['address'])

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    symbol = query.data.replace("buy_", "")
    coins = get_hot_memecoins()
    for coin in coins:
        if coin['symbol'] == symbol:
            await execute_trade(coin['address'], 10.0, symbol, coin['price'])
            await query.edit_message_text(f"✅ Manual Buy: {symbol} placed at ${coin['price']:.6f}")
            break

def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hot", hot))
    app.add_handler(CallbackQueryHandler(handle_button))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(auto_alert, "interval", seconds=60, args=[app])
    scheduler.add_job(check_stop_loss_take_profit, "interval", seconds=45)
    scheduler.start()

    print("✅ Bot live with auto alerts, trading, SL/TP, and buttons.")
    app.run_polling()

if __name__ == '__main__':
    main()
