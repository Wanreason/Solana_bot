import logging
from telegram import ParseMode
from telegram.ext import Application

async def send_alert(token, chat_id: int, app: Application):
    """
    Sends a detailed Telegram alert about a token.

    Parameters:
    - token: dict with token info (from Birdeye and Raydium)
    - chat_id: Telegram chat ID to send message to
    - app: telegram.ext.Application instance
    """
    try:
        # Extract info safely
        name = token.get("name", "Unknown")
        symbol = token.get("symbol", "UNK")
        address = token.get("address", "")
        price = token.get("price", "N/A")
        liquidity = token.get("liquidity", "N/A")
        volume_24h = token.get("volume24h", "N/A")

        message = (
            f"🚨 *New Token Alert!*\n\n"
            f"*Name:* {name}\n"
            f"*Symbol:* {symbol}\n"
            f"*Address:* `{address}`\n"
            f"*Price:* ${price}\n"
            f"*Liquidity:* ${liquidity}\n"
            f"*24h Volume:* ${volume_24h}\n\n"
            f"[View on Solana Explorer](https://explorer.solana.com/address/{address})"
        )

        await app.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
        logging.info(f"✅ Alert sent for token {symbol} ({address})")
    except Exception as e:
        logging.error(f"❌ Failed to send alert for token {token.get('address')}: {e}")
