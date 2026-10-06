from solders.keypair import Keypair
import json

# Cria uma nova carteira Solana.
keypair = Keypair()

# Mostra a chave pública.
print("Public Key:")
print(keypair.pubkey())

# Converte os bytes da chave para uma lista de números.
private_key = list(bytes(keypair))

# Mostra a chave privada em formato JSON.
print("\nPrivate Key:")
print(json.dumps(private_key))