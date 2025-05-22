import httpx
import logging

async def fetch_jupiter_tokens():
    try:
        url = "https://quote-api.jup.ag/v6/tokens"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)

        if response.status_code == 200:
            try:
                data = response.json()
                tokens = data.get("tokens", [])
                if isinstance(tokens, list):
                    logging.info(f"✅ Fetched {len(tokens)} tokens from Jupiter")
                    return tokens
                else:
                    logging.error("❌ Jupiter API returned unexpected format for 'tokens'")
                    return []
            except Exception as json_error:
                logging.error(f"❌ Failed to parse JSON from Jupiter API: {json_error}")
                return []
        else:
            logging.warning(f"⚠️ Jupiter API returned status {response.status_code}")
            return []

    except Exception as e:
        logging.error(f"❌ Error fetching Jupiter tokens: {e}")
        return []
