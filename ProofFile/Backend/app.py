# IMPORTAÇÕES

# Flask para criar o servidor web, jsonify para retornar JSON,
# request para acessar os dados enviados pelo Frontend e
# send_from_directory/send_file para disponibilizar arquivos.
from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory,
    send_file
)

# Permite que o Frontend faça requisições para o Backend.
from flask_cors import CORS

# Carrega as variáveis armazenadas no arquivo .env.
from dotenv import load_dotenv

# Data para registrar automaticamente a data do cadastro.
from datetime import date

# Path para trabalhar com caminhos de arquivos.
from pathlib import Path

# Variáveis de ambiente.
import os

# Converte a chave privada armazenada no .env.
import json

# Gera identificadores únicos.
import uuid

# Calcula o hash SHA-256.
import hashlib

# Conexão com PostgreSQL.
import psycopg

# Carteira Solana.
from solders.keypair import Keypair

# Endereço público de programas/carteiras Solana.
from solders.pubkey import Pubkey

# Instrução enviada para o Memo Program.
from solders.instruction import Instruction

# Mensagem da transação.
from solders.message import Message

# Transação Solana.
from solders.transaction import Transaction

# Cliente assíncrono da Solana.
from solana.rpc.async_api import AsyncClient

# CONFIGURAÇÃO

# Carrega as variáveis do arquivo .env.
load_dotenv()

# Cria a aplicação Flask.
app = Flask(__name__)

# Permite requisições do Frontend durante o desenvolvimento.
CORS(app)

# URL de conexão com o PostgreSQL.
DATABASE_URL = os.getenv("DATABASE_URL")

# URL da Solana Devnet.
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL")

# Define a pasta do próprio projeto.
# Isso evita depender do local de onde o comando Python foi executado.
BASE_DIR = Path(__file__).resolve().parent.parent

# Define a pasta onde os PDFs serão armazenados.
UPLOAD_FOLDER = BASE_DIR / "Backend" / "uploads"

# Cria a pasta caso ela ainda não exista.
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Limita o tamanho dos arquivos enviados para 20 MB.
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024

# Endereço oficial do Memo Program da Solana.
MEMO_PROGRAM_ID = Pubkey.from_string(
    "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"
)

# FUNÇÕES AUXILIARES

def get_keypair():
    """
    Recupera a carteira Solana a partir da chave privada
    armazenada no arquivo .env.
    """

    # Pega a chave privada do .env.
    private_key_text = os.getenv("SOLANA_PRIVATE_KEY")

    # Verifica se a chave foi configurada.
    if not private_key_text:
        raise ValueError(
            "SOLANA_PRIVATE_KEY não foi encontrada no .env."
        )

    # Converte o texto JSON para uma lista de números.
    private_key = json.loads(private_key_text)

    # Reconstrói a carteira Solana.
    return Keypair.from_bytes(bytes(private_key))


def generate_file_hash(file_data):
    """
    Calcula o hash SHA-256 do conteúdo de um arquivo.
    """

    return hashlib.sha256(file_data).hexdigest()


def generate_verification_code():
    """
    Gera um código de verificação no formato:

    PF-XXXXXXXX
    """

    return "PF-" + uuid.uuid4().hex[:8].upper()


def generate_saved_filename(original_filename):
    """
    Cria um nome único para o arquivo armazenado.
    """

    return f"{uuid.uuid4().hex}_{original_filename}"


async def register_on_solana(verification_code, file_hash):
    """
    Registra o código de verificação e o hash do contrato
    na Solana Devnet usando o Memo Program.

    O PDF não é enviado para a blockchain.
    """

    # Abre a conexão com a Solana.
    async with AsyncClient(SOLANA_RPC_URL) as client:

        # Recupera a carteira usada para assinar a transação.
        keypair = get_keypair()

        # Monta o conteúdo do Memo.
        memo_data = (
            f"PROOFFILE|{verification_code}|HASH:{file_hash}"
        )

        # Cria a instrução do Memo Program.
        instruction = Instruction(
            program_id=MEMO_PROGRAM_ID,
            accounts=[],
            data=memo_data.encode("utf-8")
        )

        # Busca um blockhash recente.
        blockhash_response = await client.get_latest_blockhash()

        recent_blockhash = blockhash_response.value.blockhash

        # Cria a mensagem da transação.
        message = Message.new_with_blockhash(
            [instruction],
            keypair.pubkey(),
            recent_blockhash
        )

        # Cria e assina a transação.
        transaction = Transaction(
            [keypair],
            message,
            recent_blockhash
        )

        # Envia a transação para a Solana Devnet.
        response = await client.send_transaction(transaction)

        # Retorna a assinatura da transação.
        return str(response.value)


def validate_pdf(file):
    """
    Faz uma validação básica para o MVP.

    Verifica:
    - se existe arquivo;
    - se o nome não está vazio;
    - se a extensão é .pdf.
    """

    if file is None:
        return "Nenhum arquivo foi enviado."

    if file.filename == "":
        return "Nenhum arquivo foi selecionado."

    if not file.filename.lower().endswith(".pdf"):
        return "Apenas arquivos PDF são permitidos."

    return None

#Rota principal do backend
@app.route("/")
def home():
    return "ProofFile Backend está funcionando."

#ROTA DE TESTE DO BANCO
@app.route("/db")
def test_database():
    
    #Testa se o Backend consegue se conectar ao PostgreSQL.
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:

                cur.execute("SELECT 1;")

                result = cur.fetchone()

        return jsonify({
            "database": "connected",
            "result": result[0]
        })

    except Exception as error:

        print(f"ERRO NO BANCO: {error}")

        return jsonify({
            "error": "Não foi possível conectar ao banco de dados."
        }), 500

#ROTA DE TESTE DO HASH
@app.route("/hash", methods=["POST"])
def generate_hash():
    """
    Recebe um arquivo e retorna seu hash SHA-256.

    Essa rota foi usada para testar o funcionamento do hash
    antes da integração com o cadastro completo.
    """

    # Verifica se o arquivo é válido.
    file = request.files.get("file")

    validation_error = validate_pdf(file)

    if validation_error:
        return jsonify({
            "error": validation_error
        }), 400

    # Lê o conteúdo do arquivo.
    file_data = file.read()

    # Calcula o hash.
    file_hash = generate_file_hash(file_data)

    return jsonify({
        "file_name": file.filename,
        "file_hash": file_hash
    })

# ROTA DE REGISTRO

@app.route("/register", methods=["POST"])
async def register_contract():
    """
    Realiza o cadastro completo de um contrato.

    Fluxo:

    PDF
      ↓
    SHA-256
      ↓
    Código de verificação
      ↓
    Solana Memo
      ↓
    PostgreSQL
    """

    # 1. VALIDAÇÃO DO ARQUIVO

    file = request.files.get("file")

    validation_error = validate_pdf(file)

    if validation_error:
        return jsonify({
            "error": validation_error
        }), 400

    # 2. VALIDAÇÃO DO NOME DO CONTRATO

    contract_name = request.form.get("contract_name", "").strip()

    if not contract_name:
        return jsonify({
            "error": "O nome do contrato é obrigatório."
        }), 400

    # 3. DATA DE EXPIRAÇÃO

    expiration_date = request.form.get(
        "expiration_date",
        ""
    ).strip()

    if not expiration_date:
        expiration_date = None

    # 4. LEITURA DO ARQUIVO

    file_data = file.read()

    if not file_data:
        return jsonify({
            "error": "O arquivo enviado está vazio."
        }), 400

    # 5. VALIDAÇÃO BÁSICA DO PDF

    # PDFs normalmente começam com %PDF.
    if not file_data.startswith(b"%PDF"):
        return jsonify({
            "error": "O arquivo enviado não parece ser um PDF válido."
        }), 400

    # 6. GERAÇÃO DO HASH

    file_hash = generate_file_hash(file_data)

    # 7. VERIFICA SE O HASH JÁ EXISTE

    try:

        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT verification_code
                    FROM contracts
                    WHERE file_hash = %s;
                    """,
                    (file_hash,)
                )

                existing_contract = cur.fetchone()

        if existing_contract:

            return jsonify({
                "error": (
                    "Este arquivo já foi registrado no ProofFile."
                ),
                "verification_code": existing_contract[0]
            }), 409

    except Exception as error:

        print(
            f"ERRO AO VERIFICAR HASH EXISTENTE: {error}"
        )

        return jsonify({
            "error": (
                "Não foi possível verificar se o contrato "
                "já foi registrado."
            )
        }), 500

    # 8. GERA CÓDIGO DE VERIFICAÇÃO

    verification_code = generate_verification_code()

    # 9. GERA NOME DO ARQUIVO

    saved_filename = generate_saved_filename(
        file.filename
    )

    file_path = UPLOAD_FOLDER / saved_filename

    # 10. SALVA O ARQUIVO

    try:

        file_path.write_bytes(file_data)

    except Exception as error:

        print(
            f"ERRO AO SALVAR ARQUIVO: {error}"
        )

        return jsonify({
            "error": "Não foi possível salvar o arquivo."
        }), 500

    # 11. REGISTRA NA SOLANA

    try:

        solana_transaction = await register_on_solana(
            verification_code,
            file_hash
        )

    except Exception as error:

        # Se a Solana falhar, remove o arquivo que acabou
        # de ser salvo para evitar um arquivo órfão.
        if file_path.exists():
            file_path.unlink()

        print(
            f"ERRO AO REGISTRAR NA SOLANA: {error}"
        )

        return jsonify({
            "error": (
                "Não foi possível registrar o contrato "
                "na Solana."
            )
        }), 500

    # 12. SALVA NO POSTGRESQL

    registration_date = date.today()

    try:

        with psycopg.connect(DATABASE_URL) as conn:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    INSERT INTO contracts (
                        verification_code,
                        contract_name,
                        company_id,
                        user_id,
                        registration_date,
                        expiration_date,
                        file_path,
                        file_hash,
                        solana_transaction
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                    RETURNING id;
                    """,
                    (
                        verification_code,
                        contract_name,
                        1,
                        1,
                        registration_date,
                        expiration_date,
                        str(file_path),
                        file_hash,
                        solana_transaction
                    )
                )

                contract_id = cur.fetchone()[0]

    except psycopg.errors.UniqueViolation:

        # Se por algum motivo o banco detectar um conflito,
        # remove o arquivo salvo.
        if file_path.exists():
            file_path.unlink()

        print(
            "ERRO NO REGISTRO: conflito de registro único."
        )

        return jsonify({
            "error": (
                "O contrato já possui um registro "
                "ou ocorreu um conflito de código."
            )
        }), 409

    except Exception as error:

        # Remove o arquivo para evitar deixar um PDF
        # sem registro correspondente no banco.
        if file_path.exists():
            file_path.unlink()

        print(
            f"ERRO AO SALVAR NO POSTGRESQL: {error}"
        )

        return jsonify({
            "error": (
                "Não foi possível salvar o registro "
                "no banco de dados."
            )
        }), 500

    # 13. RETORNA RESULTADO

    return jsonify({
        "message": "Registro concluído!",
        "contract_id": contract_id,
        "verification_code": verification_code,
        "contract_name": contract_name,
        "registration_date": str(registration_date),
        "expiration_date": expiration_date,
        "file_hash": file_hash,
        "solana_transaction": solana_transaction
    }), 201

# CONSULTA DE CONTRATO PELO CÓDIGO

@app.route("/contract/<verification_code>")
def get_contract_by_code(verification_code):
    """
    Busca informações de um contrato usando seu código
    de verificação.
    """

    try:

        with psycopg.connect(DATABASE_URL) as conn:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        ct.contract_name,
                        cm.company_name,
                        u.name,
                        u.email,
                        ct.registration_date,
                        ct.expiration_date,
                        ct.file_path,
                        ct.file_hash,
                        ct.solana_transaction
                    FROM contracts AS ct
                    INNER JOIN users AS u
                        ON ct.user_id = u.id
                    INNER JOIN companies AS cm
                        ON ct.company_id = cm.id
                    WHERE ct.verification_code = %s;
                    """,
                    (verification_code,)
                )

                result = cur.fetchone()

        if result is None:

            return jsonify({
                "error": "Contrato não encontrado."
            }), 404

        (
            contract_name,
            company_name,
            user_name,
            user_email,
            registration_date,
            expiration_date,
            file_path,
            file_hash,
            solana_transaction
        ) = result

        return jsonify({
            "contract_name": contract_name,
            "company_name": company_name,
            "user_name": user_name,
            "user_email": user_email,
            "registration_date": str(registration_date),
            "expiration_date": (
                str(expiration_date)
                if expiration_date
                else None
            ),
            "file_path": file_path,
            "file_hash": file_hash,
            "solana_transaction": solana_transaction
        })

    except Exception as error:

        print(
            f"ERRO AO CONSULTAR CONTRATO: {error}"
        )

        return jsonify({
            "error": (
                "Não foi possível consultar o contrato."
            )
        }), 500

# ROTA DE VERIFICAÇÃO

@app.route("/verify", methods=["POST"])
async def verify_contract():
    """
    Verifica se o PDF enviado corresponde ao PDF
    originalmente registrado.

    Fluxo:

    PDF recebido
         ↓
    SHA-256
         ↓
    Busca pelo código
         ↓
    Compara hashes
         ↓
    Resultado
    """

    # 1. CÓDIGO DE VERIFICAÇÃO

    verification_code = request.form.get(
        "verification_code",
        ""
    ).strip()

    if not verification_code:

        return jsonify({
            "error": (
                "O código de verificação é obrigatório."
            )
        }), 400

    # 2. ARQUIVO

    file = request.files.get("file")

    validation_error = validate_pdf(file)

    if validation_error:

        return jsonify({
            "error": validation_error
        }), 400

    # 3. LEITURA DO ARQUIVO

    file_data = file.read()

    if not file_data:

        return jsonify({
            "error": "O arquivo enviado está vazio."
        }), 400

    # 4. HASH DO ARQUIVO RECEBIDO

    file_hash = generate_file_hash(file_data)

    # 5. BUSCA O REGISTRO

    try:

        with psycopg.connect(DATABASE_URL) as conn:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT
                        ct.contract_name,
                        cm.company_name,
                        u.name,
                        ct.registration_date,
                        ct.expiration_date,
                        ct.file_path,
                        ct.file_hash,
                        ct.solana_transaction
                    FROM contracts AS ct
                    INNER JOIN users AS u
                        ON ct.user_id = u.id
                    INNER JOIN companies AS cm
                        ON ct.company_id = cm.id
                    WHERE ct.verification_code = %s;
                    """,
                    (verification_code,)
                )

                result = cur.fetchone()

        # Código inexistente.
        if result is None:

            return jsonify({
                "error": (
                    "Código de verificação "
                    "não encontrado."
                )
            }), 404

        (
            contract_name,
            company_name,
            user_name,
            registration_date,
            expiration_date,
            file_path,
            registered_hash,
            solana_transaction
        ) = result

        # 6. COMPARAÇÃO

        matches = file_hash == registered_hash

        # 7. RESULTADO

        return jsonify({
            "verified": matches,
            "message": (
                "O contrato corresponde ao registro."
                if matches
                else
                "O contrato não corresponde ao registro."
            ),
            "verification_code": verification_code,
            "contract_name": contract_name,
            "company_name": company_name,
            "registration_date": str(registration_date),
            "expiration_date": (
                str(expiration_date)
                if expiration_date
                else None
            ),
            "file_hash": file_hash,
            "registered_hash": registered_hash,
            "solana_transaction": solana_transaction
        }), 200

    except Exception as error:

        print(
            f"ERRO NA VERIFICAÇÃO: {error}"
        )

        return jsonify({
            "error": (
                "Não foi possível realizar "
                "a verificação."
            )
        }), 500

# ACESSO AO PDF REGISTRADO

@app.route("/contract-file/<verification_code>")
def get_contract_file(verification_code):
    """
    Retorna o PDF originalmente registrado.
    """

    try:

        with psycopg.connect(DATABASE_URL) as conn:

            with conn.cursor() as cur:

                cur.execute(
                    """
                    SELECT file_path
                    FROM contracts
                    WHERE verification_code = %s;
                    """,
                    (verification_code,)
                )

                result = cur.fetchone()

        if result is None:

            return jsonify({
                "error": "Contrato não encontrado."
            }), 404

        file_path = Path(result[0])

        # Verifica se o arquivo realmente existe.
        if not file_path.exists():

            return jsonify({
                "error": (
                    "Arquivo do contrato "
                    "não encontrado."
                )
            }), 404

        return send_file(
            file_path,
            mimetype="application/pdf"
        )

    except Exception as error:

        print(
            f"ERRO AO ABRIR CONTRATO: {error}"
        )

        return jsonify({
            "error": (
                "Não foi possível abrir "
                "o contrato."
            )
        }), 500

#TRATAMENTO DE ARQUIVO GRANDE
@app.errorhandler(413)
def file_too_large(error):
    """
    Retorna uma mensagem amigável quando o arquivo
    ultrapassa o limite de 20 MB.
    """

    return jsonify({
        "error": (
            "O arquivo é muito grande. "
            "O tamanho máximo permitido é 20 MB."
        )
    }), 413

# INICIALIZAÇÃO

if __name__ == "__main__":

    # O debug facilita o desenvolvimento.
    #
    # use_reloader=False evita que o Flask reinicie
    # automaticamente quando um PDF é criado dentro
    # da pasta Backend/uploads.
    app.run(
        debug=True,
        use_reloader=False
    )