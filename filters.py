import logging
from fetchers.raydium import fetch_raydium_pairs
from fetchers.birdeye import fetch_token_info_birdeye

async def is_token_valid(token):
    address = token.get("address")
    if not address:
        return False

    birdeye_info = await fetch_token_info_birdeye(address)
    raydium_info = await fetch_raydium_info(address)

    if not birdeye_info or not raydium_info:
        return False

    try:
        liquidity = float(birdeye_info["data"]["liquidity"]["usd"])
        volume = float(birdeye_info["data"]["volume"]["h24"])
        age = int(raydium_info["createdEpochTime"])

        if liquidity > 9000 and volume > 2000:
            logging.info(f"✅ Token {address} passed filters (liq: {liquidity}, vol: {volume})")
            return True
        else:
            logging.info(f"⛔ Token {address} failed filters (liq: {liquidity}, vol: {volume})")
    except Exception as e:
        logging.warning(f"⚠️ Filter error for token {address}: {e}")

    return False
