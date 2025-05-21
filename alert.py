import logging
from telegram import Bot
from fetchers.birdeye import fetch_token_info_birdeye

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN)

async def send_alert(token, chat_id):
    address = token.get("address")
    if not address:
        return

    info = await fetch_token_info_birdeye(address)
    if not info or "data" not in info:
        logging.warning(f"⚠️ Cannot alert: Missing data for {address}")
        return

    data = info["data"]
    name = data.get("name", "Unknown")
    symbol = data.get("symbol", "N/A")
    price = data.get("price_usd", "0")
    volume = data.get("volume", {}).get("h24", "0")
    liquidity = data.get("liquidity", {}).get("usd", "0")
    txns = data.get("txns", {}).get("h1", {}).get("buys", 0)

    msg = (
        f"🚨 <b>New Token Detected</b>\n\n"
        f"🔹 <b>{name} ({symbol})</b>\n"
        f"💲 Price: ${float(price):.6f}\n"
        f"💧 Liquidity: ${float(liquidity):,.0f}\n"
        f"📊 24h Volume: ${float(volume):,.0f}\n"
        f"💸 1h Buys: {txns}\n"
        f"📎 <a href='https://birdeye.so/token/{address}?chain=solana'>View on Birdeye</a>"
    )

    try:
        await bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML", disable_web_page_preview=True)
        logging.info(f"📬 Alert sent for token: {symbol}")
    except Exception as e:
        logging.error(f"❌ Failed to send alert for {address}: {e}")
