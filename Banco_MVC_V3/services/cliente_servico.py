from repository.cliente_repository import ClienteRepository
from models.cliente import ClientePF, ClientePJ
from datetime import datetime


class ClienteServico:
    """Serviços para gerenciamento de clientes"""

    @staticmethod
    def cadastrar_pf(cpf, nome, endereco):
        if ClienteRepository.existe_pf(cpf):
            print("Já existe um cliente PF com esse CPF")
            return None

        cliente = ClientePF(cpf=cpf, nome=nome, endereco=endereco)
        return ClienteRepository.salvar_pf(cliente)

    @staticmethod
    def cadastrar_pj(cnpj, razao_social, endereco):
        if ClienteRepository.existe_pj(cnpj):
            print("Já existe um cliente PJ com esse CNPJ")
            return None

        cliente = ClientePJ(cnpj=cnpj, razao_social=razao_social, endereco=endereco)
        return ClienteRepository.salvar_pj(cliente)

    @staticmethod
    def atualizar_pf(cliente_id, endereco, situacao):
        return ClienteRepository.atualizar_pf(cliente_id, endereco, situacao)

    @staticmethod
    def atualizar_pj(cliente_id, endereco, situacao):
        return ClienteRepository.atualizar_pj(cliente_id, endereco, situacao)

    @staticmethod
    def listar_clientes():
        return ClienteRepository.listar_todos()
