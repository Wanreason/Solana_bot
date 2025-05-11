import requests

# Fetch token info and price from Jupiter token list
async def fetch_token_info(symbol_or_address: str):
    try:
        # Jupiter token list API
        url = "https://cache.jup.ag/tokens"
        response = requests.get(url)
        response.raise_for_status()

        tokens = response.json().get("tokens", [])

        for token in tokens:
            if token["symbol"].lower() == symbol_or_address.lower() or token["address"] == symbol_or_address:
                return {
                    "address": token["address"],
                    "symbol": token["symbol"],
                    "name": token["name"],
                    "decimals": token["decimals"],
                    "logoURI": token.get("logoURI"),
                    "price": token.get("price", 0.0)
                }

        raise ValueError(f"Token '{symbol_or_address}' not found in Jupiter token list.")

    except Exception as e:
        return {"error": str(e)}
