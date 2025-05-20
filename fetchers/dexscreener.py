import aiohttp
import logging

async def fetch_dexscreener_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    timeout = aiohttp.ClientTimeout(total=10)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("pairs", [])
                else:
                    logging.warning(f"❌ DexScreener returned status {resp.status}")
    except Exception as e:
        logging.error(f"❌ DexScreener fetch failed: {e}")
    return []
