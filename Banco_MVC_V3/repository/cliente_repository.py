from repository.connection import get_connection
from datetime import datetime


class ClienteRepository:

    # --------- CLIENTE PF ---------
    @staticmethod
    def salvar_pf(cpf, nome, endereco=None, situacao_cliente=1, data_cadastro=None):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clientes_pf (cpf, nome, endereco, situacao_cliente, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                (cpf, nome, endereco, situacao_cliente, data_cadastro or datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def buscar_pf(cpf):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes_pf WHERE cpf = ?", (cpf,))
            return cursor.fetchone()

    @staticmethod
    def buscar_pf_por_id(id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes_pf WHERE id = ?", (id,))
            return cursor.fetchone()

    @staticmethod
    def atualizar_pf(id, cpf=None, nome=None, endereco=None, situacao_cliente=None, data_cadastro=None):
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Construir a query dinamicamente baseada nos parâmetros fornecidos
            campos = []
            valores = []
            
            if cpf is not None:
                campos.append("cpf = ?")
                valores.append(cpf)
            if nome is not None:
                campos.append("nome = ?")
                valores.append(nome)
            if endereco is not None:
                campos.append("endereco = ?")
                valores.append(endereco)
            if situacao_cliente is not None:
                campos.append("situacao_cliente = ?")
                valores.append(situacao_cliente)
            if data_cadastro is not None:
                campos.append("data_cadastro = ?")
                valores.append(data_cadastro)
            
            if not campos:
                return False  # Nada para atualizar
            
            valores.append(id)  # WHERE id = ?
            
            query = f"UPDATE clientes_pf SET {', '.join(campos)} WHERE id = ?"
            cursor.execute(query, valores)
            conn.commit()
            
            return cursor.rowcount > 0

    @staticmethod
    def listar_pf():
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes_pf")
            return cursor.fetchall()

    # --------- CLIENTE PJ ---------
    @staticmethod
    def salvar_pj(cnpj, razao_social, endereco=None, situacao_cliente=1, data_cadastro=None):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clientes_pj (cnpj, razao_social, endereco, situacao_cliente, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                (cnpj, razao_social, endereco, situacao_cliente, data_cadastro or datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def buscar_pj(cnpj):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes_pj WHERE cnpj = ?", (cnpj,))
            return cursor.fetchone()

    @staticmethod
    def buscar_pj_por_id(id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes_pj WHERE id = ?", (id,))
            return cursor.fetchone()

    @staticmethod
    def atualizar_pj(id, cnpj=None, razao_social=None, endereco=None, situacao_cliente=None, data_cadastro=None):
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Construir a query dinamicamente
            campos = []
            valores = []
            
            if cnpj is not None:
                campos.append("cnpj = ?")
                valores.append(cnpj)
            if razao_social is not None:
                campos.append("razao_social = ?")
                valores.append(razao_social)
            if endereco is not None:
                campos.append("endereco = ?")
                valores.append(endereco)
            if situacao_cliente is not None:
                campos.append("situacao_cliente = ?")
                valores.append(situacao_cliente)
            if data_cadastro is not None:
                campos.append("data_cadastro = ?")
                valores.append(data_cadastro)
            
            if not campos:
                return False  # Nada para atualizar
            
            valores.append(id)  # WHERE id = ?
            
            query = f"UPDATE clientes_pj SET {', '.join(campos)} WHERE id = ?"
            cursor.execute(query, valores)
            conn.commit()
            
            return cursor.rowcount > 0

    @staticmethod
    def listar_pj():
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes_pj")
            return cursor.fetchall()

    # --------- MÉTODOS GERAIS ---------
    @staticmethod
    def inativar_cliente_pf(id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes_pf SET situacao_cliente = 0 WHERE id = ?",
                (id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def inativar_cliente_pj(id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes_pj SET situacao_cliente = 0 WHERE id = ?",
                (id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def ativar_cliente_pf(id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes_pf SET situacao_cliente = 1 WHERE id = ?",
                (id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def ativar_cliente_pj(id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes_pj SET situacao_cliente = 1 WHERE id = ?",
                (id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    # --------- MÉTODOS ESPECÍFICOS PARA DATA ---------
    @staticmethod
    def atualizar_data_cadastro_pf(id, data_cadastro):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes_pf SET data_cadastro = ? WHERE id = ?",
                (data_cadastro, id)
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def atualizar_data_cadastro_pj(id, data_cadastro):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes_pj SET data_cadastro = ? WHERE id = ?",
                (data_cadastro, id)
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def atualizar_data_cadastro_para_atual_pf(id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes_pf SET data_cadastro = ? WHERE id = ?",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id)
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def atualizar_data_cadastro_para_atual_pj(id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clientes_pj SET data_cadastro = ? WHERE id = ?",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id)
            )
            conn.commit()
            return cursor.rowcount > 0
        
    @staticmethod
    def buscar_todos_pf(situacao=None):
        """Busca clientes PF com ou sem filtro de situação"""
        with get_connection() as conn:
            cursor = conn.cursor()
            if situacao is None:
                # Buscar TODOS os clientes PF
                cursor.execute("SELECT id, cpf, nome, endereco, situacao_cliente, data_cadastro FROM clientes_pf")
            else:
                # Buscar clientes PF com situação específica
                cursor.execute("""
                    SELECT id, cpf, nome, endereco, situacao_cliente, data_cadastro 
                    FROM clientes_pf WHERE situacao_cliente = ?
                """, (situacao,))
            return cursor.fetchall()

    @staticmethod
    def buscar_todos_pj(situacao=None):
        """Busca clientes PJ com ou sem filtro de situação"""
        with get_connection() as conn:
            cursor = conn.cursor()
            if situacao is None:
                # Buscar TODOS os clientes PJ
                cursor.execute("SELECT id, cnpj, razao_social, endereco, situacao_cliente, data_cadastro FROM clientes_pj")
            else:
                # Buscar clientes PJ com situação específica
                cursor.execute("""
                    SELECT id, cnpj, razao_social, endereco, situacao_cliente, data_cadastro 
                    FROM clientes_pj WHERE situacao_cliente = ?
                """, (situacao,))
            return cursor.fetchall()

        
   

# No arquivo ClienteRepository.py, adicione:
@staticmethod
def buscar_pj_por_id(cliente_id):
    with get_connection() as conn:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, cnpj, razao_social, endereco, situacao_cliente, data_cadastro FROM clientes_pj WHERE id = ?", (cliente_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
