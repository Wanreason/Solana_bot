import aiohttp
import logging

async def fetch_dexscreener_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    timeout = aiohttp.ClientTimeout(total=10)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                text = await resp.text()  # Get the raw response content
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("pairs", [])
                else:
                    logging.warning(f"❌ DexScreener returned status {resp.status} for URL: {url}")
                    logging.warning(f"🔎 Response content: {text}")
    except Exception as e:
        logging.error(f"❌ DexScreener fetch failed: {e}")

    return []
