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

                # If data is a dictionary, extract its values
                if isinstance(data, dict):
                    tokens = list(data.values())
                elif isinstance(data, list):
                    tokens = data
                else:
                    logging.error("❌ Unexpected token format (not list or dict)")
                    return []

                # Filter only valid dict tokens
                valid_tokens = [t for t in tokens if isinstance(t, dict)]
                logging.info(f"✅ Fetched {len(valid_tokens)} valid tokens from Jupiter")
                return valid_tokens

            except Exception as json_error:
                logging.error(f"❌ Failed to parse JSON: {json_error}")
                return []
        else:
            logging.warning(f"⚠️ Jupiter API returned status {response.status_code}")
            return []

    except Exception as e:
        logging.error(f"❌ Error fetching Jupiter tokens: {e}")
        return []
