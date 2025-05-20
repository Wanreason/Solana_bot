import logging
from config import (
    MIN_VOLUME,
    MIN_LIQUIDITY,
    BLACKLISTED_WORDS,
)
from scanner.token_safety import basic_safety_check

def is_token_valid(token: dict) -> bool:
    if not token:
        return False

    volume = token.get('volume24h', 0)
    if volume < MIN_VOLUME:
        logging.info(f"❌ Rejected: Volume too low (${volume})")
        return False

    liquidity = token.get('liquidity', 0)
    if liquidity < MIN_LIQUIDITY:
        logging.info(f"❌ Rejected: Liquidity too low (${liquidity})")
        return False

    price_change = token.get('priceChange24h', 0)
    if price_change < 0:
        logging.info(f"❌ Rejected: Negative price trend ({price_change}%)")
        return False

    name = token.get('name', '').lower()
    symbol = token.get('symbol', '').lower()
    for word in BLACKLISTED_WORDS:
        if word in name or word in symbol:
            logging.info(f"❌ Rejected: Name contains blacklisted word '{word}'")
            return False

    if not basic_safety_check(token):
        logging.info("❌ Rejected: Failed basic safety check")
        return False

    return True
