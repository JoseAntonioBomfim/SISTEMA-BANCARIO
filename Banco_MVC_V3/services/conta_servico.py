from repository.conta_repository import ContaRepository
from repository.transacao_repository import TransacaoRepository

class ContaServico:

    @staticmethod
    def depositar(numero_conta, valor):
        try:
            if valor <= 0.01:
                raise ValueError("Valor do depósito deve ser positivo")
            if valor > 100000:
                raise ValueError("Valor máximo de depósito é R$ 100.000")
            
            conta_info = ContaRepository.buscar_por_numero(numero_conta)
            if not conta_info:
                raise ValueError("Conta não encontrada")
            if conta_info[8] == 0:
                raise ValueError("Conta está inativa")
            
            # Usar TransacaoRepository para garantir saldo_apos_transacao
            transacao_id = TransacaoRepository.criar_transacao(
                tipo="DEPOSITO",
                valor=valor,
                conta_origem=numero_conta
            )
            return transacao_id

        except Exception as e:
            print(f"Erro no depósito: {e}")
            return None

    @staticmethod
    def sacar(numero_conta, valor):
        try:
            if valor <= 0:
                raise ValueError("Valor do saque deve ser positivo")

            conta_info = ContaRepository.buscar_por_numero(numero_conta)
            if not conta_info:
                raise ValueError("Conta não encontrada")
            if conta_info[8] == 0:
                raise ValueError("Conta está inativa")

            saldo_atual = conta_info[3]
            if saldo_atual < valor:
                raise ValueError("Saldo insuficiente")

            if valor < 10:
                raise ValueError("Valor mínimo de saque é R$ 10")

            saques_hoje = TransacaoRepository.obter_total_saques_hoje(numero_conta)
            if saques_hoje + valor > 5000:
                raise ValueError("Limite diário de saque excedido (R$ 5.000)")

            # Usar TransacaoRepository
            transacao_id = TransacaoRepository.criar_transacao(
                tipo="SAQUE",
                valor=valor,
                conta_origem=numero_conta
            )
            return transacao_id

        except Exception as e:
            print(f"Erro no saque: {e}")
            return None

    @staticmethod
    def transferir(conta_origem, conta_destino, valor):
        try:
            if valor <= 0:
                raise ValueError("Valor deve ser positivo")
            if conta_origem == conta_destino:
                raise ValueError("Conta origem e destino não podem ser iguais")

            conta_origem_info = ContaRepository.buscar_por_numero(conta_origem)
            conta_destino_info = ContaRepository.buscar_por_numero(conta_destino)

            if not conta_origem_info or not conta_destino_info:
                raise ValueError("Conta não encontrada")
            if conta_origem_info[8] == 0 or conta_destino_info[8] == 0:
                raise ValueError("Conta inativa")

            if conta_origem_info[3] < valor:
                raise ValueError("Saldo insuficiente")

            # Usar TransacaoRepository para registrar a transferência
            transacao_id = TransacaoRepository.criar_transacao(
                tipo="TRANSFERENCIA",
                valor=valor,
                conta_origem=conta_origem,
                conta_destino=conta_destino
            )
            return transacao_id

        except Exception as e:
            print(f"Erro na transferência: {e}")
            return None
