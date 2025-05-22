import httpx
import logging

async def fetch_jupiter_tokens():
    try:
        url = "https://quote-api.jup.ag/v6/tokens"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)

        if response.status_code == 200:
            data = response.json()

            # ✅ Jupiter returns a list of token dicts
            if isinstance(data, list):
                return data

            # ✅ In case it's a dict with 'tokens' key (just in case)
            elif isinstance(data, dict):
                return data.get("tokens", [])

            else:
                logging.error("❌ Unexpected data format from Jupiter.")
                return []

        else:
            logging.warning(f"⚠️ Jupiter API returned status {response.status_code}")
            return []

    except Exception as e:
        logging.error(f"❌ Error fetching Jupiter tokens: {e}")
        return []
