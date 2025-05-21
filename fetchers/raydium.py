import aiohttp
import logging

RAYDIUM_POOLS_URL = "https://api.raydium.io/pairs"

async def fetch_raydium_pairs():
    timeout = aiohttp.ClientTimeout(total=10)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(RAYDIUM_POOLS_URL) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logging.warning(f"❌ Raydium returned status {resp.status}")
    except Exception as e:
        logging.error(f"❌ Failed to fetch Raydium pools: {e}")

    return []
