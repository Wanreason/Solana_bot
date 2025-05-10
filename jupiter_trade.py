# jupiter_trade.py
import os
import httpx
import base64
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed

USDC_MINT = "Es9vMFrzaCERJzD6ZRBN5JZp1XrqJg9YdtxuKPrsB8Q"
JUPITER_QUOTE_URL = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_URL = "https://quote-api.jup.ag/v6/swap"

purchased_tokens = {}  # symbol: {entry_price, address}

async def execute_trade(token_address: str, amount_usdc: float, symbol: str, price: float):
    private_key_b64 = os.getenv("PRIVATE_KEY")
    if not private_key_b64:
        print("❌ No private key provided.")
        return

    keypair = Keypair.from_secret_key(base64.b64decode(private_key_b64))
    user_pubkey = str(keypair.public_key)

    try:
        async with httpx.AsyncClient() as client:
            quote_res = await client.get(JUPITER_QUOTE_URL, params={
                "inputMint": USDC_MINT,
                "outputMint": token_address,
                "amount": int(amount_usdc * 10**6),
                "slippage": 1,
            })
            route = quote_res.json()["data"][0]

            swap_res = await client.post(JUPITER_SWAP_URL, json={
                "route": route,
                "userPublicKey": user_pubkey,
                "wrapUnwrapSOL": False
            })

            swap_tx_bytes = base64.b64decode(swap_res.json()["swapTransaction"])
            transaction = Transaction.deserialize(swap_tx_bytes)
            transaction.sign(keypair)

            async with AsyncClient("https://api.mainnet-beta.solana.com") as solana_client:
                txid = await solana_client.send_transaction(
                    transaction, keypair, opts=TxOpts(skip_preflight=True, preflight_commitment=Confirmed)
                )
                print(f"✅ Buy Success: https://solscan.io/tx/{txid.value}")

            # Track for sell
            purchased_tokens[symbol] = {"entry_price": price, "address": token_address}

    except Exception as e:
        print(f"⚠️ Buy failed: {e}")

async def check_stop_loss_take_profit():
    async with httpx.AsyncClient() as client:
        for symbol, data in list(purchased_tokens.items()):
            try:
                quote = await client.get(JUPITER_QUOTE_URL, params={
                    "inputMint": data['address'],
                    "outputMint": USDC_MINT,
                    "amount": 1000000,  # dummy 1 token equivalent
                })
                out = quote.json()['data'][0]
                current_price = out['outAmount'] / 10**6
                entry = data['entry_price']
                change = (current_price - entry) / entry * 100

                if change <= -10 or change >= 30:
                    print(f"📉 Triggering sell for {symbol} ({change:.2f}%)")
                    await execute_sell(data['address'], symbol)
                    del purchased_tokens[symbol]

            except Exception as e:
                print(f"⚠️ Price check failed for {symbol}: {e}")

async def execute_sell(token_address: str, symbol: str):
    await execute_trade(token_address, 0.0, symbol, 0.0)  # simulate sell logic
    print(f"✅ Simulated sell for {symbol}")
