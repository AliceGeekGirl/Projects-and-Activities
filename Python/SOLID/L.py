"""
LSP — Substituição de Liskov
Cenário errado
Crie uma classe Ave com método voar(). Depois crie uma classe Pinguim herdando de Ave, mas o pinguim não voa.

Cenário correto
Refatore para algo como:

classe Ave;

classe AveQueVoa;

classe Pinguim.

O que observar
A subclasse não pode quebrar o comportamento esperado da classe pai.
"""

"""
MÉTODO ERRADO:
"""

"""
#Criando o molde de Ave (Classe Pai)
class Ave:
    #Método construtor simples da classe Ave
    def __init__(self):
        pass #Não faz nada, apenas mantém a sintaxe válida.

    #Método que diz que voou
    def voar(self):
        print("Voou!")

#Criando a molde Pinguim que herda de 'Ave' (Classe Filha) 
class Pinguim(Ave):

    #Sobrescreve o método 'voar' da classe pai, mas deixamos vazio ('pass') porque pinguim não voa
    def voar(self):
        pass #AQUI ESTÁ O ERRO DO LSP: A classe filha anula/desativa uma funcionalidade do pai!

#Instancia (cria) um objeto da classe pai 'Ave'
ave= Ave()

#Instancia (cria) um objeto da classe filha 'Pinguim'
pinguim= Pinguim()

#Chamando o método voar para o pinguim
pinguim.voar() #Não faz nada
"""

"""
MÉTODO CERTO:
"""

#Criando o molde de Ave (Classe Pai)
class Ave:
    #Método construtor simples da classe Ave
    def __init__(self, nome):
        self.nome = nome #Salva o nome da ave

    #Comportamento que TODA ave tem (voando ou não)
    def emitir_som(self):
        print(f"{self.nome} está emitindo um som!")

#Criando a molde 'AveQueVoa' que herda de 'Ave' (Classe Filha) 
class AveQueVoa(Ave):
    def voar(self):
        print(f"{self.nome} voou!")

#Criando a molde Pinguim que herda de 'Ave' (Classe Filha) 
class Pinguim(Ave):

    #Comportamento específico do pinguim
    def nadar(self):
        print(f"{self.nome} está nadando na água gelada!")

#Instancia (cria) um Pinguim (é uma Ave, mas não é uma AveQueVoa)
pinguim = Pinguim("Pinguim")

#Instancia (cria) uma Ave que Voa (ex: Águia)
aguia = AveQueVoa("Águia")

#Ambas conseguem emitir som, pois herdam da classe pai 'Ave'
pinguim.emitir_som()
aguia.emitir_som()

#Apenas a Águia consegue voar (Pinguim nem possui o método 'voar', evitando chamadas inválidas)
aguia.voar()

#Apenas o Pinguim consegue nadar
pinguim.nadar()