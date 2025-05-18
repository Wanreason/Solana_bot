import aiohttp

async def fetch_token_info_birdeye(address):
    url = f"https://public-api.birdeye.so/public/token/{address}"
    headers = {"x-chain": "solana"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            return None
