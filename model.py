from abc import ABC,abstractclassmethod,abstractproperty
from datetime import datetime
import textwrap

date = datetime

class Cliente:
    def __init__(self,endereco):
        self.endereco = str(endereco)
        self.contas = []

    def realizar_transacao(self,conta,transacao):
        transacao.registrar(conta)

    def adicionar_conta(self,conta):
        self.contas.append(conta)
        
class PessoaFisica(Cliente):

    def __init__(self,endereco,nome, data_nascimento, cpf):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento


class Conta:
    def __init__(self,numero,cliente):
        self._saldo = 0
        self._numero = int(numero)
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls,cliente,numero):
        return cls(numero,cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    
    def sacar(self,valor):
        saldo = self._saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("Operação inválida\nSaldo insuficiente") 

        elif valor > 0:
            self._saldo -= valor
            print("Saque realizado com sucesso")
            return True
        else:
            print("Valor informado é inválido")

        return False

    def depositar(self,valor):
        if valor > 0:
            self._saldo += valor
            print("Valor depositado com sucesso")
            
        else:
            print("Operação falhou valor inválido")
            return False
        
        return True
    
    def __str__(self) -> str:
        return f"Agencia{self.agencia}\nNúmero da conta:{self.__numero}"        
       
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite =500,limite_saques = 3):
        super().__init__( numero, cliente)
        self.__limite = limite
        self.__limite_saques = limite_saques

    def sacar(self,valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]       )
        
        excedeu_limite = valor > self.__limite
        excedeu_saques = numero_saques >= self.__limite_saques

        if excedeu_limite:
            print("Falha na operação, valor do saque excede o limite")
        elif excedeu_saques:
            print("Falha na operação,Excedeu o limite de saques")
        else:
            return super().sacar(valor)
        
        return False

    def __str__(self):
        return f" Agência:{self.agencia}\nC/C: {self.numero}\nTitular:{self.cliente.nome}"
    
class Historico:
    def __init__(self):
        self.__transacoes = []
    
    @property
    def transacoes(self):
      return self.__transacoes
    
    def adicionar_transacao(self, transacao):
         self.__transacoes.append(
           {
               "tipo":transacao.__class__.__name__,
               "valor":transacao.valor,
               "data": datetime.now().strftime("%d-%m-%Y %H:%M%S")
           }

       ) 

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    def registrar(self,conta):
        pass

class Saque(Transacao):
    def __init__(self,valor):
        self._valor = float(valor)

    @property
    def valor(self):
        return self._valor

    def registrar(self,conta):
        sucesso_transacao = conta.sacar(self._valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):

    def __init__(self,valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self,conta):
        sucesso_transacao = conta.depositar(self.valor)
    
        if sucesso_transacao:
            return conta.historico


def menu():
    menu = """
    ===========MENU===========
    1...Depositar
    2...Sacar
    3...Extrato
    4...Nova Conta
    5...Listar Contas
    6...Novo úsuario
    7...Sair =>
    """
    
    return int(input(menu))

def filtrar_cliente(cpf,clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]

    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("Cliente não possui contas")
        return
    
    return cliente.contas[0]

def depositar(clientes):
    cpf = input("Digite o CPF do cliente:")
    cliente = filtrar_cliente(cpf,clientes)

    if not cliente:
        print("Cliente não encontrado")
        return False
    
    valor = float(input("Informe o valor do depósito:"))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta,transacao)

def sacar(clientes):
    cpf = input("Digite seu CPF:")
    cliente = filtrar_cliente(cpf,clientes)

    if not cliente:
        print("Cliente não encontrado")
        return
    
    valor = float(input("Digite o valor que deseja sacar:"))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)


    cliente.realizar_transacao(conta,transacao)

def extrato(clientes):
    cpf = input("Digite o seu CPF:")
    cliente = filtrar_cliente(cpf,clientes)

    if not cliente:
        print("Cliente não encontrado")
        
        return

    conta = recuperar_conta_cliente(cliente)

    print("==========EXTRATO==========")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        print("Não foram realizadas transações")
    else:
        for transacao in transacoes:
            extrato+= f"{transacao["tipo"]} \nR${transacao["valor"]:.2f}"
        
    print(extrato)
    print(f"\nsaldo:\n R$ {conta.saldo:.2f}")

def criar_cliente(clientes):
    cpf = input("Digite o CPF:")
    cliente = filtrar_cliente(cpf,clientes)

    if cliente:
        print("Já existe um cliente com esse CPF")
        return
    
    nome = input("Digite o seu nome")
    data_nascimento = input("Informe sua data de nascimento (dd-mm-aaaa)")
    endereco = input("Informe seu endereço (logradouro - bairro -cidade/sigla estado):")
    cliente = PessoaFisica(nome= nome,data_nascimento=data_nascimento,cpf = cpf, endereco=endereco)

    clientes.append(cliente)
    print("Cliente criado com sucesso")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Digite seu cpf:")
    cliente = filtrar_cliente(cpf,clientes)
    
    if not cliente:
        print("Cliente não encontrado")
        return

    conta = ContaCorrente.nova_conta(cliente, numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("Conta criada com sucesso")

def listar_contas(contas):
    for conta in contas:
        print("=" *95)
        print(textwrap.dedent(str(conta)))

def main():
    clientes = []
    contas = []

    while True:
        
        escolha = menu()

        if escolha == 1:
            depositar(clientes)
        elif escolha == 2:
            sacar(clientes)
        elif escolha == 3:
            extrato(clientes)
        elif escolha == 4:
            numero_conta = int(input("Digite o número da conta:"))
            criar_conta(numero_conta,clientes,contas)
        elif escolha == 5:
            listar_contas(contas)
        elif escolha == 6:
            criar_cliente(clientes)
        elif escolha == 7:
             break

main()