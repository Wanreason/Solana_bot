import aiohttp
import logging

JUPITER_PRICE_API = "https://price.jup.ag/v4/price"

async def fetch_jupiter_price(mint_address):
    url = f"{JUPITER_PRICE_API}?ids={mint_address}"
    timeout = aiohttp.ClientTimeout(total=10)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if mint_address in data.get("data", {}):
                        return data["data"][mint_address]["price"]
                    else:
                        logging.warning(f"⚠️ No price found for {mint_address} in Jupiter response")
                else:
                    logging.warning(f"❌ Jupiter returned status {resp.status} for {mint_address}")
    except Exception as e:
        logging.error(f"❌ Failed to fetch Jupiter price for {mint_address}: {e}")

    return None
