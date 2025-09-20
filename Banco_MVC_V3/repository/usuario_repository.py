from repository.connection import get_connection
from datetime import datetime
from repository import connection

class UsuarioRepository:

    @staticmethod
    def salvar_usuario_pf(login, senha, tipo_usuario, cliente_pf_id, data_cadastro=None):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (login, senha, tipo_usuario, cliente_pf_id, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                (login, senha, tipo_usuario, cliente_pf_id, data_cadastro or datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def salvar_usuario_pj(login, senha, tipo_usuario, cliente_pj_id, data_cadastro=None):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (login, senha, tipo_usuario, cliente_pj_id, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                (login, senha, tipo_usuario, cliente_pj_id, data_cadastro or datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def salvar_usuario_funcionario(login, senha, tipo_usuario, cliente_pf_id, cliente_pj_id, funcionario_id, data_cadastro=None):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (login, senha, tipo_usuario, cliente_pf_id, cliente_pj_id, funcionario_id, data_cadastro) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (login, senha, tipo_usuario, cliente_pf_id, cliente_pj_id, funcionario_id, data_cadastro or datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def buscar_por_login(login):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE login = ?", (login,))
            return cursor.fetchone()

    @staticmethod
    def autenticar(login, senha, tipo_usuario=None):
        with get_connection() as conn:
            cursor = conn.cursor()
            
            if tipo_usuario:
                # Se um tipo específico foi fornecido, filtra por tipo
                cursor.execute(
                    "SELECT * FROM usuarios WHERE login = ? AND senha = ? AND tipo_usuario = ?",
                    (login, senha, tipo_usuario)
                )
            else:
                # Se nenhum tipo foi fornecido, busca qualquer tipo
                cursor.execute(
                    "SELECT * FROM usuarios WHERE login = ? AND senha = ?",
                    (login, senha)
                )
            
            usuario = cursor.fetchone()
            
            if usuario:
                # Retorna sucesso, usuario_id, id_relacionado, tipo_usuario
                return True, usuario[0], usuario[4] or usuario[5] or usuario[6], usuario[3]
            else:
                return False, None, None, None

    @staticmethod
    def atualizar_login_senha(usuario_id, novo_login, nova_senha):
        """
        Atualiza o login e senha de um usuário
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE usuarios 
                SET login = ?, senha = ?
                WHERE id = ?""",
                (novo_login, nova_senha, usuario_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def buscar_todos_usuarios():
        """Retorna todos os usuários do sistema"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, login, tipo_usuario FROM usuarios ORDER BY login")
            return cursor.fetchall()

    @staticmethod
    def buscar_por_id(usuario_id):
        """Busca um usuário pelo ID"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
            return cursor.fetchone()
        
    @staticmethod
    def buscar_todos_usuarios():
        """Retorna todos os usuários do sistema"""
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, login, tipo_usuario, data_cadastro FROM usuarios")
            return cursor.fetchall()

    @staticmethod
    def buscar_por_id(usuario_id):
        """Busca um usuário pelo ID"""
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, login, tipo_usuario, data_cadastro FROM usuarios WHERE id = ?", (usuario_id,))
            return cursor.fetchone()

    @staticmethod
    def buscar_por_login(login):
        """Busca um usuário pelo login"""
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, login, senha, tipo_usuario, cliente_pf_id, cliente_pj_id, funcionario_id, data_cadastro FROM usuarios WHERE login = ?" , (login,))
            return cursor.fetchone()

    @staticmethod
    def atualizar_login_senha(usuario_id, novo_login, nova_senha):
        """Atualiza o login e senha de um usuário"""
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET login = ?, senha = ? WHERE id = ?", 
                        (novo_login, nova_senha, usuario_id))
            conn.commit()
            return cursor.rowcount > 0
        

    @staticmethod
    def buscar_por_cliente_id(cliente_id, tipo_cliente):
        with connection.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if tipo_cliente == 'cliente_pf':
                    cursor.execute("SELECT id FROM usuarios WHERE cliente_pf_id = %s", (cliente_id,))
                elif tipo_cliente == 'cliente_pj':
                    cursor.execute("SELECT id FROM usuarios WHERE cliente_pj_id = %s", (cliente_id,))
                else:
                    return None
                return cursor.fetchone()
            finally:
                cursor.close()
                conn.close()