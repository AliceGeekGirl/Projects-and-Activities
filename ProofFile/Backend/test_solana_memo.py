import os
import json
import asyncio

from dotenv import load_dotenv
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction
from solders.message import Message
from solders.transaction import Transaction
from solana.rpc.async_api import AsyncClient


# Carrega as variáveis do arquivo .env
load_dotenv()


# Program ID oficial do Memo Program
MEMO_PROGRAM_ID = Pubkey.from_string(
    "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"
)


async def send_memo():

    # --------------------------------------------------
    # 1. Conecta à Solana Devnet
    # --------------------------------------------------

    rpc_url = os.getenv("SOLANA_RPC_URL")

    if not rpc_url:
        raise ValueError("SOLANA_RPC_URL não foi encontrada no .env")

    async with AsyncClient(rpc_url) as client:

        # --------------------------------------------------
        # 2. Recupera a carteira do .env
        # --------------------------------------------------

        private_key_text = os.getenv("SOLANA_PRIVATE_KEY")

        if not private_key_text:
            raise ValueError(
                "SOLANA_PRIVATE_KEY não foi encontrada no .env"
            )

        private_key = json.loads(private_key_text)

        keypair = Keypair.from_bytes(
            bytes(private_key)
        )

        print("Carteira:")
        print(keypair.pubkey())

        # --------------------------------------------------
        # 3. Verifica o saldo
        # --------------------------------------------------

        balance_response = await client.get_balance(
            keypair.pubkey()
        )

        balance_sol = balance_response.value / 1_000_000_000

        print("Saldo:", balance_sol, "SOL")

        if balance_response.value == 0:
            raise ValueError(
                "A carteira não possui SOL suficiente."
            )

        # --------------------------------------------------
        # 4. Dados que queremos registrar
        # --------------------------------------------------

        verification_code = "PF-TESTE001"

        file_hash = (
            "c74f6c17b42969e48d41d18d6b0db0bee5809a5db4da5e826db1b7facf0dd825"
        )

        memo_data = (
            f"PROOFFILE|{verification_code}|HASH:{file_hash}"
        )

        print("\nMemo que será registrado:")
        print(memo_data)

        # --------------------------------------------------
        # 5. Cria a instrução do Memo Program
        # --------------------------------------------------

        instruction = Instruction(
            program_id=MEMO_PROGRAM_ID,
            accounts=[],
            data=memo_data.encode("utf-8")
        )

        # --------------------------------------------------
        # 6. Obtém um blockhash recente
        # --------------------------------------------------

        blockhash_response = (
            await client.get_latest_blockhash()
        )

        recent_blockhash = (
            blockhash_response.value.blockhash
        )

        # --------------------------------------------------
        # 7. Cria a mensagem da transação
        # --------------------------------------------------

        message = Message.new_with_blockhash(
            [instruction],
            keypair.pubkey(),
            recent_blockhash
        )

        # --------------------------------------------------
        # 8. Cria e assina a transação
        # --------------------------------------------------

        transaction = Transaction(
            [keypair],
            message,
            recent_blockhash
        )

        # --------------------------------------------------
        # 9. Envia a transação para a Devnet
        # --------------------------------------------------

        print("\nEnviando transação...")

        response = await client.send_transaction(
            transaction
        )

        signature = response.value

        print("\n===================================")
        print("TRANSAÇÃO ENVIADA COM SUCESSO!")
        print("===================================")

        print("\nTransaction Signature:")
        print(signature)

        print("\nMemo:")
        print(memo_data)

        print("\nExplorer:")
        print(
            f"https://explorer.solana.com/tx/{signature}?cluster=devnet"
        )


asyncio.run(send_memo())