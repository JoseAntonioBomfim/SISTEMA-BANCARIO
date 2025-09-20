from datetime import datetime, date
from repository.connection import get_connection

class TransacaoRepository:
    
      
    @staticmethod
    def buscar_extrato(numero_conta, data_inicio=None, data_fim=None):
        """
        Busca extrato com filtro por período
        Retorna: lista de transações com todos os campos
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT id, tipo, valor, conta_origem, conta_destino, data_hora, saldo_apos_transacao 
                FROM transacoes 
                WHERE conta_origem = ? OR conta_destino = ?
            """
            params = [numero_conta, numero_conta]
            
            # Adicionar filtro de data se fornecido
            if data_inicio:
                query += " AND DATE(data_hora) >= ?"
                params.append(data_inicio)
            if data_fim:
                query += " AND DATE(data_hora) <= ?"
                params.append(data_fim)
            
            query += " ORDER BY data_hora DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
        
    @staticmethod
    def obter_total_saques_hoje(numero_conta):
        """
        Retorna o total de saques realizados hoje para uma conta específica
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            data_hoje = date.today().strftime("%Y-%m-%d")
            
            cursor.execute(
                """SELECT COALESCE(SUM(valor), 0) 
                FROM transacoes 
                WHERE conta_origem = ? 
                AND tipo = 'SAQUE' 
                AND DATE(data_hora) = ?""",
                (numero_conta, data_hoje)
            )
            
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0.0
    

    @staticmethod
    def criar_transacao(tipo, valor, conta_origem, conta_destino=None, descricao=None):
        """Cria uma nova transação e atualiza o saldo da conta"""
        with get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # 1. Buscar saldo atual da conta de origem
                cursor.execute("SELECT saldo FROM contas WHERE numero_conta = ?", (conta_origem,))
                resultado = cursor.fetchone()
                saldo_atual = resultado[0] if resultado else 0.0
                
                # 2. Calcular novo saldo
                if tipo in ['DEPOSITO_INICIAL', 'DEPOSITO']:
                    novo_saldo = saldo_atual + valor
                elif tipo == 'SAQUE':
                    novo_saldo = saldo_atual - valor
                elif tipo == 'TRANSFERENCIA':
                    novo_saldo = saldo_atual - valor
                    # Para transferência, também atualiza a conta destino
                    if conta_destino:
                        cursor.execute("SELECT saldo FROM contas WHERE numero_conta = ?", (conta_destino,))
                        resultado_destino = cursor.fetchone()
                        saldo_destino = resultado_destino[0] if resultado_destino else 0.0
                        novo_saldo_destino = saldo_destino + valor
                        cursor.execute("UPDATE contas SET saldo = ? WHERE numero_conta = ?", 
                                    (novo_saldo_destino, conta_destino))
                
                # 3. Atualizar saldo na conta de origem
                cursor.execute("UPDATE contas SET saldo = ? WHERE numero_conta = ?", 
                            (novo_saldo, conta_origem))
                
                # 4. Inserir a transação
                cursor.execute(
                    """INSERT INTO transacoes 
                    (tipo, valor, conta_origem, conta_destino, data_hora, saldo_apos_transacao) 
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (tipo, valor, conta_origem, conta_destino, 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), novo_saldo)
                )
                
                conn.commit()
                return cursor.lastrowid
                
            except Exception as e:
                conn.rollback()
                print(f"Erro ao criar transação: {e}")
                return None

    
    
    