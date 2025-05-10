import os
import httpx
import base64
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed

JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_URL = "https://quote-api.jup.ag/v6/swap"
USDC_MINT = "Es9vMFrzaCERJzD6ZRBN5JZp1XrqJg9YdtxuKPrsB8Q"  # Mainnet USDC

async def execute_trade(token_address: str, amount_usdc: float):
    private_key_b64 = os.getenv("PRIVATE_KEY")
    if not private_key_b64:
        print("❌ No private key provided.")
        return

    keypair = Keypair.from_secret_key(base64.b64decode(private_key_b64))
    user_pubkey = str(keypair.public_key)

    try:
        async with httpx.AsyncClient() as client:
            # 1. Fetch quote
            quote_res = await client.get(JUPITER_QUOTE_URL, params={
                "inputMint": USDC_MINT,
                "outputMint": token_address,
                "amount": int(amount_usdc * 10**6),  # Convert to micro USDC
                "slippage": 1,
            })
            quote_data = quote_res.json()
            if not quote_data.get("data"):
                print("❌ No route available from Jupiter.")
                return

            route = quote_data["data"][0]

            # 2. Get swap transaction
            swap_res = await client.post(JUPITER_SWAP_URL, json={
                "route": route,
                "userPublicKey": user_pubkey,
                "wrapUnwrapSOL": False,
                "feeAccount": None,
            })
            swap_json = swap_res.json()
            if "swapTransaction" not in swap_json:
                print("❌ Failed to fetch swap transaction.")
                return

            # 3. Decode transaction
            swap_tx_bytes = base64.b64decode(swap_json["swapTransaction"])
            transaction = Transaction.deserialize(swap_tx_bytes)
            transaction.sign(keypair)

            # 4. Send transaction
            async with AsyncClient("https://api.mainnet-beta.solana.com") as solana_client:
                txid = await solana_client.send_transaction(
                    transaction, keypair, opts=TxOpts(skip_preflight=True, preflight_commitment=Confirmed)
                )
                print(f"✅ Trade complete: https://solscan.io/tx/{txid.value}")

    except Exception as e:
        print(f"⚠️ Trade failed: {e}")
