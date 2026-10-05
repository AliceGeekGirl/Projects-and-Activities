#Importa o Flask, que será usado para criar o servidor da aplicação.
#O jsonify será usado para transformar o resultado da consulta em uma resposta JSON.
#O request permite que o Flask acesse os dados enviados pelo navegador, incluindo o arquivo.
from flask import Flask, jsonify, request

#Importa a função que carrega as variáveis de configuração armazenadas no arquivo .env.
from dotenv import load_dotenv

#Importa o acesso a variáveis de ambiente do sistema, como a DATABASE_URL que colocamos no .env.
import os

#Importa uma biblioteca que permite ao Python se comunicar com um banco PostgreSQL.
import psycopg

#O hashlib é a biblioteca do Python que permite calcular o hash.
import hashlib

#O uuid será usado para gerar um código de verificação único.
import uuid

#Carrega as informações que estão no arquivo .env para que o Python possa acessá-las como variáveis de ambiente.
load_dotenv()

#Cria a aplicação Flask.
app = Flask(__name__) # __name__ identifica o arquivo atual para o Flask.

#Pega do ambiente a variável DATABASE_URL. Essa variável contém as informações necessárias para o Python se conectar ao PostgreSQL do Neon.
DATABASE_URL = os.getenv("DATABASE_URL")

#Define a pasta onde os contratos enviados serão armazenados.
UPLOAD_FOLDER = "Backend/Uploads"

#Informa ao Flask qual pasta será usada para salvar os arquivos.
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

#Cria a rota "/db". Essa rota será usada para testar a comunicação entre o Flask/Python e o banco PostgreSQL.
@app.route("/db")
def test_database():

    #Abre uma conexão com o PostgreSQL usando a configuração que veio do arquivo .env.
    conn = psycopg.connect(DATABASE_URL)

    #Cria um cursor para enviar comandos SQL para o banco de dados.
    cur = conn.cursor()

    #Executa uma consulta SQL simples. Estamos usando SELECT 1 apenas para testar se a comunicação com o banco está funcionando.
    cur.execute("SELECT 1;")

    #Pega a primeira linha do resultado da consulta.
    result = cur.fetchone() #Esperamos receber algo como (1,).

    #Fecha o cursor porque terminamos de executarc omandos SQL nesta conexão.
    cur.close()

    #Fecha a conexão com o banco para liberar o recurso.
    conn.close()

    #Envia o resultado da consulta para o navegador.
    return f"Resultado do banco: {result}"

#Rota que busca os contratos cadastrados no ProofFile.
@app.route("/contract/<verification_code>")
def get_contract_by_code(verification_code):

    #Abre a conexão com o PostgreSQL.
    conn = psycopg.connect(DATABASE_URL)

    #Cria o cursor para executar o SQL.
    cur = conn.cursor()

    #Busca o contrato correspondente ao código informado na URL.
    cur.execute("""
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
    """, (verification_code,))

    #Pega o primeiro registro encontrado.
    result = cur.fetchone()

    #Fecha o cursor e a conexão.
    cur.close()
    conn.close()

    #Verifica se o código não existe no banco.
    if result is None:
        return "Contrato não encontrado.", 404

    #Retorna os dados encontrados.
    return jsonify(result)

@app.route("/hash", methods=["POST"])
def generate_hash():
    # Verifica se um arquivo foi enviado na requisição
    if "file" not in request.files:
        return "Nenhum arquivo foi enviado.", 400

    # Pega o arquivo enviado
    file = request.files["file"]

    # Lê o conteúdo do arquivo em bytes
    file_data = file.read()

    # Cria o hash SHA-256 usando o conteúdo do arquivo
    file_hash = hashlib.sha256(file_data).hexdigest()

    # Mostra algumas informações para conferirmos o resultado
    return jsonify({
        "file_name": file.filename,
        "file_hash": file_hash
    })

@app.route("/register", methods=["POST"])
def register_contract():

    # Verifica se o formulário enviou um arquivo.
    if "file" not in request.files:
        return "Nenhum arquivo foi enviado.", 400

    # Pega o arquivo enviado pelo formulário.
    file = request.files["file"]

    # Verifica se o usuário realmente escolheu um arquivo.
    if file.filename == "":
        return "Nenhum arquivo foi selecionado.", 400

    # Pega o nome do contrato enviado pelo formulário.
    contract_name = request.form.get("contract_name")

    # Verifica se o nome do contrato foi informado.
    if not contract_name:
        return "O nome do contrato é obrigatório.", 400

    # Pega a data de expiração enviada pelo formulário.
    expiration_date = request.form.get("expiration_date")

    # Define a data de registro automaticamente.
    from datetime import date
    registration_date = date.today()

    # Lê o conteúdo do PDF em bytes.
    file_data = file.read()

    # Calcula o hash SHA-256 do arquivo.
    file_hash = hashlib.sha256(file_data).hexdigest()

    # Gera um código único para a verificação do contrato.
    verification_code = "PF-" + uuid.uuid4().hex[:8].upper()

    # Define o caminho onde o PDF será salvo.
    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    # Volta o ponteiro do arquivo para o início.
    file.seek(0)

    # Salva o PDF na pasta uploads.
    file.save(file_path)

    # Abre uma conexão com o PostgreSQL.
    conn = psycopg.connect(DATABASE_URL)

    # Cria um cursor para executar o INSERT.
    cur = conn.cursor()

    # Insere o contrato no banco.
    cur.execute("""
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
    """, (
        verification_code,
        contract_name,
        1,
        1,
        registration_date,
        expiration_date if expiration_date else None,
        file_path,
        file_hash,
        "PENDING_SOLANA"
    ))

    # Pega o ID gerado para o contrato.
    contract_id = cur.fetchone()[0]

    # Confirma a alteração no banco.
    conn.commit()

    # Fecha o cursor.
    cur.close()

    # Fecha a conexão.
    conn.close()

    # Retorna os dados do registro.
    return jsonify({
        "message": "Contrato registrado com sucesso.",
        "contract_id": contract_id,
        "verification_code": verification_code,
        "contract_name": contract_name,
        "registration_date": registration_date.isoformat(),
        "expiration_date": expiration_date,
        "file_path": file_path,
        "file_hash": file_hash,
        "solana_transaction": "PENDING_SOLANA"
    })

#Inicia o servidor quando este arquivo é executado diretamente.
if __name__ == "__main__":
    app.run(debug=True)