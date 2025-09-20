from repository.connection import get_connection
from datetime import datetime


class FuncionarioRepository:

    @staticmethod
    def salvar_funcionario(cpf, nome, cargo, data_cadastro=None, situacao_funcionario=1):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO funcionarios (cpf, nome, cargo, data_cadastro, situacao_funcionario) VALUES (?, ?, ?, ?, ?)",
                (cpf, nome, cargo, data_cadastro or datetime.now().strftime("%Y-%m-%d %H:%M:%S"), situacao_funcionario)
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def buscar_funcionario(cpf):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM funcionarios WHERE cpf = ?", (cpf,))
            return cursor.fetchone()

    @staticmethod
    def listar_funcionario():
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM funcionarios")
            return cursor.fetchall()





         # Funcionários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS funcionarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                cargo TEXT,
                data_cadastro TEXT,
                situacao_funcionario INTEGER DEFAULT 1
            )
        """)