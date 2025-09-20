# models/conta.py
from datetime import datetime


class Conta:
    def __init__(self, numero_conta, agencia, tipo_conta, id=None, saldo=0.0,  cpf=None, cnpj =None, situacao_conta=1, data_abertura=None):
        """
        Conta bancária.
        situacao_conta:
        - 1 = ativa
        - 0 = inativa
        """
        
        self.numero_conta = numero_conta
        self.agencia = agencia
        self.saldo = saldo
        self.tipo_conta = tipo_conta
        self.id = id
        self.cpf = cpf  # FK para cliente (CPF ou CNPJ)
        self.cnpj = cnpj 
        self.situacao_conta = situacao_conta
        self.data_abertura = data_abertura or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return (f"<Conta id={self.id}, numero_conta={self.numero_conta}, agencia={self.agencia}, "
                f"cpf={self.cpf}, saldo={self.saldo:.2f}, situacao={self.situacao_conta}>")



#teste = Conta(numero_conta="12345-6", agencia="0001", tipo_conta="CORRENTE", cpf="123.456.789-00")
#print(teste)