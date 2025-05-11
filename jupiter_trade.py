import os
import ast
import base58
import httpx
import json

from dotenv import load_dotenv
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed

load_dotenv()

# Load base58 private key
PRIVATE_KEY_B58 = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY_B58:
    raise ValueError("Missing PRIVATE_KEY in environment variables.")

try:
    secret_key_bytes = base58.b58decode(PRIVATE_KEY_B58)
    if len(secret_key_bytes) != 64:
        raise ValueError("Expected a 64-byte private key.")
    keypair = Keypair.from_bytes(secret_key_bytes)
except Exception as e:
    raise ValueError(f"Failed to decode PRIVATE_KEY from base58: {e}")

wallet_address = str(keypair.pubkey())
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
JUPITER_API = "https://quote-api.jup.ag"

# Initialize Solana client
client = AsyncClient(SOLANA_RPC)

async def execute_trade(token_address: str, usdc_amount: float, symbol: str, price: float):
    try:
        # Step 1: Get quote
        async with httpx.AsyncClient() as session:
            quote_url = f"{JUPITER_API}/v6/quote"
            params = {
                "inputMint": "Es9vMFrzaCER9Piy3Z4ZZ1xpsB8cBeLEU9tz3KjPrXkT",  # USDC
                "outputMint": token_address,
                "amount": int(usdc_amount * 10**6),
                "slippageBps": 100,
                "onlyDirectRoutes": False,
            }
            quote_response = await session.get(quote_url, params=params)
            quote = quote_response.json()

            if not quote.get("data"):
                return {"success": False, "error": "No quote available."}

            route = quote["data"][0]

            # Step 2: Get swap transaction
            swap_url = f"{JUPITER_API}/v6/swap"
            swap_payload = {
                "route": route,
                "userPublicKey": wallet_address,
                "wrapUnwrapSOL": True,
                "useSharedAccounts": True,
                "feeAccount": None,
            }
            swap_response = await session.post(swap_url, json=swap_payload)
            swap_data = swap_response.json()

            if "swapTransaction" not in swap_data:
                return {"success": False, "error": "Swap transaction not returned."}

            swap_tx_b64 = swap_data["swapTransaction"]

        # Step 3: Sign and send transaction
        from base64 import b64decode
        from solana.transaction import Transaction

        tx_bytes = b64decode(swap_tx_b64)
        transaction = Transaction.deserialize(tx_bytes)
        transaction.sign([keypair])
        tx_sig = await client.send_transaction(transaction, keypair, opts=TxOpts(skip_confirmation=False, preflight_commitment=Confirmed))

        return {
            "success": True,
            "tx_hash": tx_sig.value,
            "token": symbol,
            "amount_usdc": usdc_amount
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


async def check_stop_loss_take_profit(token_data, buy_price, stop_loss=0.10, take_profit=0.25):
    current_price = token_data["price"]
    drop = (buy_price - current_price) / buy_price
    gain = (current_price - buy_price) / buy_price

    if drop >= stop_loss:
        return "stop_loss"
    elif gain >= take_profit:
        return "take_profit"
    return None
