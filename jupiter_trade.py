import os
import ast
import base58
from dotenv import load_dotenv

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts

from jupiter_sdk import JupiterClient, SwapMode

load_dotenv()

# Load private key from base58 in environment variable
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not PRIVATE_KEY:
    raise ValueError("Missing PRIVATE_KEY in environment variables.")

try:
    secret_bytes = base58.b58decode(PRIVATE_KEY)
    if len(secret_bytes) != 64:
        raise ValueError("Expected 64 bytes for full secret key.")
    keypair = Keypair.from_bytes(secret_bytes)
except Exception as e:
    raise ValueError(f"Failed to decode PRIVATE_KEY from base58: {e}")

wallet_address = str(keypair.pubkey())

# Solana RPC client
client = Client("https://api.mainnet-beta.solana.com")
async_client = AsyncClient("https://api.mainnet-beta.solana.com")

jupiter = JupiterClient(async_client)

# 🔁 Execute real trade
async def execute_trade(token_address: str, usdc_amount: float, symbol: str, price: float):
    try:
        route_map = await jupiter.route_map()
        usdc_mint = Pubkey.from_string("Es9vMFrzaCERZT2XXGkUa6cdGvySCGAUnxHkcDFVSxkf")  # USDC
        out_mint = Pubkey.from_string(token_address)

        # Get best route
        routes = await jupiter.quote(
            input_mint=usdc_mint,
            output_mint=out_mint,
            amount=int(usdc_amount * 10**6),
            slippage=1.0,
            swap_mode=SwapMode.ExactIn
        )

        if not routes or not routes["data"]:
            return {"success": False, "error": "No swap route found."}

        route = routes["data"][0]

        tx_data = await jupiter.swap(
            route=route,
            user_public_key=keypair.pubkey()
        )

        tx = tx_data["swapTransaction"]

        # Sign and send
        from solders.transaction import VersionedTransaction
        signed = VersionedTransaction.from_bytes(base58.b58decode(tx)).sign([keypair])
        txid = await async_client.send_raw_transaction(signed.serialize(), opts=TxOpts(skip_preflight=True))

        return {
            "success": True,
            "tx_hash": str(txid.value),
            "token": symbol,
            "amount_usdc": usdc_amount
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

# ✅ Stop-loss / Take-profit logic
async def check_stop_loss_take_profit(token_data, buy_price, stop_loss=0.10, take_profit=0.25):
    current_price = token_data["price"]
    drop = (buy_price - current_price) / buy_price
    gain = (current_price - buy_price) / buy_price

    if drop >= stop_loss:
        return "stop_loss"
    elif gain >= take_profit:
        return "take_profit"
    return None
