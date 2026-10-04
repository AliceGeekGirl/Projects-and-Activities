#Importa o Flask, que será usado para criar o servidor da aplicação.
from flask import Flask

# Importa a função que carrega as variáveis de configuração armazenadas no arquivo .env.
from dotenv import load_dotenv

# Permite acessar variáveis de ambiente do sistema, como a DATABASE_URL que colocamos no .env.
import os

# Biblioteca que permite ao Python se comunicar com um banco PostgreSQL.
import psycopg

# Carrega as informações que estão no arquivo .env para que o Python possa acessá-las como variáveis de ambiente.
load_dotenv()

# Cria a aplicação Flask.
app = Flask(__name__) # __name__ identifica o arquivo atual para o Flask.

# Pega do ambiente a variável DATABASE_URL. Essa variável contém as informações necessárias para o Python se conectar ao PostgreSQL do Neon.
DATABASE_URL = os.getenv("DATABASE_URL")

#Cria a rota principal "/". Quando o navegador acessar http://127.0.0.1:5000/, o Flask executará a função home().
@app.route("/")
def home():

    # Retorna uma mensagem simples para confirmar que a aplicação Flask está funcionando.
    return "Olá, ProofFile!"

# Cria a rota "/db". Essa rota será usada para testar a comunicação entre o Flask/Python e o banco PostgreSQL.
@app.route("/db")
def test_database():

    # Abre uma conexão com o PostgreSQL usando a configuração que veio do arquivo .env.
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


#Verifica se este arquivo está sendo executado diretamente. Se estiver, inicia o servidor Flask.
if __name__ == "__main__":

    #Inicia o servidor e ativa o modo debug, que facilita o desenvolvimento e mostra erros durante os testes.
    app.run(debug=True)