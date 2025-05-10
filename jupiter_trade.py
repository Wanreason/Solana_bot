import os
import ast
from dotenv import load_dotenv

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts

load_dotenv()

# Load private key from environment variable
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Validate private key format
if not PRIVATE_KEY:
    raise ValueError("Missing PRIVATE_KEY in environment variables.")

try:
    private_key_list = ast.literal_eval(PRIVATE_KEY)
    if not isinstance(private_key_list, list) or len(private_key_list) != 64:
        raise ValueError("Invalid PRIVATE_KEY format. It must be a list of 64 integers.")
    keypair = Keypair.from_bytes(bytearray(private_key_list))
except Exception as e:
    raise ValueError(f"Failed to parse PRIVATE_KEY: {e}")

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
