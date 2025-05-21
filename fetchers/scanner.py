import logging
from fetchers.birdeye import fetch_token_info_birdeye

# TEMP: Replace with real token addresses or logic to fetch tokens
solana_token_list = [
    "So11111111111111111111111111111111111111112",  # SOL
    "Es9vMFrzaCERGyjMY6Dk2CVAgwF1Lx3SMwFgW6Y6t2tw",  # USDT
]

async def fetch_tokens():
    tokens = []
    for address in solana_token_list:
        token_data = await fetch_token_info_birdeye(address)
        if token_data:
            tokens.append(token_data.get("data"))
        else:
            logging.warning(f"❌ Skipping token {address} due to fetch failure.")
    return tokens
