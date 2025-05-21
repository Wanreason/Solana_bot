import aiohttp
import logging

RAYDIUM_API_URL = "https://api.raydium.io/pairs"

async def fetch_raydium_pairs():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(RAYDIUM_API_URL) as resp:
                if resp.status == 429:
                    logging.warning("❌ Raydium rate limit hit (429). Sleeping for 2 minutes before retrying.")
                    await asyncio.sleep(120)
                    return []
                elif resp.status == 200:
                    data = await resp.json()
                    return data
                else:
                    logging.warning(f"❌ Raydium returned unexpected status {resp.status}")
                    return []
    except Exception as e:
        logging.error(f"❌ Raydium fetch error: {e}")
        return []
