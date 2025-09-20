# models/cliente.py
from datetime import datetime


class ClientePF:
    def __init__(self, id=None, cpf=None, nome=None, endereco=None, situacao_cliente=1, data_cadastro=None):
        """
        Cliente Pessoa Física
        situacao_cliente:
        - 1 = ativo
        - 0 = inativo
        """
        self.id = id
        self.cpf = cpf
        self.nome = nome
        self.endereco = endereco
        self.situacao_cliente = situacao_cliente
        self.data_cadastro = data_cadastro or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return (f"<ClientePF id={self.id}, cpf={self.cpf}, nome={self.nome}, "
                f"endereco={self.endereco}, situacao={self.situacao_cliente}>")

    def ativar(self):
        self.situacao_cliente = 1

    def desativar(self):
        self.situacao_cliente = 0


class ClientePJ:
    def __init__(self, id=None, cnpj=None, razao_social=None, endereco=None, situacao_cliente=1, data_cadastro=None):
        """
        Cliente Pessoa Jurídica
        situacao_cliente:
        - 1 = ativo
        - 0 = inativo
        """
        self.id = id
        self.cnpj = cnpj
        self.razao_social = razao_social
        self.endereco = endereco
        self.situacao_cliente = situacao_cliente
        self.data_cadastro = data_cadastro or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return (f"<ClientePJ id={self.id}, cnpj={self.cnpj}, razao_social={self.razao_social}, "
                f"endereco={self.endereco}, situacao={self.situacao_cliente}>")

    def ativar(self):
        self.situacao_cliente = 1

    def desativar(self):
        self.situacao_cliente = 0
