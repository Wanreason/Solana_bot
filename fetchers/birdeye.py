import aiohttp
import logging

async def fetch_token_info_birdeye(address):
    url = f"https://public-api.birdeye.so/public/token/{address}"
    headers = {"x-chain": "solana"}
    timeout = aiohttp.ClientTimeout(total=10)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logging.warning(f"❌ Birdeye returned status {resp.status} for token {address}")
    except Exception as e:
        logging.error(f"❌ Birdeye fetch failed for token {address}: {e}")
    
    return None

