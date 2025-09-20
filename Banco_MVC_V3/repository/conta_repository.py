from repository.connection import get_connection
from repository.transacao_repository import TransacaoRepository
from datetime import datetime
import random

class ContaRepository:

    
    @staticmethod
    def criar_conta(cpf=None, cnpj=None, tipo_cliente="PF", agencia="0001", saldo_inicial=0.0, tipo_conta="CORRENTE"):
        with get_connection() as conn:
            cursor = conn.cursor()
            
            numero_conta = ContaRepository.gerar_numero_conta()
            
            # Inserir a conta com saldo ZERO inicialmente
            cursor.execute(
                """INSERT INTO contas 
                (numero_conta, agencia, saldo, tipo_conta, cpf, cnpj, tipo_cliente, situacao, data_abertura) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (numero_conta, agencia, 0.0, tipo_conta, cpf, cnpj, tipo_cliente, 1,  # ← Saldo inicial 0
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            
            conn.commit()
            
            # Registrar transação de depósito inicial se o saldo for maior que 0
            if saldo_inicial > 0:
                TransacaoRepository.criar_transacao(
                    tipo="DEPOSITO_INICIAL",
                    valor=saldo_inicial,
                    conta_origem=numero_conta,
                    descricao=f"Depósito inicial - Abertura de conta"
                )
            
            return numero_conta

    @staticmethod
    def gerar_numero_conta():
        """Gera um número de conta único de 6 dígitos"""
        with get_connection() as conn:
            cursor = conn.cursor()
            while True:
                numero = str(random.randint(100000, 999999))
                cursor.execute("SELECT id FROM contas WHERE numero_conta = ?", (numero,))
                if not cursor.fetchone():
                    return numero

    @staticmethod
    def conta_existe(cpf_cnpj, tipo_cliente):
        """Verifica se o cliente já possui uma conta"""
        with get_connection() as conn:
            cursor = conn.cursor()
            if tipo_cliente == "PF":
                cursor.execute("SELECT id FROM contas WHERE cpf = ?", (cpf_cnpj,))
            else:
                cursor.execute("SELECT id FROM contas WHERE cnpj = ?", (cpf_cnpj,))
            return cursor.fetchone() is not None

    @staticmethod
    def obter_numero_conta_por_id(conta_id):
        """Obtém o número da conta pelo ID"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT numero_conta FROM contas WHERE id = ?", (conta_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    @staticmethod
    def obter_numero_conta(numero_conta):
        """Obtém o número da conta pelo ID"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT numero_conta FROM contas WHERE numero_conta = ?", (numero_conta))
            result = cursor.fetchone()
            return result[0] if result else None

    @staticmethod
    def buscar_por_cpf(cpf):
        """Busca conta por CPF"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contas WHERE cpf = ?", (cpf,))
            return cursor.fetchone()

    @staticmethod
    def buscar_por_cnpj(cnpj):
        """Busca conta por CNPJ"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contas WHERE cnpj = ?", (cnpj,))
            return cursor.fetchone()

    @staticmethod
    def listar_contas():
        """Lista todas as contas"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, 
                       COALESCE(pf.nome, pj.razao_social) as nome_cliente
                FROM contas c
                LEFT JOIN clientes_pf pf ON c.cpf = pf.cpf
                LEFT JOIN clientes_pj pj ON c.cnpj = pj.cnpj
                ORDER BY c.data_abertura DESC
            """)
            return cursor.fetchall()

    
    @staticmethod
    def buscar_saldo(numero_conta):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT saldo FROM contas WHERE numero_conta = ?", (numero_conta,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0.0
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def buscar_por_numero(numero_conta):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM contas WHERE numero_conta = ?", (numero_conta,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()     

    @staticmethod
    def buscar_contas_por_cliente(cpf_cnpj, tipo_cliente):
        """
        Busca todas as contas de um cliente pelo CPF ou CNPJ
        tipo_cliente: "PF" ou "PJ"
        Retorna: Lista de tuplas com (numero_conta, agencia, tipo_conta, saldo, situacao, data_abertura)
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if tipo_cliente == "PF":
                query = """
                SELECT numero_conta, agencia, tipo_conta, saldo, situacao, data_abertura 
                FROM contas 
                WHERE cpf = ? 
                ORDER BY data_abertura DESC
                """
            else:  # PJ
                query = """
                SELECT numero_conta, agencia, tipo_conta, saldo, situacao, data_abertura 
                FROM contas 
                WHERE cnpj = ? 
                ORDER BY data_abertura DESC
                """
            
            cursor.execute(query, (cpf_cnpj,))
            contas = cursor.fetchall()
            
            conn.close()
            return contas if contas else []
            
        except Exception as e:
            print(f"Erro ao buscar contas do cliente: {e}")
            return []

    @staticmethod
    def buscar_por_identificador(identificador):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Tenta buscar por CPF primeiro (SQLite usa ?)
            cursor.execute("SELECT * FROM contas WHERE cpf = ?", (identificador,))
            conta = cursor.fetchone()
            if conta:
                return conta
            
            # Se não encontrou por CPF, busca por CNPJ
            cursor.execute("SELECT * FROM contas WHERE cnpj = ?", (identificador,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()