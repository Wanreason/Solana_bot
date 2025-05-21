import os
import logging
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in environment variables.")

bot = Bot(token=TELEGRAM_TOKEN)

async def send_alert(token: dict, chat_id: int):
    try:
        name = token.get("name", "Unknown")
        symbol = token.get("symbol", "N/A")
        price = float(token.get("priceUsd", 0))
        liquidity = float(token.get("liquidity", 0))
        volume = float(token.get("volume24h", 0))
        price_change = float(token.get("priceChange24h", 0))
        url = token.get("url", "")

        # Validate URL: must start with http or https
        if not url.startswith("http"):
            logging.warning(f"⚠️ Invalid or missing DexScreener URL for token {name}: {url}")
            url = ""

        message = (
            f"✅ *New Token Alert!*\n\n"
            f"🚀 *Token:* {name} (${symbol})\n"
            f"🟢 *Price:* `${price:.8f}`\n"
            f"💰 *Liquidity:* `${liquidity:,.0f}`\n"
            f"📊 *Volume (24h):* `${volume:,.0f}`\n"
            f"📈 *Change (24h):* `{price_change:.2f}%`\n"
        )
        
        if url:
            message += f"🔗 [View on DexScreener]({url})\n\n"
        else:
            message += "\n"

        message += "#Solana #TokenAlert"

        await bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        logging.info(f"✅ Alert sent: {name} (${symbol})")

    except Exception as e:
        logging.error(f"❌ Error sending alert: {e}")
