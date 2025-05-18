from config import (
    MIN_VOLUME,
    MIN_LIQUIDITY,
    BLACKLISTED_WORDS,
)
from scanner.token_safety import basic_safety_check

def is_token_valid(token: dict) -> bool:
    # 1. Check if token data exists
    if not token:
        return False

    # 2. Check volume (24h)
    volume = token.get('volume24h', 0)
    if volume < MIN_VOLUME:
        print(f"❌ Rejected: Volume too low (${volume})")
        return False

    # 3. Check liquidity
    liquidity = token.get('liquidity', 0)
    if liquidity < MIN_LIQUIDITY:
        print(f"❌ Rejected: Liquidity too low (${liquidity})")
        return False

    # 4. Check price trend (positive growth only)
    price_change = token.get('priceChange24h', 0)
    if price_change < 0:
        print(f"❌ Rejected: Negative price trend ({price_change}%)")
        return False

    # 5. Blacklist check
    name = token.get('name', '').lower()
    symbol = token.get('symbol', '').lower()
    for word in BLACKLISTED_WORDS:
        if word in name or word in symbol:
            print(f"❌ Rejected: Name contains blacklisted word '{word}'")
            return False

    # 6. Optional: Basic safety check
    if not basic_safety_check(token):
        print(f"❌ Rejected: Failed basic safety check")
        return False

    # Optional: Add more filters (age, renounce, etc.)

    return True
