from telegram import Bot
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

def send_alert(token: dict):
    try:
        name = token.get("name", "Unknown")
        symbol = token.get("symbol", "N/A")
        price = token.get("priceUsd", 0)
        liquidity = token.get("liquidity", 0)
        volume = token.get("volume24h", 0)
        price_change = token.get("priceChange24h", 0)
        url = token.get("url", "")

        message = (
            f"✅ *New Token Alert!*\n\n"
            f"🚀 *Token:* {name} (${symbol})\n"
            f"🟢 *Price:* `${price:.8f}`\n"
            f"💰 *Liquidity:* `${liquidity:,.0f}`\n"
            f"📊 *Volume (24h):* `${volume:,.0f}`\n"
            f"📈 *Change (24h):* `{price_change:.2f}%`\n"
            f"🔗 [View on DexScreener]({url})\n\n"
            f"#Solana #TokenAlert"
        )

        bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        print(f"✅ Alert sent: {name} (${symbol})")

    except Exception as e:
        print(f"❌ Error sending alert: {e}")
