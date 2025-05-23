# fetchers/jup.py
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

                if isinstance(data, dict):  # <-- Jupiter returns a dict of tokens
                    token_list = list(data.values())  # Convert to list of tokens
                    logging.info(f"✅ Fetched {len(token_list)} tokens from Jupiter")
                    return token_list
                else:
                    logging.error("❌ Unexpected data format (not a dict)")
                    return []
            except Exception as json_error:
                logging.error(f"❌ Failed to parse JSON: {json_error}")
                return []
        else:
            logging.warning(f"⚠️ Jupiter API returned status {response.status_code}")
            return []

    except Exception as e:
        logging.error(f"❌ Error fetching Jupiter tokens: {e}")
        return []
