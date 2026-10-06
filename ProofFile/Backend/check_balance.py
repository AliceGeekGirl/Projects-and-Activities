import os
import json
import asyncio

from dotenv import load_dotenv
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient


# Carrega as variáveis do arquivo .env
load_dotenv()


async def check_balance():
    # Conecta à Solana Devnet
    client = AsyncClient(os.getenv("SOLANA_RPC_URL"))

    # Recupera a chave privada do .env
    private_key = json.loads(os.getenv("SOLANA_PRIVATE_KEY"))

    # Reconstrói a carteira
    keypair = Keypair.from_bytes(bytes(private_key))

    # Consulta o saldo da carteira
    balance = await client.get_balance(keypair.pubkey())

    # Mostra os resultados
    print("Public Key:", keypair.pubkey())
    print("Saldo em lamports:", balance.value)
    print("Saldo em SOL:", balance.value / 1_000_000_000)

    await client.close()


asyncio.run(check_balance())