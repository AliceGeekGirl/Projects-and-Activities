"""
OCP — Aberto/Fechado
Cenário errado
Crie uma função de desconto que usa if e elif para cada tipo de cliente:

cliente comum;
cliente VIP;
cliente premium.

Sempre que surgir um novo tipo, você vai precisar alterar a função.

Cenário correto
Crie uma classe base Desconto e classes filhas como:

DescontoComum;
DescontoVIP;
DescontoPremium.

O que observar
Na versão correta, você adiciona novos comportamentos sem mexer no código antigo.
"""

"""
MÉTODO ERRADO: 
"""

"""
#Criando uma função rígida que viola o Princípio Aberto/Fechado (OCP)
def desconto(tipo_cliente, valor):

    #Usa uma estrutura de escolhas para decidir a porcentagem do desconto
    if tipo_cliente == "comum":
        return valor * 0.05  #5% de desconto para cliente comum
    elif tipo_cliente == "VIP":
        return valor * 0.10  #10% de desconto para cliente VIP
    elif tipo_cliente == "Premium":
        return valor * 0.15  #15% de desconto para cliente Premium
    
    #Caso o tipo digitado não exista nos 'ifs' acima, avisa e não aplica desconto
    else:
        print(f"Aviso: Tipo de cliente '{tipo_cliente}' não reconhecido.")
        return 0.0

#Recebe o valor total da compra do usuário e converte para número decimal (float)
valor= float(input("Qual o seu valor: "))

#Recebe a categoria do cliente
tipo= input("Que tipo de cliente é você: ")

#Chama a função de desconto e exibe o valor retornado formatado com 2 casas decimais
print(f"Desconto: R$ {desconto(tipo, valor):.2f}")

#O PROBLEMA DESTE MÉTODO (POR QUE ESTÁ "ERRADO"?):

#Se a loja criar um cliente 'estudante' ou 'funcionario', a chamada: desconto('estudante', valor) vai falhar e retornar R$ 0.00 até que você Venha AQUI e ABRA esta função para adicionar um novo 'elif'
"""
"""
MÉTODO CERTO:

O que é Herança (Classes Filhas)?
Quando colocamos 'class DescontoComum(Desconto):', estamos dizendo que DescontoComum 
é uma "filha" de Desconto. Ela herda tudo o que a classe pai tem, mas pode 
modificar (sobrescrever) métodos para ter seu próprio comportamento.
"""

#Criando o molde base para os tipos de desconto (CLASSE PAI/MÃE)
class Desconto:
    
    #Método padrão: caso uma classe filha não crie seu próprio cálculo, essa função base retorna 0.0
    def calcular(self, valor):
        return 0.0

#'DescontoComum' (CLASSE FILHA) HERDA de 'Desconto'. Ela copia tudo da mãe, mas altera o método 'calcular'
class DescontoComum(Desconto):

    #Sobrescreve (substitui) o método 'calcular' para aplicar a regra do cliente Comum
    def calcular(self, valor):
        return valor * 0.05  #5% de desconto para cliente comum

#'DescontoVIP' também é uma classe filha de 'Desconto', ou seja, herda (copia) tudo e altera o método
class DescontoVIP(Desconto):

    #Sobrescreve (substitui) o método 'calcular' para aplicar a regra do cliente VIP
    def calcular(self, valor):
        return valor * 0.10  #10% de desconto para cliente VIP

#'DescontoPremium' é outra classe filha de 'Desconto', ou seja, herda (copia) tudo e altera o método
class DescontoPremium(Desconto):

    #Sobrescreve (substitui) o método 'calcular' para aplicar a regra do cliente Premium
    def calcular(self, valor):
        return valor * 0.15  #15% de desconto para cliente Premium

#E SE SURGIR UM NOVO TIPO? (EXTENSÃO)
#Basta criar a nova classe abaixo, SEM MEXER nas de cima!

#'DescontoEstudante' nasce como filha de 'Desconto' com sua própria regra
class DescontoEstudante(Desconto):

    #Sobrescreve (substitui) o método 'calcular' para aplicar a regra do cliente Estudante
    def calcular(self, valor):
        return valor * 0.08 #8% de desconto para estudante

#Recebe o valor total da compra do usuário e converte para número decimal (float)
valor= float(input("Qual o seu valor: "))

#Dicionário que associa o nome do tipo ao objeto da classe filha correspondente
tipos_desconto = {
    "comum": DescontoComum(),  #Guarda uma instância (objeto) da classe DescontoComum
    "VIP": DescontoVIP(),       #Guarda uma instância (objeto) da classe DescontoVIP
    "Premium": DescontoPremium(),  #Guarda uma instância (objeto) da classe DescontoPremium
    "estudante": DescontoEstudante() #Guarda uma instância (objeto) da classe DescontoEstudante
}

#Recebe a categoria do cliente
tipo= input("Que tipo de cliente você é (comum, VIP, Premium, estudante): ")

#Busca no dicionário o objeto correto do tipo digitado. Se o usuário digitar algo errado, pega 'Desconto()' por padrão
calculador = tipos_desconto.get(tipo, Desconto())

#O 'calculador' chama o método 'calcular' do objeto encontrado e é atribuído a 'valor_desconto' (Polimorfismo: o Python executa o 'calcular' da classe filha certa)
valor_desconto = calculador.calcular(valor)

#Exibe o valor do desconto formatado com 2 casas decimais
print(f"Desconto: R$ {valor_desconto:.2f}")