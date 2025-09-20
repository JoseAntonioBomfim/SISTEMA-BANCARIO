from repository.funcionario_repository import FuncionarioRepository
from models.funcionario import Funcionario
from datetime import datetime


class FuncionarioServico:
    """Serviços para gerenciamento de funcionários"""

    @staticmethod
    def cadastrar(cpf, nome, cargo):
        if FuncionarioRepository.existe(cpf):
            print("Já existe um funcionário com esse CPF")
            return None

        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        funcionario = Funcionario(cpf=cpf, nome=nome, cargo=cargo, data_cadastro=data_cadastro)
        return FuncionarioRepository.salvar(funcionario)

    @staticmethod
    def listar():
        return FuncionarioRepository.listar()

    @staticmethod
    def atualizar(funcionario_id, cargo, situacao):
        return FuncionarioRepository.atualizar(funcionario_id, cargo, situacao)


