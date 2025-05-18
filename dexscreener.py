import aiohttp

async def fetch_dexscreener_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("pairs", [])
            return []
