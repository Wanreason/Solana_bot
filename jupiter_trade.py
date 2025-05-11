import os
import base58
from dotenv import load_dotenv

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts

load_dotenv()

# Load base58 private key from environment variable
PRIVATE_KEY_BASE58 = os.getenv("PRIVATE_KEY")

# Validate private key format
if not PRIVATE_KEY_BASE58:
    raise ValueError("Missing PRIVATE_KEY in environment variables.")

try:
    private_key_bytes = base58.b58decode(PRIVATE_KEY_BASE58)
    keypair = Keypair.from_bytes(private_key_bytes)
except Exception as e:
    raise ValueError(f"Failed to decode PRIVATE_KEY from base58: {e}")

wallet_address = str(keypair.pubkey())

# Solana RPC client
client = Client("https://api.mainnet-beta.solana.com")

# 🔁 Placeholder for actual Jupiter integration
async def execute_trade(token_address: str, usdc_amount: float, symbol: str, price: float):
    print(f"[EXECUTE] Buying ${usdc_amount} of {symbol} at price ${price}")
    print(f"Token Address: {token_address}")
    print(f"Wallet: {wallet_address}")
    
    # TODO: Insert Jupiter swap logic here using token_address and keypair

    # Simulated response
    return {
        "success": True,
        "tx_hash": "mock_transaction_hash",
        "token": symbol,
        "amount_usdc": usdc_amount
    }

# ✅ Optional: Stop-loss / Take-profit logic
async def check_stop_loss_take_profit(token_data, buy_price, stop_loss=0.10, take_profit=0.25):
    current_price = token_data["price"]
    drop = (buy_price - current_price) / buy_price
    gain = (current_price - buy_price) / buy_price

    if drop >= stop_loss:
        return "stop_loss"
    elif gain >= take_profit:
        return "take_profit"
    return None
