import logging
from fetchers.birdeye import fetch_token_info_birdeye

solana_token_list = [
    "So11111111111111111111111111111111111111112",  # SOL
    "Es9vMFrzaCERGyjMY6Dk2CVAgwF1Lx3SMwFgW6Y6t2tw",  # USDT
]

async def fetch_tokens():
    tokens = []
    for address in solana_token_list:
        token_data = await fetch_token_info_birdeye(address)
        if token_data and isinstance(token_data, dict):
            token_info = token_data.get("data")
            if token_info and isinstance(token_info, dict):
                tokens.append(token_info)
            else:
                logging.warning(f"❌ Token data 'data' field missing or invalid for {address}")
        else:
            logging.warning(f"❌ Skipping token {address} due to fetch failure or invalid data.")
    return tokens
