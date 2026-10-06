#Importa o Flask para criar o servidor web, o jsonify para retornar respostas em JSON e o request para acessar os dados enviados pelo Frontend.
from flask import Flask, jsonify, request

from flask_cors import CORS

#Importa a função que carrega as variáveis armazenadas no arquivo .env.
from dotenv import load_dotenv

#Importa date para registrar automaticamente a data em que o contrato foi cadastrado.
from datetime import date

#Importa Path para trabalhar com caminhos de arquivos e criar a pasta de uploads.
from pathlib import Path

#Importa os para acessar variáveis de ambiente, como as configurações do .env.
import os

#Importa json para transformar a chave privada armazenada no .env em uma lista de números.
import json

#Importa uuid para gerar identificadores únicos para os códigos e nomes dos arquivos.
import uuid

#Importa hashlib para calcular o hash SHA-256 dos arquivos enviados.
import hashlib

#Importa Keypair para reconstruir a carteira Solana a partir da chave privada.
from solders.keypair import Keypair

#Importa Pubkey para representar o endereço público de um programa ou carteira Solana.
from solders.pubkey import Pubkey

#Importa Instruction para criar a instrução que será enviada ao Memo Program.
from solders.instruction import Instruction

#Importa Message para montar a mensagem que fará parte da transação.
from solders.message import Message

#Importa Transaction para criar e assinar a transação Solana.
from solders.transaction import Transaction

#Importa AsyncClient para enviar requisições de forma assíncrona para a Solana Devnet.
from solana.rpc.async_api import AsyncClient

#Carrega as variáveis de ambiente que estão no arquivo .env.
load_dotenv()

#Cria a aplicação Flask.
app = Flask(__name__)

#Pega a URL de conexão do PostgreSQL armazenada no .env.
DATABASE_URL = os.getenv("DATABASE_URL")

#Pega a URL da Solana Devnet armazenada no .env.
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL")

#Define onde os arquivos PDF enviados serão armazenados.
UPLOAD_FOLDER = Path("Backend/uploads")

#Cria a pasta uploads caso ela ainda não exista.
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

#Define o tamanho máximo permitido para o arquivo enviado.
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024 #Neste caso, o sistema permite arquivos de até 20 MB.

#Define o endereço oficial do Memo Program que receberá os dados que queremos registrar na transação da Solana.
MEMO_PROGRAM_ID = Pubkey.from_string(
    "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"
)

#Recupera a carteira Solana a partir da chave privada armazenada no .env. Essa função é usada sempre que o Backend precisa assinar uma transação antes de enviá-la para a Solana.
def get_keypair():

    #Pega a chave privada armazenada no arquivo .env.
    private_key_text = os.getenv("SOLANA_PRIVATE_KEY")

    #Verifica se a chave privada foi configurada antes de tentar reconstruir a carteira Solana.
    if not private_key_text:
        raise ValueError(
            "SOLANA_PRIVATE_KEY não foi encontrada no .env."
        )

    #Converte o texto JSON armazenado no .env para uma lista de números.
    private_key = json.loads(private_key_text)

    #Converte a lista de números para bytes e usa esses bytes para reconstruir exatamente a carteira Solana que será usada para assinar as transações.
    return Keypair.from_bytes(bytes(private_key))

#Registra o código de verificação e o hash do contrato na Solana Devnet.
#A função cria uma transação usando o Memo Program e retorna a assinatura da transação, que será armazenada posteriormente no PostgreSQL.
async def register_on_solana(verification_code, file_hash):

    #Cria uma conexão com a Solana Devnet. O bloco async with garante que a conexão seja fechada ao terminar.
    async with AsyncClient(SOLANA_RPC_URL) as client:

        #Recupera a carteira que será usada para assinar a transação.
        keypair = get_keypair()

        #Monta o texto que será registrado pelo Memo Program. O código identifica o registro e o hash identifica o conteúdo do contrato.
        memo_data = (
            f"PROOFFILE|{verification_code}|HASH:{file_hash}" #O PDF em si não será enviado para a blockchain.
        )

        #Cria uma instrução para o Memo Program contendo o código de verificação e o hash do contrato.
        instruction = Instruction(
            program_id=MEMO_PROGRAM_ID,
            accounts=[],
            data=memo_data.encode("utf-8")
        )

        #Busca um blockhash recente, que é necessário para criar uma transação válida na rede Solana.
        blockhash_response = await client.get_latest_blockhash()

        #Pega o blockhash retornado pela Solana.
        recent_blockhash = blockhash_response.value.blockhash

        #Monta a mensagem da transação usando a instrução do Memo, a carteira que está assinando e o blockhash obtido recentemente.
        message = Message.new_with_blockhash(
            [instruction],
            keypair.pubkey(),
            recent_blockhash
        )

        #Cria a transação usando a mensagem preparada anteriormente. A Keypair fornece a assinatura digital necessária para provar que essa carteira autorizou o envio da transação.
        transaction = Transaction(
            [keypair],
            message,
            recent_blockhash
        )

        #Envia a transação assinada para a Solana Devnet.
        response = await client.send_transaction(transaction)

        #Retorna a assinatura que identifica a transação na blockchain.
        return str(response.value)

#Cria a rota /db para testar se o Backend consegue se conectar corretamente ao banco de dados PostgreSQL.
@app.route("/db")

#Testa a conexão entre o Backend e o PostgreSQL executando uma consulta simples. Essa função é usada apenas para verificar se a comunicação com o banco está funcionando corretamente.
def test_database():

    #Importa o psycopg, que permite que o Python se comunique com o PostgreSQL.
    import psycopg

    #Abre uma conexão com o PostgreSQL usando a URL armazenada no .env.
    conn = psycopg.connect(DATABASE_URL)

    #Cria um cursor para executar comandos SQL no banco.
    cur = conn.cursor()

    #Executa uma consulta simples apenas para verificar se a conexão com o banco de dados está funcionando.
    cur.execute("SELECT 1;")

    #Pega o resultado retornado pela consulta.
    result = cur.fetchone()

    #Fecha o cursor depois de terminar a consulta.
    cur.close()

    #Fecha a conexão com o PostgreSQL.
    conn.close()

    #Retorna o resultado em JSON para confirmar que o banco está funcionando.
    return jsonify(result)

#Cria a rota /hash para receber um arquivo enviado pelo Frontend e gerar o hash SHA-256 desse arquivo.
@app.route("/hash", methods=["POST"]) #O método POST é usado porque estamos enviando um arquivo para o Backend.

#Recebe um arquivo enviado pelo Frontend e calcula seu hash SHA-256. Essa função foi criada inicialmente para testar o funcionamento do hash antes de integrá-lo ao cadastro completo do contrato.
def generate_hash():

    #Verifica se o formulário recebeu um arquivo.
    if "file" not in request.files:
        return "Nenhum arquivo foi enviado.", 400

    #Pega o arquivo enviado pelo usuário.
    file = request.files["file"]

    #Lê o conteúdo do arquivo em bytes para que ele possa ser processado.
    file_data = file.read()

    #Calcula o hash SHA-256 do conteúdo do arquivo.
    file_hash = hashlib.sha256(file_data).hexdigest() #Esse valor funciona como uma identificação matemática do conteúdo do PDF.

    #Retorna o nome e o hash do arquivo em formato JSON.
    return jsonify({
        "file_name": file.filename,
        "file_hash": file_hash
    })

#Cria a rota /register para realizar o cadastro completo de um contrato.
#Essa rota recebe o PDF e os dados do contrato, calcula o hash, registra a informação na Solana e salva os dados no PostgreSQL.
@app.route("/register", methods=["POST"]) #O método POST é usado porque estamos enviando dados para criar um novo registro.

#Realiza o cadastro completo de um contrato no ProofFile. A função recebe o PDF, calcula seu hash, gera o código de verificação, registra o hash na Solana, salva o arquivo e registra os dados no PostgreSQL.
async def register_contract():

    #Importa o psycopg usado para permitir que o Python execute comandos no PostgreSQL.
    import psycopg

    #Verifica se o formulário recebeu um arquivo.
    if "file" not in request.files:
        return jsonify({
            "error": "Nenhum arquivo foi enviado."
        }), 400

    #Pega o arquivo enviado pelo usuário.
    file = request.files["file"]

    #Verifica se o usuário realmente selecionou um arquivo.
    if file.filename == "":
        return jsonify({
            "error": "Nenhum arquivo foi selecionado."
        }), 400

    #Pega o nome ou identificação do contrato enviado pelo formulário.
    contract_name = request.form.get("contract_name")

    # Verifica se o nome do contrato foi informado.
    if not contract_name:
        return jsonify({
            "error": "O nome do contrato é obrigatório."
        }), 400

    #Pega a data de expiração caso o usuário tenha informado uma.
    expiration_date = request.form.get("expiration_date") #Caso contrário, o valor será vazio e depois será salvo como NULL.

    #Lê o conteúdo do PDF antes de salvá-lo.
    file_data = file.read()

    #Calcula o hash SHA-256 do conteúdo do PDF.
    file_hash = hashlib.sha256(file_data).hexdigest() #Esse hash será usado como representação matemática do conteúdo do contrato e também será registrado na Solana.

    #Gera um código único que será entregue ao cliente.
    verification_code = (
        "PF-" + uuid.uuid4().hex[:8].upper() #Esse código permitirá localizar posteriormente o registro correspondente no PostgreSQL.
    )

    #Cria um nome único para o arquivo armazenado.
    saved_filename = (
        f"{uuid.uuid4().hex}_{file.filename}" #O UUID evita que dois contratos com o mesmo nome sobrescrevam um arquivo que já esteja na pasta uploads.
    )

    #Define o caminho onde o PDF será armazenado.
    file_path = UPLOAD_FOLDER / saved_filename

    #Salva o PDF dentro da pasta uploads.
    file_path.write_bytes(file_data)

    try:
        #Registra primeiro o hash e o código na Solana.
        #Fazemos isso antes do INSERT no PostgreSQL porque a coluna solana_transaction é obrigatória e precisa receber a assinatura real da transação, e não mais o valor temporário PENDING_SOLANA.
        solana_transaction = await register_on_solana(
            verification_code,
            file_hash
        )

        #Abre a conexão com o PostgreSQL somente depois que a transação da Solana foi criada com sucesso.
        conn = psycopg.connect(DATABASE_URL)

        #Cria um cursor para executar o INSERT do contrato.
        cur = conn.cursor()

        #Insere o contrato usando os IDs de teste que já existem nas tabelas users e companies.
        #Nesta etapa do MVP ainda estamos usando esses registros fixos para testar a integração do cadastro.
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
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id;
            """,
            (
                verification_code,
                contract_name,
                1,
                1,
                date.today(),
                expiration_date if expiration_date else None,
                str(file_path),
                file_hash,
                solana_transaction
            )
        )

        #Pega o ID gerado pelo PostgreSQL para identificar o novo contrato cadastrado.
        contract_id = cur.fetchone()[0]

        #Confirma definitivamente o INSERT no banco.
        conn.commit()

        #Fecha o cursor depois de terminar a operação.
        cur.close()

        #Fecha a conexão com o PostgreSQL.
        conn.close()
        
    except Exception as error:
        # Mostra o erro completo no terminal do Flask.
        # Isso permite identificar exatamente qual etapa do cadastro falhou.
        print(f"ERRO NO REGISTRO: {error}")

        # Retorna o erro também para o Frontend em formato JSON.
        return jsonify({
            "error": str(error)
        }), 500

    #Retorna os dados principais do registro para que o Frontend possa mostrar ao usuário que o contrato foi registrado, incluindo o código de verificação e a assinatura da transação Solana.
    return jsonify({
        "message": "Registro concluído!",
        "contract_id": contract_id,
        "verification_code": verification_code,
        "contract_name": contract_name,
        "registration_date": str(date.today()),
        "expiration_date": expiration_date,
        "file_hash": file_hash,
        "solana_transaction": solana_transaction
    }), 201

#Cria a rota /contract/<verification_code> para buscar um contrato usando o código de verificação informado na URL.
#Essa rota utiliza o método GET, que é o comportamento padrão do Flask, porque estamos apenas consultando informações que já estão cadastradas.
@app.route("/contract/<verification_code>")

#Busca no PostgreSQL os dados de um contrato usando seu código de verificação. Essa função será utilizada posteriormente pelo processo de verificação para localizar o registro original do contrato.
def get_contract_by_code(verification_code):
    
    #Importa o psycopg para permitir que o Python consulte o PostgreSQL.
    import psycopg

    #Abre uma conexão com o banco.
    conn = psycopg.connect(DATABASE_URL)

    #Cria um cursor para executar a consulta SQL.
    cur = conn.cursor()

    #Busca o contrato usando o código de verificação informado.
    #Os INNER JOINs permitem recuperar também os dados relacionados ao usuário e à empresa responsáveis pelo registro.
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

    #Pega o primeiro resultado encontrado.
    result = cur.fetchone()

    #Fecha o cursor depois da consulta.
    cur.close()

    #Fecha a conexão com o PostgreSQL.
    conn.close()

    #Informa que o contrato não existe caso nenhum registro seja encontrado.
    if result is None:
        return "Contrato não encontrado.", 404

    #Retorna os dados encontrados em formato JSON.
    return jsonify(result)

 #Verifica se este arquivo app.py está sendo executado diretamente pelo Python. Essa condição evita que o servidor seja iniciado automaticamente caso o arquivo seja importado por outro arquivo do projeto
if __name__ == "__main__":

    #Inicia o servidor Flask quando este arquivo é executado diretamente.
    app.run(debug=True)  #O modo debug facilita o desenvolvimento porque mostra erros detalhados e reinicia o servidor quando o código é alterado.