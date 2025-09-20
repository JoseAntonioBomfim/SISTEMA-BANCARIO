# models/funcionario.py
from datetime import datetime


class Funcionario:
    def __init__(self, id=None, cpf=None, nome=None, cargo='funcionario', situacao_funcionario=1, data_cadastro=None):
        """
        cargo:
        - 'funcionario'
        - 'gerente'
        situacao_funcionario:
        - 1 = ativo
        - 0 = inativo
        """
        if cargo not in ['funcionario', 'gerente']:
            raise ValueError("Cargo deve ser 'funcionario' ou 'gerente'.")
        
        self.id = id
        self.cpf = cpf
        self.nome = nome
        self.cargo = cargo
        self.situacao_funcionario = situacao_funcionario
        self.data_cadastro = data_cadastro or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return (f"<Funcionario id={self.id}, cpf={self.cpf}, nome={self.nome}, "
                f"cargo={self.cargo}, situacao={self.situacao_funcionario}>")

    
