import logging
from fetchers.birdeye import fetch_token_info_birdeye

# You can tweak these thresholds easily
MIN_VOLUME = 5000
MIN_LIQUIDITY = 2000
MIN_PRICE = 0.00000001
MIN_MARKET_CAP = 10000

async def is_token_valid(token):
    address = token.get("address") or token.get("pairAddress")
    if not address:
        logging.warning("⚠️ Token missing address.")
        return False

    info = await fetch_token_info_birdeye(address)
    if not info or "data" not in info:
        logging.warning(f"⚠️ No data from Birdeye for token {address}")
        return False

    data = info["data"]

    try:
        price = float(data.get("price_usd", 0))
        market_cap = float(data.get("mc", 0))
        volume = float(data.get("volume_24h", 0))
        liquidity = float(data.get("liquidity", 0))
        symbol = data.get("symbol", "UNKNOWN")

        # Apply thresholds
        if price < MIN_PRICE:
            logging.info(f"❌ {symbol}: Price too low (${price})")
            return False
        if market_cap < MIN_MARKET_CAP:
            logging.info(f"❌ {symbol}: Market cap too low (${market_cap})")
            return False
        if volume < MIN_VOLUME:
            logging.info(f"❌ {symbol}: 24h volume too low (${volume})")
            return False
        if liquidity < MIN_LIQUIDITY:
            logging.info(f"❌ {symbol}: Liquidity too low (${liquidity})")
            return False

        logging.info(f"✅ Token passed: {symbol} | Price: ${price:.4f}")
        return True

    except Exception as e:
        logging.error(f"❌ Error parsing token data: {e}")
        return False
