import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "banco.db")


def get_connection():
    """Abre uma conexão com o banco de dados"""
    conn = sqlite3.connect(DB_FILE)
    return conn


def criar_tabelas():
    """Cria as tabelas do banco de dados (se não existirem)"""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Clientes Pessoa Física
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes_pf (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cpf TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                endereco TEXT,
                situacao_cliente INTEGER DEFAULT 1,
                data_cadastro TEXT
            )
        """)

        # Clientes Pessoa Jurídica
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes_pj (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cnpj TEXT UNIQUE NOT NULL,
                razao_social TEXT NOT NULL,
                endereco TEXT,
                situacao_cliente INTEGER DEFAULT 1,
                data_cadastro TEXT
            )
        """)

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

        # Usuários (login)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL,
                cliente_pf_id INTEGER,
                cliente_pj_id INTEGER,
                funcionario_id INTEGER,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_pf_id) REFERENCES clientes_pf(id),
                FOREIGN KEY (cliente_pj_id) REFERENCES clientes_pj(id),
                FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
            )
        """)

        # Contas bancárias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_conta TEXT UNIQUE NOT NULL,
                agencia TEXT NOT NULL,
                saldo REAL DEFAULT 0.0,
                tipo_conta TEXT NOT NULL CHECK(tipo_conta IN ('CORRENTE', 'POUPANÇA', 'SALÁRIO')),
                cpf TEXT,
                cnpj TEXT,
                tipo_cliente TEXT,
                situacao INTEGER DEFAULT 1,
                data_abertura TEXT,
                FOREIGN KEY (cpf) REFERENCES clientes_pf (cpf),
                FOREIGN KEY (cnpj) REFERENCES clientes_pj (cnpj)
            )
        """)
        # Transações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL CHECK(tipo IN ('DEPOSITO', 'SAQUE', 'TRANSFERENCIA', 'DEPOSITO_INICIAL')),
                valor REAL NOT NULL CHECK(valor > 0),
                conta_origem TEXT NOT NULL,  -- Número da conta de origem
                conta_destino TEXT,           -- Número da conta destino (para transferências)
                data_hora TEXT NOT NULL,
                saldo_apos_transacao REAL,    -- Saldo após esta transação
                FOREIGN KEY (conta_origem) REFERENCES contas (numero_conta),
                FOREIGN KEY (conta_destino) REFERENCES contas (numero_conta)
         )
    """)
        conn.commit()
        
