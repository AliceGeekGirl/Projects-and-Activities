from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

#cria app
app = Flask(__name__)

#cria rota /
@app.route("/")

#rota chama função
def home():
    return "Olá, ProofFile!" #função retorna resposta

#inicia servidor
if __name__ == "__main__":
    app.run(debug=True)