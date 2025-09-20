import bcrypt

from repository.usuario_repository import UsuarioRepository


class UsuarioServico:
    """Serviços para gerenciamento de usuários e autenticação"""

    @staticmethod
    def cadastrar(
                  login=None, senha=None, tipo_usuario=None, cliente_pf_id=None, cliente_pj_id=None, funcionario_id=None, data_cadastro=None):
        if not login:
            raise ValueError("Login não pode ser vazio")
        if not senha:
            raise ValueError("Senha não pode ser vazia")

        # Verifica se login já existe
        if UsuarioRepository.buscar_por_login(login):
            print("Já existe um usuário com esse login")
            return None

        # Gera hash seguro da senha
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        return UsuarioRepository.salvar_usuario_funcionario(
               login, senha_hash, tipo_usuario, cliente_pf_id, cliente_pj_id, funcionario_id, data_cadastro
        )

    @staticmethod
    def autenticar(login, senha, tipo_esperado=None):
        usuario = UsuarioRepository.buscar_por_login(login)
        if not usuario:
            print("Usuário não encontrado")
            return False, None, None, None

        login, senha_hash, tipo_usuario, cliente_pf_id, cliente_pj_id, funcionario_id, data_cadastro = usuario[1:8]

        # Verifica tipo se foi especificado
        if tipo_esperado and tipo_usuario != tipo_esperado:
            print("Tipo de usuário não corresponde")
            return False, None, None, None

        # Verifica senha
        if isinstance(senha_hash, str):  # caso esteja como string
            senha_hash = senha_hash.encode('utf-8')

        if not bcrypt.checkpw(senha.encode('utf-8'), senha_hash):
            print("Senha incorreta")
            return False, None, None, None

        # Determina qual ID associado retornar
        if tipo_usuario == "cliente_pf" and cliente_pf_id:
            return True, login, cliente_pf_id, tipo_usuario
        elif tipo_usuario == "cliente_pj" and cliente_pj_id:
            return True, login, cliente_pj_id, tipo_usuario
        elif tipo_usuario in ("funcionario", "gerente") and funcionario_id:
            return True, login, funcionario_id, tipo_usuario
        else:
            return False, None, None, None

    @staticmethod
    def atualizar_login_senha(usuario_id, senha_atual, novo_login=None, nova_senha=None):
        if not senha_atual or not nova_senha:
            raise ValueError("Senha atual e nova senha são obrigatórias")

        usuario = UsuarioRepository.buscar_por_id(usuario_id)
        if not usuario:
            print("Usuário não encontrado")
            return False

        # usuario = (id, login, tipo_usuario, data_cadastro, ...) dependendo da sua query
        # mas precisamos também do hash da senha → ajuste no repository se não estiver retornando
        # vamos assumir que o método retorna senha no índice 2 ou 3 (dependendo do SELECT)
        
        senha_hash = usuario[2]  # ajustar índice conforme seu SELECT (precisa vir a senha)
        if isinstance(senha_hash, str):
            senha_hash = senha_hash.encode("utf-8")

        # Confere senha atual
        if not bcrypt.checkpw(senha_atual.encode("utf-8"), senha_hash):
            print("Senha atual incorreta")
            return False

        # Gera hash da nova senha
        nova_senha_hash = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt())

        # Atualiza login se fornecido
        if not novo_login:
            novo_login = usuario[1]  # mantém login atual

        return UsuarioRepository.atualizar_login_senha(usuario_id, novo_login, nova_senha_hash)
    
    @staticmethod
    def atualizar_login_senha_pelo_gerente(usuario_id, novo_login=None, nova_senha=None):
        if not nova_senha:
            raise ValueError("Nova Senha é obrigatoria")
        usuario = UsuarioRepository.buscar_por_id(usuario_id)
        if not usuario:
            print("Usuário não encontrado")
            return False

        # usuario = (id, login, tipo_usuario, data_cadastro, ...) dependendo da sua query
        # mas precisamos também do hash da senha → ajuste no repository se não estiver retornando
        # vamos assumir que o método retorna senha no índice 2 ou 3 (dependendo do SELECT)
        
        senha_hash = usuario[2]  # ajustar índice conforme seu SELECT (precisa vir a senha)
        if isinstance(senha_hash, str):
            senha_hash = senha_hash.encode("utf-8")

       # Gera hash da nova senha
        nova_senha_hash = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt())

        # Atualiza login se fornecido
        if not novo_login:
            novo_login = usuario[1]  # mantém login atual

        return UsuarioRepository.atualizar_login_senha(usuario_id, novo_login, nova_senha_hash)

