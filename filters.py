import logging
from fetchers.birdeye import fetch_token_info_birdeye

async def is_token_valid(token):
    address = token.get("address") or token.get("pairAddress")
    if not address:
        logging.warning("⚠️ Token missing address.")
        return False

    info = await fetch_token_info_birdeye(address)
    if not info or "data" not in info:
        return False

    data = info["data"]

    try:
        price = float(data.get("price_usd", 0))
        market_cap = float(data.get("mc", 0))
        volume = float(data.get("volume_24h", 0))
        liquidity = float(data.get("liquidity", 0))

        if price <= 0 or market_cap <= 0 or volume < 5000 or liquidity < 2000:
            return False

        logging.info(f"✅ Token passed: {data.get('symbol')} | Price: ${price:.4f}")
        return True

    except Exception as e:
        logging.error(f"❌ Error parsing token data: {e}")
        return False
