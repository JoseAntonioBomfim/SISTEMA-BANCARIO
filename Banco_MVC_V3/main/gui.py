import tkinter as tk
from tkinter import ttk
from repository import connection
from datetime import datetime
import tkinter.messagebox as messagebox
from repository.funcionario_repository import FuncionarioRepository
from repository.usuario_repository import UsuarioRepository
from repository import connection 
from repository.cliente_repository import ClienteRepository
from repository.conta_repository import ContaRepository
from services.conta_servico import ContaServico
from repository.transacao_repository import TransacaoRepository
import tkinter as tk
from tkinter import messagebox
import os
from datetime import datetime, timedelta
from services.usuario_servico import UsuarioServico


# ------------------ CONFIGURAÇÃO ------------------
SENHA_SUPERGERENTE = "admin123"

# ------------------ TELA SUPER GERENTE ------------------
def tela_super_gerente():
    janela = tk.Tk()
    janela.title("SUPER GERENTE")
    janela.geometry("350x250")

    tk.Label(janela, text="Senha do SUPER GERENTE:").pack(pady=10)
    entry_senha = tk.Entry(janela, show="*"); entry_senha.pack()
    lbl_status = tk.Label(janela, text=""); lbl_status.pack(pady=5)

    def autenticar():
        senha = entry_senha.get()
        if senha == SENHA_SUPERGERENTE:
            janela.destroy()
            cadastrar_primeiro_gerente()
        else:
            lbl_status.config(text="Senha incorreta!", fg="red")

    tk.Button(janela, text="Entrar", command=autenticar).pack(pady=15)
    janela.mainloop()

# ------------------ CADASTRAR PRIMEIRO GERENTE ------------------
def cadastrar_primeiro_gerente():
    janela = tk.Tk()
    janela.title("Cadastrar Primeiro Gerente")
    janela.geometry("400x300")  # Aumentei o tamanho para mais campos

    tk.Label(janela, text="Nome do Gerente:").pack(pady=5)
    entry_nome = tk.Entry(janela); entry_nome.pack()
    
    tk.Label(janela, text="CPF do Gerente:").pack(pady=5)
    entry_cpf = tk.Entry(janela); entry_cpf.pack()
    
    tk.Label(janela, text="Login do Gerente:").pack(pady=5)
    entry_login = tk.Entry(janela); entry_login.pack()
    
    tk.Label(janela, text="Senha do Gerente:").pack(pady=5)
    entry_senha = tk.Entry(janela, show="*"); entry_senha.pack()
    
    lbl_status = tk.Label(janela, text=""); lbl_status.pack(pady=5)

    def salvar():
        nome = entry_nome.get()
        cpf = entry_cpf.get()
        login = entry_login.get()
        senha = entry_senha.get()
        
        if not all([nome, cpf, login, senha]):
            lbl_status.config(text="Preencha todos os campos!", fg="red")
            return
        
        try:
            # Primeiro cria o funcionário
            data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            funcionario_id = FuncionarioRepository.salvar_funcionario(
                cpf=cpf,
                nome=nome,
                cargo="Gerente",
                data_cadastro=data_cadastro,
                situacao_funcionario=1
            )
            
            # Depois cria o usuário associado ao funcionário
            # ✅ CORRIGIDO: Removidos os parâmetros desnecessários
            UsuarioServico.cadastrar(
                login=login,
                senha=senha,
                tipo_usuario="gerente",  # ✅ Corrigido: 'tipo_usuario' em vez de 'tipo'
                funcionario_id=funcionario_id,
                data_cadastro=data_cadastro
            )
            
            lbl_status.config(text="Primeiro gerente cadastrado com sucesso!", fg="green")
            janela.after(1500, lambda: [janela.destroy(), tela_login()])
            
        except Exception as e:
            lbl_status.config(text=f"Erro ao cadastrar: {str(e)}", fg="red")
            print(f"Erro: {e}")

    tk.Button(janela, text="Cadastrar", command=salvar).pack(pady=10)
    janela.mainloop()

# ------------------ LOGIN ------------------
def tela_login():
    global janela_login  # Adicione esta linha para tornar janela_login global
    
    janela_login = tk.Tk()  # Mude root para janela_login
    janela_login.title("Banco MVC - Login")
    janela_login.geometry("400x400")

    # Frame para tipo de usuário
    frame_tipo = tk.Frame(janela_login)
    frame_tipo.pack(pady=5)
    
    tk.Label(frame_tipo, text="Tipo de Usuário:").pack()
    
    tipo_var = tk.StringVar(value="cliente_pf")
    tk.Radiobutton(frame_tipo, text="Pessoa Física", variable=tipo_var, value="cliente_pf").pack()
    tk.Radiobutton(frame_tipo, text="Pessoa Jurídica", variable=tipo_var, value="cliente_pj").pack()
    tk.Radiobutton(frame_tipo, text="Funcionário", variable=tipo_var, value="funcionario").pack()
    tk.Radiobutton(frame_tipo, text="Gerente", variable=tipo_var, value="gerente").pack()

    tk.Label(janela_login, text="Usuário:").pack(pady=5)
    entry_usuario = tk.Entry(janela_login); entry_usuario.pack()
    tk.Label(janela_login, text="Senha:").pack(pady=5)
    entry_senha = tk.Entry(janela_login, show="*"); entry_senha.pack()
    lbl_status = tk.Label(janela_login, text=""); lbl_status.pack()

    def autenticar():
        login = entry_usuario.get().strip()
        senha = entry_senha.get().strip()
        tipo_selecionado = tipo_var.get()
        
        if not login or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        # Para o radio button "Funcionário", vamos buscar tanto 'funcionario' quanto 'gerente'
        if tipo_selecionado == 'funcionario':
            # Primeiro tenta como funcionário, depois como gerente
            sucesso, usuario_id, id_relacionado, tipo = UsuarioServico.autenticar(login, senha, 'funcionario')
            if not sucesso:
                sucesso, usuario_id, id_relacionado, tipo = UsuarioServico.autenticar(login, senha, 'gerente')
        else:
            # Para outros tipos, busca normalmente
            sucesso, usuario_id, id_relacionado, tipo = UsuarioServico.autenticar(login, senha, tipo_selecionado)
        
        if sucesso:
            if tipo in ['cliente_pf', 'cliente_pj']:
                # CORREÇÃO: Passe o tipo como segundo parâmetro
                tela_cliente(id_relacionado, tipo)
            elif tipo in ['funcionario', 'gerente']:
                # USA A FUNÇÃO UNIFICADA PARA AMBOS
                tela_gerente_funcionario(id_relacionado, tipo)
            else:
                messagebox.showerror("Erro", "Tipo de usuário desconhecido!")
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")
    tk.Button(janela_login, text="Entrar", command=autenticar).pack(pady=20)
    janela_login.mainloop()
    janela_login.quit()

# ------------------ CLIENTE ------------------

def tela_cliente(cliente_id, tipo_cliente, usuario_id=None):
    janela = tk.Tk()
    janela.title("Área do Cliente")
    janela.geometry("600x500")
    janela.configure(bg="#f0f0f0")
    
    # Obter informações do cliente baseado no tipo
    if tipo_cliente == 'cliente_pf':
        cliente_info = ClienteRepository.buscar_pf_por_id(cliente_id)
    elif tipo_cliente == 'cliente_pj':
        cliente_info = ClienteRepository.buscar_pj_por_id(cliente_id)
    else:
        messagebox.showerror("Erro", "Tipo de cliente inválido!")
        janela.destroy()
        return
    
    if not cliente_info:
        messagebox.showerror("Erro", "Cliente não encontrado!")
        janela.destroy()
        return
    
    # Extrair informações baseado no tipo
    if tipo_cliente == 'cliente_pf':
        id_cliente, cpf, nome, endereco, situacao, data_cadastro = cliente_info
        identificador_valor = cpf
    else:  # cliente_pj
        id_cliente, cnpj, razao_social, endereco, situacao, data_cadastro = cliente_info
        identificador_valor = cnpj
        nome = razao_social  # Use razão social para PJ
    
    # Obter informações da conta
    conta_info = ContaRepository.buscar_por_identificador(identificador_valor)
    
    # Frame principal
    frame_principal = tk.Frame(janela, bg="#f0f0f0")
    frame_principal.pack(padx=20, pady=20, fill='both', expand=True)
    
    # Cabeçalho
    tk.Label(frame_principal, text=f"Bem-vindo, {nome}!", 
            font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=(0, 10))
    
    # Informações do cliente
    frame_info = tk.LabelFrame(frame_principal, text="Informações Pessoais", 
                            font=("Arial", 10, "bold"), bg="#f0f0f0")
    frame_info.pack(fill='x', pady=(0, 15))
    
    # Ajustar texto das informações baseado no tipo
    if tipo_cliente == 'cliente_pf':
        info_text = f"CPF: {cpf}\nEndereço: {endereco or 'Não informado'}\nData de Cadastro: {data_cadastro}"
    else:
        info_text = f"CNPJ: {cnpj}\nRazão Social: {razao_social}\nEndereço: {endereco or 'Não informado'}\nData de Cadastro: {data_cadastro}"
    
    tk.Label(frame_info, text=info_text, font=("Arial", 9), 
            justify='left', bg="#f0f0f0").pack(padx=10, pady=10)
    
    # Informações da conta (se existir)
    if conta_info:
        id_conta, numero_conta, agencia, saldo, tipo_conta, cpf_conta, cnpj_conta, tipo_cliente_conta, situacao_conta, data_abertura = conta_info
        frame_conta = tk.LabelFrame(frame_principal, text="Informações da Conta", 
                                font=("Arial", 10, "bold"), bg="#f0f0f0")
        frame_conta.pack(fill='x', pady=(0, 15))
        
        conta_text = f"Número: {numero_conta}\nAgência: {agencia}\nSaldo: R$ {saldo:.2f}\nTipo: {tipo_conta}\nStatus: {'Ativa' if situacao_conta == 1 else 'Inativa'}"
        tk.Label(frame_conta, text=conta_text, font=("Arial", 9), 
                justify='left', bg="#f0f0f0").pack(padx=10, pady=10)
    else:
        frame_conta = tk.LabelFrame(frame_principal, text="Conta Bancária", 
                                font=("Arial", 10, "bold"), bg="#f0f0f0")
        frame_conta.pack(fill='x', pady=(0, 15))
        tk.Label(frame_conta, text="Você ainda não possui uma conta bancária.\nProcure um gerente para abrir sua conta.", 
                font=("Arial", 9), fg="red", bg="#f0f0f0").pack(padx=10, pady=10)
        numero_conta = None
        agencia = None
    
    # Frame de botões
    frame_botoes = tk.Frame(frame_principal, bg="#f0f0f0")
    frame_botoes.pack(pady=10)
    
    # Funções para os botões
    def consultar_saldo():
        if not conta_info:
            messagebox.showinfo("Informação", "Você não possui uma conta bancária.")
            return
            
        win = tk.Toplevel(janela)
        win.title("Saldo da Conta")
        win.geometry("300x250")
        win.configure(bg="#f0f0f0")
        
        saldo_atual = ContaRepository.buscar_saldo(numero_conta)
        
        tk.Label(win, text="SALDO ATUAL", font=("Arial", 14, "bold"), 
                bg="#f0f0f0").pack(pady=(20, 10))
        
        tk.Label(win, text=f"R$ {saldo_atual:,.2f}", 
                font=("Arial", 24, "bold"), fg="green", bg="#f0f0f0").pack(pady=10)
        
        tk.Label(win, text=f"Conta: {numero_conta}\nAgência: {agencia}", 
                font=("Arial", 9), bg="#f0f0f0").pack(pady=10)
        
        tk.Button(win, text="Fechar", command=win.destroy, 
                bg="#dc3545", fg="white", width=10).pack(pady=10)
    
    def consultar_extrato():
        if not conta_info:
            messagebox.showinfo("Informação", "Você não possui uma conta bancária.")
            return
            
        win = tk.Toplevel(janela)
        win.title("Extrato Bancário")
        win.geometry("700x500")
        win.configure(bg="#f0f0f0")
        
        frame_top = tk.Frame(win, bg="#f0f0f0")
        frame_top.pack(padx=20, pady=20, fill='x')
        
        tk.Label(frame_top, text=f"EXTRATO - CONTA {numero_conta}", 
                font=("Arial", 14, "bold"), bg="#f0f0f0").pack()
        
        saldo_atual = ContaRepository.buscar_saldo(numero_conta)
        tk.Label(frame_top, text=f"Saldo Atual: R$ {saldo_atual:,.2f}", 
                font=("Arial", 12), fg="green", bg="#f0f0f0").pack(pady=(5, 10))
        
        # Frame com scrollbar para o extrato
        frame_extrato = tk.Frame(win)
        frame_extrato.pack(padx=20, pady=(0, 20), fill='both', expand=True)
        
        canvas = tk.Canvas(frame_extrato)
        scrollbar = tk.Scrollbar(frame_extrato, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Buscar extrato
        extrato = TransacaoRepository.buscar_extrato(numero_conta)
        
        if extrato:
            for transacao in extrato:
                id_trans, tipo, valor, conta_origem, conta_destino, data_hora, saldo_apos = transacao
                
                # Tratar valores None
                valor_formatado = f"{valor:,.2f}" if valor is not None else "0.00"
                saldo_apos_formatado = f"{saldo_apos:,.2f}" if saldo_apos is not None else "N/A"
                
                if tipo == "DEPOSITO":
                    texto = f"{data_hora} - DEPÓSITO: +R$ {valor_formatado} | Saldo: R$ {saldo_apos_formatado}"
                    cor = "green"
                elif tipo == "SAQUE":
                    texto = f"{data_hora} - SAQUE: -R$ {valor_formatado} | Saldo: R$ {saldo_apos_formatado}"
                    cor = "red"
                elif tipo == "TRANSFERENCIA":
                    if conta_origem == numero_conta:
                        texto = f"{data_hora} - TRANSF. ENVIADA: -R$ {valor_formatado} para {conta_destino or 'N/A'} | Saldo: R$ {saldo_apos_formatado}"
                        cor = "red"
                    else:
                        texto = f"{data_hora} - TRANSF. RECEBIDA: +R$ {valor_formatado} de {conta_origem or 'N/A'} | Saldo: R$ {saldo_apos_formatado}"
                        cor = "green"
                else:
                    texto = f"{data_hora} - {tipo}: R$ {valor_formatado} | Saldo: R$ {saldo_apos_formatado}"
                    cor = "blue"
                
                tk.Label(scrollable_frame, text=texto, fg=cor, font=("Arial", 9), 
                        justify='left').pack(anchor='w', pady=2)
        else:
            tk.Label(scrollable_frame, text="Nenhuma transação encontrada.", 
                    fg="gray", font=("Arial", 10)).pack(pady=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Button(win, text="Fechar", command=win.destroy, 
                bg="#6c757d", fg="white", width=10).pack(pady=10)

    def alterar_dados():
        win = tk.Toplevel(janela)
        win.title("Alterar Dados de Acesso")
        win.geometry("300x250")
        win.configure(bg="#f0f0f0")

        tk.Label(win, text="Senha Atual:", bg="#f0f0f0").pack(pady=5)
        entry_senha_atual = tk.Entry(win, show="*")
        entry_senha_atual.pack()

        tk.Label(win, text="Novo Usuário (opcional):", bg="#f0f0f0").pack(pady=5)
        entry_novo_usuario = tk.Entry(win)
        entry_novo_usuario.pack()

        tk.Label(win, text="Nova Senha:", bg="#f0f0f0").pack(pady=5)
        entry_nova_senha = tk.Entry(win, show="*")
        entry_nova_senha.pack()

        def salvar_alteracao():
            senha_atual = entry_senha_atual.get().strip()
            novo_usuario = entry_novo_usuario.get().strip()
            nova_senha = entry_nova_senha.get().strip()

            if not senha_atual or not nova_senha:
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
                return

            # Se usuario_id não foi passado, precisamos buscar
            if usuario_id is None:
                # Buscar o usuario_id baseado no cliente_id e tipo
                usuario_info = UsuarioRepository.buscar_por_cliente_id(cliente_id, tipo_cliente)
                if usuario_info:
                    usuario_id_atual = usuario_info[0]
                else:
                    messagebox.showerror("Erro", "Usuário não encontrado!")
                    return
            else:
                usuario_id_atual = usuario_id

            sucesso = UsuarioServico.atualizar_login_senha(usuario_id_atual, senha_atual, novo_usuario, nova_senha)

            if sucesso:
                messagebox.showinfo("Sucesso", "Dados de login/senha atualizados com sucesso!")
                win.destroy()
            else:
                messagebox.showerror("Erro", "Senha atual incorreta ou erro ao atualizar.")

        tk.Button(win, text="Salvar", command=salvar_alteracao,
                bg="#28a745", fg="white", width=10).pack(pady=10)
        tk.Button(win, text="Cancelar", command=win.destroy,
                bg="#dc3545", fg="white", width=10).pack(pady=5)
    
    def sair():
        janela.destroy()
        tela_login()
    
    # Botões (apenas se tiver conta)
    if conta_info:
        btn_saldo = tk.Button(frame_botoes, text="Consultar Saldo", command=consultar_saldo,
                            bg="#28a745", fg="white", font=("Arial", 10, "bold"),
                            width=15, height=2)
        btn_saldo.grid(row=0, column=0, padx=5, pady=5)
        
        btn_extrato = tk.Button(frame_botoes, text="Ver Extrato", command=consultar_extrato,
                            bg="#17a2b8", fg="white", font=("Arial", 10, "bold"),
                            width=15, height=2)
        btn_extrato.grid(row=0, column=1, padx=5, pady=5)
    
    btn_alterar = tk.Button(frame_botoes, text="Alterar Dados", command=alterar_dados,
                        bg="#ffc107", fg="black", font=("Arial", 10, "bold"),
                        width=15, height=2)
    btn_alterar.grid(row=1, column=0, padx=5, pady=5)
    
    btn_sair = tk.Button(frame_botoes, text="Sair", command=sair,
                    bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
                    width=15, height=2)
    btn_sair.grid(row=1, column=1, padx=5, pady=5)
    
    # Rodapé
    tk.Label(frame_principal, text="Banco MVC - Sistema Bancário", 
            font=("Arial", 8), fg="gray", bg="#f0f0f0").pack(side='bottom', pady=10)
    
    janela.mainloop()    
    tela_login() # Volta para a tela de login ao fechar a janela do cliente

   
########################################################################################################

# ------------------ GERENTE ------------------
def tela_gerente_funcionario(usuario_id, tipo_usuario="funcionario"):
    janela = tk.Tk()
    
    if tipo_usuario == "gerente":
        janela.title("Área do Gerente")
        janela.geometry("400x600")
    else:
        janela.title("Área do Funcionário")
        janela.geometry("400x550")  # Menor altura

        # ------------------ CLIENTE PESSOA FÍSICA (REFORMULADA) ------------------
    def cadastrar_cliente_pf():
        win = tk.Toplevel(janela)
        win.title("Cadastrar Cliente - Pessoa Física")
        win.geometry("500x550")
        win.resizable(True, True)
        
        # Frame principal
        frame_principal = tk.Frame(win)
        frame_principal.pack(padx=30, pady=30, fill='both', expand=True)
        
        tk.Label(frame_principal, text="CADASTRAR CLIENTE PESSOA FÍSICA", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para os campos
        frame_campos = tk.Frame(frame_principal)
        frame_campos.pack(fill='x', pady=(0, 20))
        
        # Nome
        tk.Label(frame_campos, text="Nome Completo:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        entry_nome = tk.Entry(frame_campos, width=30, font=("Arial", 10))
        entry_nome.grid(row=0, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # CPF
        tk.Label(frame_campos, text="CPF:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        entry_cpf = tk.Entry(frame_campos, width=20, font=("Arial", 10))
        entry_cpf.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Endereço
        tk.Label(frame_campos, text="Endereço:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=(0, 5))
        entry_endereco = tk.Entry(frame_campos, width=30, font=("Arial", 10))
        entry_endereco.grid(row=2, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Separador
        ttk.Separator(frame_principal, orient='horizontal').pack(fill='x', pady=(0, 20))
        
        tk.Label(frame_principal, text="DADOS DE ACESSO", font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Frame para dados de acesso
        frame_acesso = tk.Frame(frame_principal)
        frame_acesso.pack(fill='x', pady=(0, 20))
        
        # Login
        tk.Label(frame_acesso, text="Login:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        entry_login = tk.Entry(frame_acesso, width=20, font=("Arial", 10))
        entry_login.grid(row=0, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Senha
        tk.Label(frame_acesso, text="Senha:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        entry_senha = tk.Entry(frame_acesso, width=20, show="*", font=("Arial", 10))
        entry_senha.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Confirmar Senha
        tk.Label(frame_acesso, text="Confirmar Senha:*", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=(0, 5))
        entry_confirmar_senha = tk.Entry(frame_acesso, width=20, show="*", font=("Arial", 10))
        entry_confirmar_senha.grid(row=2, column=1, sticky='ew', pady=(0, 15), padx=(10, 0))
        
        # Status label
        lbl_status = tk.Label(frame_principal, text="", fg="green", font=("Arial", 10))
        lbl_status.pack(pady=(0, 15))
        
        def validar_campos():
            """Valida todos os campos do formulário"""
            nome = entry_nome.get().strip()
            cpf = entry_cpf.get().strip()
            login = entry_login.get().strip()
            senha = entry_senha.get().strip()
            confirmar_senha = entry_confirmar_senha.get().strip()
            
            if not all([nome, cpf, login, senha, confirmar_senha]):
                return False, "Preencha todos os campos obrigatórios!"
            
            if len(cpf) != 11 or not cpf.isdigit():
                return False, "CPF inválido! Deve ter 11 dígitos."
            
            if senha != confirmar_senha:
                return False, "As senhas não coincidem!"
            
            if len(senha) < 4:
                return False, "A senha deve ter pelo menos 4 caracteres!"
            
            return True, ""
        
        def salvar():
            # Validar campos
            valido, mensagem_erro = validar_campos()
            if not valido:
                lbl_status.config(text=mensagem_erro, fg="red")
                return
            
            # Obter valores
            nome = entry_nome.get().strip()
            cpf = ''.join(filter(str.isdigit, entry_cpf.get().strip()))
            endereco = entry_endereco.get().strip()
            login = entry_login.get().strip()
            senha = entry_senha.get().strip()
            data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                # Verificar se CPF já existe
                if ClienteRepository.buscar_pf(cpf=cpf):
                    lbl_status.config(text="CPF já cadastrado!", fg="red")
                    return
                
                # Verificar se login já existe
                if UsuarioRepository.buscar_por_login(login):
                    lbl_status.config(text="Login já está em uso! Escolha outro.", fg="red")
                    return
                
                # Salvar cliente PF
                cliente_id = ClienteRepository.salvar_pf(
                    cpf=cpf,
                    nome=nome,
                    endereco=endereco,
                    situacao_cliente=1,
                    data_cadastro=data_cadastro
                )
                
                # Salvar usuário
                UsuarioServico.cadastrar(
                    cliente_pf_id=cliente_id,
                    login=login,
                    senha=senha,
                    tipo_usuario="cliente_pf"
                )
                
                lbl_status.config(text="Cliente cadastrado com sucesso!", fg="green")
                
                # Limpar campos após sucesso
                entry_nome.delete(0, tk.END)
                entry_cpf.delete(0, tk.END)
                entry_endereco.delete(0, tk.END)
                entry_login.delete(0, tk.END)
                entry_senha.delete(0, tk.END)
                entry_confirmar_senha.delete(0, tk.END)
                
                # Fechar após 2 segundos
                win.after(2000, win.destroy)
                
            except Exception as e:
                lbl_status.config(text=f"Erro ao cadastrar: {str(e)}", fg="red")
        
        # Frame para botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(pady=10)
        
        btn_salvar = tk.Button(frame_botoes, text="Cadastrar", command=salvar,
                            bg="#28a745", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_salvar.pack(side='left', padx=5)
        
        btn_limpar = tk.Button(frame_botoes, text="Limpar", command=lambda: [
            entry_nome.delete(0, tk.END),
            entry_cpf.delete(0, tk.END),
            entry_endereco.delete(0, tk.END),
            entry_login.delete(0, tk.END),
            entry_senha.delete(0, tk.END),
            entry_confirmar_senha.delete(0, tk.END),
            lbl_status.config(text="")
        ], bg="#6c757d", fg="white", font=("Arial", 10, "bold"),
        width=12, height=2)
        btn_limpar.pack(side='left', padx=5)
        
        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=win.destroy,
                            bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_cancelar.pack(side='left', padx=5)
        
        # Configurar grid weights
        frame_campos.columnconfigure(1, weight=1)
        frame_acesso.columnconfigure(1, weight=1)

    # ------------------ CLIENTE PESSOA JURÍDICA (REFORMULADA) ------------------
    def cadastrar_cliente_pj():
        win = tk.Toplevel(janela)
        win.title("Cadastrar Cliente - Pessoa Jurídica")
        win.geometry("500x550")
        win.resizable(True, True)
        
        # Frame principal
        frame_principal = tk.Frame(win)
        frame_principal.pack(padx=30, pady=30, fill='both', expand=True)
        
        tk.Label(frame_principal, text="CADASTRAR CLIENTE PESSOA JURÍDICA", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para os campos
        frame_campos = tk.Frame(frame_principal)
        frame_campos.pack(fill='x', pady=(0, 20))
        
        # Razão Social
        tk.Label(frame_campos, text="Razão Social:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        entry_razao_social = tk.Entry(frame_campos, width=30, font=("Arial", 10))
        entry_razao_social.grid(row=0, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # CNPJ
        tk.Label(frame_campos, text="CNPJ:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        entry_cnpj = tk.Entry(frame_campos, width=20, font=("Arial", 10))
        entry_cnpj.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Endereço
        tk.Label(frame_campos, text="Endereço:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=(0, 5))
        entry_endereco = tk.Entry(frame_campos, width=30, font=("Arial", 10))
        entry_endereco.grid(row=2, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Separador
        ttk.Separator(frame_principal, orient='horizontal').pack(fill='x', pady=(0, 20))
        
        tk.Label(frame_principal, text="DADOS DE ACESSO", font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Frame para dados de acesso
        frame_acesso = tk.Frame(frame_principal)
        frame_acesso.pack(fill='x', pady=(0, 20))
        
        # Login
        tk.Label(frame_acesso, text="Login:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        entry_login = tk.Entry(frame_acesso, width=20, font=("Arial", 10))
        entry_login.grid(row=0, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Senha
        tk.Label(frame_acesso, text="Senha:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        entry_senha = tk.Entry(frame_acesso, width=20, show="*", font=("Arial", 10))
        entry_senha.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Confirmar Senha
        tk.Label(frame_acesso, text="Confirmar Senha:*", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=(0, 5))
        entry_confirmar_senha = tk.Entry(frame_acesso, width=20, show="*", font=("Arial", 10))
        entry_confirmar_senha.grid(row=2, column=1, sticky='ew', pady=(0, 15), padx=(10, 0))
        
        # Status label
        lbl_status = tk.Label(frame_principal, text="", fg="green", font=("Arial", 10))
        lbl_status.pack(pady=(0, 15))
        
        def validar_campos():
            """Valida todos os campos do formulário"""
            razao_social = entry_razao_social.get().strip()
            cnpj = entry_cnpj.get().strip()
            login = entry_login.get().strip()
            senha = entry_senha.get().strip()
            confirmar_senha = entry_confirmar_senha.get().strip()
            
            if not all([razao_social, cnpj, login, senha, confirmar_senha]):
                return False, "Preencha todos os campos obrigatórios!"
            
            if len(cnpj) != 14 or not cnpj.isdigit():
                return False, "CNPJ inválido! Deve ter 14 dígitos."
            
            if senha != confirmar_senha:
                return False, "As senhas não coincidem!"
            
            if len(senha) < 4:
                return False, "A senha deve ter pelo menos 4 caracteres!"
            
            return True, ""
        
        def salvar():
            # Validar campos
            valido, mensagem_erro = validar_campos()
            if not valido:
                lbl_status.config(text=mensagem_erro, fg="red")
                return
            
            # Obter valores
            razao_social = entry_razao_social.get().strip()
            cnpj = ''.join(filter(str.isdigit, entry_cnpj.get().strip()))
            endereco = entry_endereco.get().strip()
            login = entry_login.get().strip()
            senha = entry_senha.get().strip()
            data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                # Verificar se CNPJ já existe
                if ClienteRepository.buscar_pj(cnpj=cnpj):
                    lbl_status.config(text="CNPJ já cadastrado!", fg="red")
                    return
                
                # Verificar se login já existe
                if UsuarioRepository.buscar_por_login(login):
                    lbl_status.config(text="Login já está em uso! Escolha outro.", fg="red")
                    return
                
                # Salvar cliente PJ
                cliente_id = ClienteRepository.salvar_pj(
                    cnpj=cnpj,
                    razao_social=razao_social,
                    endereco=endereco,
                    situacao_cliente=1,
                    data_cadastro=data_cadastro
                )
                
                # Salvar usuário
                UsuarioServico.cadastrar(
                    cliente_pj_id=cliente_id,
                    login=login,
                    senha=senha,
                    tipo_usuario="cliente_pj"
                )
                
                lbl_status.config(text="Cliente cadastrado com sucesso!", fg="green")
                
                # Limpar campos após sucesso
                entry_razao_social.delete(0, tk.END)
                entry_cnpj.delete(0, tk.END)
                entry_endereco.delete(0, tk.END)
                entry_login.delete(0, tk.END)
                entry_senha.delete(0, tk.END)
                entry_confirmar_senha.delete(0, tk.END)
                
                # Fechar após 2 segundos
                win.after(2000, win.destroy)
                
            except Exception as e:
                lbl_status.config(text=f"Erro ao cadastrar: {str(e)}", fg="red")
        
        # Frame para botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(pady=10)
        
        btn_salvar = tk.Button(frame_botoes, text="Cadastrar", command=salvar,
                            bg="#28a745", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_salvar.pack(side='left', padx=5)
        
        btn_limpar = tk.Button(frame_botoes, text="Limpar", command=lambda: [
            entry_razao_social.delete(0, tk.END),
            entry_cnpj.delete(0, tk.END),
            entry_endereco.delete(0, tk.END),
            entry_login.delete(0, tk.END),
            entry_senha.delete(0, tk.END),
            entry_confirmar_senha.delete(0, tk.END),
            lbl_status.config(text="")
        ], bg="#6c757d", fg="white", font=("Arial", 10, "bold"),
        width=12, height=2)
        btn_limpar.pack(side='left', padx=5)
        
        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=win.destroy,
                            bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_cancelar.pack(side='left', padx=5)
        
        # Configurar grid weights
        frame_campos.columnconfigure(1, weight=1)
        frame_acesso.columnconfigure(1, weight=1)

    # ------------------ ATUALIZAR CLIENTE (REFORMULADA) ------------------
    def atualizar_cliente():
        win = tk.Toplevel(janela)
        win.title("Atualizar Cliente")
        win.geometry("600x600")
        win.resizable(True, True)
        
        # Frame principal
        frame_principal = tk.Frame(win)
        frame_principal.pack(padx=30, pady=30, fill='both', expand=True)
        
        tk.Label(frame_principal, text="ATUALIZAR DADOS DO CLIENTE", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para busca
        frame_busca = tk.Frame(frame_principal)
        frame_busca.pack(fill='x', pady=(0, 20))
        
        # Tipo de busca
        tk.Label(frame_busca, text="Buscar por:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        frame_tipo_busca = tk.Frame(frame_busca)
        frame_tipo_busca.grid(row=0, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        tipo_busca_var = tk.StringVar(value="CPF")
        tk.Radiobutton(frame_tipo_busca, text="CPF", variable=tipo_busca_var, value="CPF", 
                    font=("Arial", 9)).pack(side='left')
        tk.Radiobutton(frame_tipo_busca, text="CNPJ", variable=tipo_busca_var, value="CNPJ", 
                    font=("Arial", 9)).pack(side='left', padx=(10, 0))
        
        # Número do documento
        tk.Label(frame_busca, text="Número do CPF/CNPJ:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        entry_busca = tk.Entry(frame_busca, width=20, font=("Arial", 10))
        entry_busca.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Status label
        lbl_status = tk.Label(frame_principal, text="", fg="green", font=("Arial", 10))
        lbl_status.pack(pady=(0, 15))
        
        # Variáveis para armazenar dados
        cliente_id = None
        cliente_tipo = None
        cpf_cnpj_original = None
        
        def buscar_cliente():
            nonlocal cliente_id, cliente_tipo, cpf_cnpj_original
            
            numero = entry_busca.get().strip()
            tipo_busca = tipo_busca_var.get()
            
            if not numero:
                lbl_status.config(text="Digite um número para buscar!", fg="red")
                return
            
            try:
                if tipo_busca == "CPF":
                    cliente = ClienteRepository.buscar_pf(numero)
                    if cliente:
                        cliente_id, cpf, nome, endereco, situacao, data_cadastro = cliente
                        cliente_tipo = "PF"
                        cpf_cnpj_original = cpf
                        
                        # Preencher campos
                        entry_novo_cpf_cnpj.delete(0, tk.END)
                        entry_novo_cpf_cnpj.insert(0, cpf if cpf else "")
                        entry_nome_razao.delete(0, tk.END)
                        entry_nome_razao.insert(0, nome if nome else "")
                        entry_endereco.delete(0, tk.END)
                        entry_endereco.insert(0, endereco if endereco else "")
                        situacao_var.set(str(situacao))
                        lbl_status.config(text=f"Cliente PF encontrado: {nome}", fg="green")
                    else:
                        lbl_status.config(text="Cliente não encontrado!", fg="red")
                        
                else:  # CNPJ
                    cliente = ClienteRepository.buscar_pj(numero)
                    if cliente:
                        cliente_id, cnpj, razao_social, endereco, situacao, data_cadastro = cliente
                        cliente_tipo = "PJ"
                        cpf_cnpj_original = cnpj
                        
                        # Preencher campos
                        entry_novo_cpf_cnpj.delete(0, tk.END)
                        entry_novo_cpf_cnpj.insert(0, cnpj if cnpj else "")
                        entry_nome_razao.delete(0, tk.END)
                        entry_nome_razao.insert(0, razao_social if razao_social else "")
                        entry_endereco.delete(0, tk.END)
                        entry_endereco.insert(0, endereco if endereco else "")
                        situacao_var.set(str(situacao))
                        lbl_status.config(text=f"Cliente PJ encontrado: {razao_social}", fg="green")
                    else:
                        lbl_status.config(text="Cliente não encontrado!", fg="red")
                        
            except Exception as e:
                lbl_status.config(text=f"Erro na busca: {str(e)}", fg="red")
        
        # Botão de busca (AGORA DEPOIS da definição da função)
        btn_buscar = tk.Button(frame_busca, text="Buscar Cliente", command=buscar_cliente,
                            bg="#17a2b8", fg="white", font=("Arial", 10, "bold"),
                            width=15)
        btn_buscar.grid(row=2, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        # Separador
        ttk.Separator(frame_principal, orient='horizontal').pack(fill='x', pady=(0, 20))
        
        # Frame para dados do cliente
        frame_dados = tk.Frame(frame_principal)
        frame_dados.pack(fill='x', pady=(0, 20))
        
        # Campos para edição
        tk.Label(frame_dados, text="Novo CPF/CNPJ:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        entry_novo_cpf_cnpj = tk.Entry(frame_dados, width=20, font=("Arial", 10))
        entry_novo_cpf_cnpj.grid(row=0, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        tk.Label(frame_dados, text="Novo Nome/Razão Social:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        entry_nome_razao = tk.Entry(frame_dados, width=30, font=("Arial", 10))
        entry_nome_razao.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        tk.Label(frame_dados, text="Novo Endereço:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=(0, 5))
        entry_endereco = tk.Entry(frame_dados, width=30, font=("Arial", 10))
        entry_endereco.grid(row=2, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        tk.Label(frame_dados, text="Nova Situação:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky='w', pady=(0, 5))
        frame_situacao = tk.Frame(frame_dados)
        frame_situacao.grid(row=3, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        situacao_var = tk.StringVar(value="1")
        tk.Radiobutton(frame_situacao, text="Ativo", variable=situacao_var, value="1", 
                    font=("Arial", 9)).pack(side='left')
        tk.Radiobutton(frame_situacao, text="Inativo", variable=situacao_var, value="0", 
                    font=("Arial", 9)).pack(side='left', padx=(10, 0))
        
        # Frame para botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(pady=10)
        
        def atualizar_dados():
            nonlocal cliente_id, cliente_tipo, cpf_cnpj_original
            
            if not cliente_id:
                lbl_status.config(text="Busque um cliente primeiro!", fg="red")
                return
            
            novo_cpf_cnpj = entry_novo_cpf_cnpj.get().strip()
            novo_nome_razao = entry_nome_razao.get().strip()
            novo_endereco = entry_endereco.get().strip()
            nova_situacao = situacao_var.get()
            
            # Verificar se o CPF/CNPJ foi alterado
            if novo_cpf_cnpj != cpf_cnpj_original:
                # Verificar se o novo CPF/CNPJ já existe
                try:
                    if cliente_tipo == "PF":
                        if ClienteRepository.buscar_pf(novo_cpf_cnpj):
                            lbl_status.config(text="Este CPF já está cadastrado para outro cliente!", fg="red")
                            return
                    else:  # PJ
                        if ClienteRepository.buscar_pj(novo_cpf_cnpj):
                            lbl_status.config(text="Este CNPJ já está cadastrado para outro cliente!", fg="red")
                            return
                except Exception as e:
                    lbl_status.config(text=f"Erro ao verificar CPF/CNPJ: {str(e)}", fg="red")
                    return
            
            try:
                situacao_int = int(nova_situacao)
                
                # Usar função do repositório para atualizar
                if cliente_tipo == "PF":
                    sucesso = ClienteRepository.atualizar_pf(
                        id=cliente_id,
                        cpf=novo_cpf_cnpj if novo_cpf_cnpj else None,
                        nome=novo_nome_razao if novo_nome_razao else None,
                        endereco=novo_endereco if novo_endereco else None,
                        situacao_cliente=situacao_int
                    )
                else:  # PJ
                    sucesso = ClienteRepository.atualizar_pj(
                        id=cliente_id,
                        cnpj=novo_cpf_cnpj if novo_cpf_cnpj else None,
                        razao_social=novo_nome_razao if novo_nome_razao else None,
                        endereco=novo_endereco if novo_endereco else None,
                        situacao_cliente=situacao_int
                    )
                
                if sucesso:
                    lbl_status.config(text="Cliente atualizado com sucesso!", fg="green")
                    win.after(2000, win.destroy)
                else:
                    lbl_status.config(text="Nenhum dado foi alterado!", fg="orange")
                
            except Exception as e:
                lbl_status.config(text=f"Erro na atualização: {str(e)}", fg="red")
        
        def limpar_campos():
            """Limpa todos os campos"""
            entry_busca.delete(0, tk.END)
            entry_novo_cpf_cnpj.delete(0, tk.END)
            entry_nome_razao.delete(0, tk.END)
            entry_endereco.delete(0, tk.END)
            situacao_var.set("1")
            lbl_status.config(text="")
        
        btn_atualizar = tk.Button(frame_botoes, text="Atualizar", command=atualizar_dados,
                                bg="#28a745", fg="white", font=("Arial", 10, "bold"),
                                width=12, height=2)
        btn_atualizar.pack(side='left', padx=5)
        
        btn_limpar = tk.Button(frame_botoes, text="Limpar", command=limpar_campos,
                            bg="#6c757d", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_limpar.pack(side='left', padx=5)
        
        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=win.destroy,
                            bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_cancelar.pack(side='left', padx=5)
        
        # Configurar grid weights
        frame_busca.columnconfigure(1, weight=1)
        frame_dados.columnconfigure(1, weight=1)    
        

    # ------------------ CRIAR CONTA (REFORMULADA) ------------------
    def criar_conta():
        win = tk.Toplevel(janela)
        win.title("Criar Nova Conta")
        win.geometry("500x500")
        win.resizable(True, True)
        
        # Frame principal
        frame_principal = tk.Frame(win)
        frame_principal.pack(padx=30, pady=30, fill='both', expand=True)
        
        tk.Label(frame_principal, text="CRIAR NOVA CONTA BANCÁRIA", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para os campos
        frame_campos = tk.Frame(frame_principal)
        frame_campos.pack(fill='x', pady=(0, 20))
        
        # Tipo de Cliente
        tk.Label(frame_campos, text="Tipo de Cliente:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        frame_tipo = tk.Frame(frame_campos)
        frame_tipo.grid(row=0, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        tipo_var = tk.StringVar(value="PF")
        tk.Radiobutton(frame_tipo, text="Pessoa Física", variable=tipo_var, value="PF", 
                    font=("Arial", 9)).pack(side='left')
        tk.Radiobutton(frame_tipo, text="Pessoa Jurídica", variable=tipo_var, value="PJ", 
                    font=("Arial", 9)).pack(side='left', padx=(10, 0))
        
        # CPF/CNPJ
        tk.Label(frame_campos, text="CPF/CNPJ do Cliente:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        entry_cliente = tk.Entry(frame_campos, width=20, font=("Arial", 10))
        entry_cliente.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Agência
        tk.Label(frame_campos, text="Agência:*", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=(0, 5))
        entry_agencia = tk.Entry(frame_campos, width=10, font=("Arial", 10))
        entry_agencia.insert(0, "0001")
        entry_agencia.grid(row=2, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        # Saldo Inicial
        tk.Label(frame_campos, text="Saldo Inicial:*", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky='w', pady=(0, 5))
        entry_saldo = tk.Entry(frame_campos, width=15, font=("Arial", 10))
        entry_saldo.insert(0, "0.00")
        entry_saldo.grid(row=3, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        # Tipo de Conta
        tk.Label(frame_campos, text="Tipo de Conta:*", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky='w', pady=(0, 5))
        tipo_conta_var = tk.StringVar(value="CORRENTE")
        combo_tipo = ttk.Combobox(frame_campos, textvariable=tipo_conta_var, 
                                values=["CORRENTE", "POUPANÇA", "SALÁRIO"], 
                                state="readonly", width=15, font=("Arial", 10))
        combo_tipo.grid(row=4, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        # Status label
        lbl_status = tk.Label(frame_principal, text="", fg="green", font=("Arial", 10))
        lbl_status.pack(pady=(0, 15))
        
        def formatar_documento(event=None):
            """Formata automaticamente CPF/CNPJ"""
            documento = entry_cliente.get()
            documento = ''.join(filter(str.isdigit, documento))
            
            if tipo_var.get() == "PF" and len(documento) <= 11:
                if len(documento) > 9:
                    documento = f"{documento[:3]}.{documento[3:6]}.{documento[6:9]}-{documento[9:]}"
                elif len(documento) > 6:
                    documento = f"{documento[:3]}.{documento[3:6]}.{documento[6:]}"
                elif len(documento) > 3:
                    documento = f"{documento[:3]}.{documento[3:]}"
            elif tipo_var.get() == "PJ" and len(documento) <= 14:
                if len(documento) > 12:
                    documento = f"{documento[:2]}.{documento[2:5]}.{documento[5:8]}/{documento[8:12]}-{documento[12:]}"
                elif len(documento) > 8:
                    documento = f"{documento[:2]}.{documento[2:5]}.{documento[5:8]}/{documento[8:]}"
                elif len(documento) > 5:
                    documento = f"{documento[:2]}.{documento[2:5]}.{documento[5:]}"
                elif len(documento) > 2:
                    documento = f"{documento[:2]}.{documento[2:]}"
            
            # Atualizar o campo sem triggerar evento
            entry_cliente.delete(0, tk.END)
            entry_cliente.insert(0, documento)
        
        def validar_campos():
            """Valida todos os campos do formulário"""
            cliente = ''.join(filter(str.isdigit, entry_cliente.get().strip()))
            agencia = entry_agencia.get().strip()
            saldo = entry_saldo.get().strip()
            tipo_cliente = tipo_var.get()
            
            if not all([cliente, agencia, saldo]):
                return False, "Preencha todos os campos obrigatórios!"
            
            if tipo_cliente == "PF" and (len(cliente) != 11 or not cliente.isdigit()):
                return False, "CPF inválido! Deve ter 11 dígitos."
            
            if tipo_cliente == "PJ" and (len(cliente) != 14 or not cliente.isdigit()):
                return False, "CNPJ inválido! Deve ter 14 dígitos."
            
            try:
                saldo_float = float(saldo)
                if saldo_float < 0:
                    return False, "O saldo inicial não pode ser negativo!"
            except ValueError:
                return False, "Saldo deve ser um valor numérico!"
            
            return True, ""
        
        def criar():
            # Validar campos
            valido, mensagem_erro = validar_campos()
            if not valido:
                lbl_status.config(text=mensagem_erro, fg="red")
                return
            
            # Obter valores
            tipo_cliente = tipo_var.get()
            cliente_doc = ''.join(filter(str.isdigit, entry_cliente.get().strip()))
            agencia = entry_agencia.get().strip()
            saldo = float(entry_saldo.get().strip())

             # OBTER O TIPO DE CONTA SELECIONADO (já está no formato correto)
            tipo_conta_db = tipo_conta_var.get()  # ← Já é "CORRENTE", "POUPANCA" ou "SALARIO"
            
            try:
                # Verificar se cliente existe
                if tipo_cliente == "PF":
                    cliente = ClienteRepository.buscar_pf(cpf=cliente_doc)
                    if not cliente:
                        lbl_status.config(text="Cliente PF não encontrado!", fg="red")
                        return
                else:  # PJ
                    cliente = ClienteRepository.buscar_pj(cnpj=cliente_doc)
                    if not cliente:
                        lbl_status.config(text="Cliente PJ não encontrado!", fg="red")
                        return
                
                # Criar conta usando o método CORRETO do repositório
                if tipo_cliente == "PF":
                    conta_id = ContaRepository.criar_conta(
                        cpf=cliente_doc,
                        tipo_cliente="PF",
                        agencia=agencia,
                        saldo_inicial=saldo,
                        tipo_conta=tipo_conta_db 
                    )
                else:  # PJ
                    conta_id = ContaRepository.criar_conta(
                        cnpj=cliente_doc,
                        tipo_cliente="PJ",
                        agencia=agencia,
                        saldo_inicial=saldo,
                        tipo_conta=tipo_conta_db
                    )
                
                if conta_id:
                    # Buscar o número da conta criada
                    if tipo_cliente == "PF":
                        conta_criada = ContaRepository.buscar_por_cpf(cliente_doc)
                    else:
                        conta_criada = ContaRepository.buscar_por_cnpj(cliente_doc)
                    
                    if conta_criada:
                        numero_conta = conta_criada[1]  # Supondo que o número da conta está na posição 1
                        lbl_status.config(text=f"Conta criada com sucesso! Número: {numero_conta}", fg="green")
                    else:
                        lbl_status.config(text="Conta criada, mas não foi possível obter o número!", fg="orange")
                    
                    # Limpar campos após sucesso
                    entry_cliente.delete(0, tk.END)
                    entry_saldo.delete(0, tk.END)
                    entry_saldo.insert(0, "0.00")
                    
                    # Fechar após 3 segundos
                    win.after(3000, win.destroy)
                else:
                    lbl_status.config(text="Erro ao criar conta!", fg="red")
                    
            except Exception as e:
                lbl_status.config(text=f"Erro ao criar conta: {str(e)}", fg="red")
        
        # Vincular evento de formatação
        entry_cliente.bind("<KeyRelease>", formatar_documento)
        tipo_var.trace("w", lambda *args: formatar_documento())
        
        # Frame para botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(pady=10)
        
        btn_criar = tk.Button(frame_botoes, text="Criar Conta", command=criar,
                            bg="#28a745", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_criar.pack(side='left', padx=5)
        
        btn_limpar = tk.Button(frame_botoes, text="Limpar", command=lambda: [
            entry_cliente.delete(0, tk.END),
            entry_saldo.delete(0, tk.END),
            entry_saldo.insert(0, "0.00"),
            lbl_status.config(text="")
        ], bg="#6c757d", fg="white", font=("Arial", 10, "bold"),
        width=12, height=2)
        btn_limpar.pack(side='left', padx=5)
        
        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=win.destroy,
                            bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_cancelar.pack(side='left', padx=5)
        
        # Configurar grid weights
        frame_campos.columnconfigure(1, weight=1)
        
        # Focar no campo do documento
        entry_cliente.focus()
    # ------------------ DEPOSITAR (REFORMULADA) ------------------
    def depositar():
        win = tk.Toplevel(janela)
        win.title("Depositar")
        win.geometry("500x400")
        win.resizable(True, True)
        
        # Frame principal
        frame_principal = tk.Frame(win)
        frame_principal.pack(padx=30, pady=30, fill='both', expand=True)
        
        tk.Label(frame_principal, text="DEPOSITAR VALOR", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para os campos
        frame_campos = tk.Frame(frame_principal)
        frame_campos.pack(fill='x', pady=(0, 20))
        
        # Número da Conta
        tk.Label(frame_campos, text="Número da Conta:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        entry_conta = tk.Entry(frame_campos, width=15, font=("Arial", 10))
        entry_conta.grid(row=0, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Valor
        tk.Label(frame_campos, text="Valor do Depósito:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        entry_valor = tk.Entry(frame_campos, width=15, font=("Arial", 10))
        entry_valor.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Descrição
        tk.Label(frame_campos, text="Descrição:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=(0, 5))
        entry_descricao = tk.Entry(frame_campos, width=30, font=("Arial", 10))
        entry_descricao.grid(row=2, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Status label
        lbl_status = tk.Label(frame_principal, text="", fg="green", font=("Arial", 10))
        lbl_status.pack(pady=(0, 15))
        
        def validar_campos():
            """Valida todos os campos do formulário"""
            conta = entry_conta.get().strip()
            valor = entry_valor.get().strip()
            
            if not all([conta, valor]):
                return False, "Preencha todos os campos obrigatórios!"
            
            if not conta.isdigit():
                return False, "Número da conta deve conter apenas dígitos!"
            
            try:
                valor_float = float(valor)
                if valor_float <= 0:
                    return False, "O valor do depósito deve ser positivo!"
            except ValueError:
                return False, "Valor deve ser um número!"
            
            return True, ""
        
        def executar_deposito():
            # Validar campos
            valido, mensagem_erro = validar_campos()
            if not valido:
                lbl_status.config(text=mensagem_erro, fg="red")
                return
            
            # Obter valores
            numero_conta = entry_conta.get().strip()
            valor = float(entry_valor.get().strip())
            descricao = entry_descricao.get().strip() or "Depósito"
            
            try:
                # Verificar se conta existe
                conta = ContaRepository.buscar_por_numero(numero_conta)
                if not conta:
                    lbl_status.config(text="Conta não encontrada!", fg="red")
                    return 
                
                # Extrair dados da conta
                situacao = conta[8]  # situacao está na posição 8
                
                # Verificar se conta está ativa
                if situacao != 1:
                    lbl_status.config(text="Conta inativa! Não é possível depositar.", fg="red")
                    return
                
                # Executar depósito - este método já chama criar_transacao internamente
                transacao_id = ContaServico.depositar(numero_conta, valor)
                
                if transacao_id is None:
                    lbl_status.config(text="Erro ao realizar depósito!", fg="red")
                    return
                
                # Obter o novo saldo atualizado
                novo_saldo = ContaRepository.buscar_saldo(numero_conta)
                
                lbl_status.config(text=f"Depósito realizado! Novo saldo: R$ {novo_saldo:.2f}", fg="green")
                
                # Limpar campos após sucesso
                entry_valor.delete(0, tk.END)
                entry_descricao.delete(0, tk.END)
                
                # Fechar após 3 segundos
                win.after(3000, win.destroy)
                
            except Exception as e:
                lbl_status.config(text=f"Erro ao realizar depósito: {str(e)}", fg="red")
        
        # Frame para botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(pady=10)
        
        btn_depositar = tk.Button(frame_botoes, text="Depositar", command=executar_deposito,
                                bg="#28a745", fg="white", font=("Arial", 10, "bold"),
                                width=12, height=2)
        btn_depositar.pack(side='left', padx=5)
        
        btn_limpar = tk.Button(frame_botoes, text="Limpar", command=lambda: [
            entry_conta.delete(0, tk.END),
            entry_valor.delete(0, tk.END),
            entry_descricao.delete(0, tk.END),
            lbl_status.config(text="")
        ], bg="#6c757d", fg="white", font=("Arial", 10, "bold"),
        width=12, height=2)
        btn_limpar.pack(side='left', padx=5)
        
        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=win.destroy,
                            bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_cancelar.pack(side='left', padx=5)
        
        # Configurar grid weights
        frame_campos.columnconfigure(1, weight=1)

    # ------------------ SACAR (REFORMULADA) ------------------
    def sacar():
        win = tk.Toplevel(janela)
        win.title("Sacar")
        win.geometry("500x400")
        win.resizable(True, True)
        
        # Frame principal
        frame_principal = tk.Frame(win)
        frame_principal.pack(padx=30, pady=30, fill='both', expand=True)
        
        tk.Label(frame_principal, text="SACAR VALOR", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para os campos
        frame_campos = tk.Frame(frame_principal)
        frame_campos.pack(fill='x', pady=(0, 20))
        
        # Número da Conta
        tk.Label(frame_campos, text="Número da Conta:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        entry_conta = tk.Entry(frame_campos, width=15, font=("Arial", 10))
        entry_conta.grid(row=0, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Valor
        tk.Label(frame_campos, text="Valor do Saque:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        entry_valor = tk.Entry(frame_campos, width=15, font=("Arial", 10))
        entry_valor.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Descrição
        tk.Label(frame_campos, text="Descrição:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=(0, 5))
        entry_descricao = tk.Entry(frame_campos, width=30, font=("Arial", 10))
        entry_descricao.grid(row=2, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Status label
        lbl_status = tk.Label(frame_principal, text="", fg="green", font=("Arial", 10))
        lbl_status.pack(pady=(0, 15))
        
        def validar_campos():
            """Valida todos os campos do formulário"""
            conta = entry_conta.get().strip()
            valor = entry_valor.get().strip()
            
            if not all([conta, valor]):
                return False, "Preencha todos os campos obrigatórios!"
            
            if not conta.isdigit():
                return False, "Número da conta deve conter apenas dígitos!"
            
            try:
                valor_float = float(valor)
                if valor_float <= 0:
                    return False, "O valor do saque deve ser positivo!"
            except ValueError:
                return False, "Valor deve ser um número!"
            
            return True, ""
        
        def executar_saque():
            # Validar campos
            valido, mensagem_erro = validar_campos()
            if not valido:
                lbl_status.config(text=mensagem_erro, fg="red")
                return
            
            # Obter valores
            numero_conta = entry_conta.get().strip()
            valor = float(entry_valor.get().strip())
            descricao = entry_descricao.get().strip() or "Saque"
            
            try:
                # Verificar se conta existe
                conta = ContaRepository.buscar_por_numero(numero_conta)
                if not conta:
                    lbl_status.config(text="Conta não encontrada!", fg="red")
                    return
                
                # Extrair dados da conta
                saldo_atual = conta[3]  # saldo está na posição 3
                situacao = conta[8]     # situacao está na posição 8
                
                # Verificar se conta está ativa
                if situacao != 1:
                    lbl_status.config(text="Conta inativa! Não é possível sacar.", fg="red")
                    return
                
                # Verificar se há saldo suficiente
                if saldo_atual < valor:
                    lbl_status.config(text="Saldo insuficiente!", fg="red")
                    return
                
                # Executar saque - este método já chama criar_transacao internamente
                transacao_id = ContaServico.sacar(numero_conta, valor)
                
                if transacao_id is None:
                    lbl_status.config(text="Erro ao realizar saque!", fg="red")
                    return
                
                # Obter o novo saldo atualizado
                novo_saldo = ContaRepository.buscar_saldo(numero_conta)
                
                lbl_status.config(text=f"Saque realizado! Novo saldo: R$ {novo_saldo:.2f}", fg="green")
                
                # Limpar campos após sucesso
                entry_valor.delete(0, tk.END)
                entry_descricao.delete(0, tk.END)
                
                # Fechar após 3 segundos
                win.after(3000, win.destroy)
                
            except Exception as e:
                lbl_status.config(text=f"Erro ao realizar saque: {str(e)}", fg="red")
            
        # Frame para botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(pady=10)
        
        btn_sacar = tk.Button(frame_botoes, text="Sacar", command=executar_saque,
                            bg="#28a745", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_sacar.pack(side='left', padx=5)
        
        btn_limpar = tk.Button(frame_botoes, text="Limpar", command=lambda: [
            entry_conta.delete(0, tk.END),
            entry_valor.delete(0, tk.END),
            entry_descricao.delete(0, tk.END),
            lbl_status.config(text="")
        ], bg="#6c757d", fg="white", font=("Arial", 10, "bold"),
        width=12, height=2)
        btn_limpar.pack(side='left', padx=5)
        
        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=win.destroy,
                            bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_cancelar.pack(side='left', padx=5)
        
        # Configurar grid weights
        frame_campos.columnconfigure(1, weight=1)

    # ------------------ TRANSFERIR (REFORMULADA) ------------------
    def transferir():
        win = tk.Toplevel(janela)
        win.title("Transferir")
        win.geometry("500x500")
        win.resizable(True, True)
        
        # Frame principal
        frame_principal = tk.Frame(win)
        frame_principal.pack(padx=30, pady=30, fill='both', expand=True)
        
        tk.Label(frame_principal, text="TRANSFERIR ENTRE CONTAS", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para os campos
        frame_campos = tk.Frame(frame_principal)
        frame_campos.pack(fill='x', pady=(0, 20))
        
        # Conta de Origem
        tk.Label(frame_campos, text="Conta de Origem:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        entry_conta_origem = tk.Entry(frame_campos, width=15, font=("Arial", 10))
        entry_conta_origem.grid(row=0, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Conta de Destino
        tk.Label(frame_campos, text="Conta de Destino:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        entry_conta_destino = tk.Entry(frame_campos, width=15, font=("Arial", 10))
        entry_conta_destino.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Valor
        tk.Label(frame_campos, text="Valor da Transferência:*", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=(0, 5))
        entry_valor = tk.Entry(frame_campos, width=15, font=("Arial", 10))
        entry_valor.grid(row=2, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Descrição
        tk.Label(frame_campos, text="Descrição:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky='w', pady=(0, 5))
        entry_descricao = tk.Entry(frame_campos, width=30, font=("Arial", 10))
        entry_descricao.grid(row=3, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Status label
        lbl_status = tk.Label(frame_principal, text="", fg="green", font=("Arial", 10))
        lbl_status.pack(pady=(0, 15))
        
        def validar_campos():
            """Valida todos os campos do formulário"""
            conta_origem = entry_conta_origem.get().strip()
            conta_destino = entry_conta_destino.get().strip()
            valor = entry_valor.get().strip()
            
            if not all([conta_origem, conta_destino, valor]):
                return False, "Preencha todos os campos obrigatórios!"
            
            if not conta_origem.isdigit() or not conta_destino.isdigit():
                return False, "Números de conta devem conter apenas dígitos!"
            
            if conta_origem == conta_destino:
                return False, "Conta de origem e destino não podem ser iguais!"
            
            try:
                valor_float = float(valor)
                if valor_float <= 0:
                    return False, "O valor da transferência deve ser positivo!"
            except ValueError:
                return False, "Valor deve ser um número!"
            
            return True, ""
        
        def executar_transferencia():
            # Validar campos
            valido, mensagem_erro = validar_campos()
            if not valido:
                lbl_status.config(text=mensagem_erro, fg="red")
                return
            
            # Obter valores
            numero_conta_origem = entry_conta_origem.get().strip()
            numero_conta_destino = entry_conta_destino.get().strip()
            valor = float(entry_valor.get().strip())
            descricao = entry_descricao.get().strip() or "Transferência"
            
            try:
                # Verificar se conta de origem existe
                conta_origem = ContaRepository.buscar_por_numero(numero_conta_origem)
                if not conta_origem:
                    lbl_status.config(text="Conta de origem não encontrada!", fg="red")
                    return
                
                # Extrair dados da conta
                saldo_origem = conta_origem[3]  # saldo está na posição 3
                situacao_origem = conta_origem[8]  # situacao está na posição 8
                
                # Verificar se conta de origem está ativa
                if situacao_origem != 1:
                    lbl_status.config(text="Conta de origem inativa!", fg="red")
                    return
                
                # Verificar se conta de destino existe
                conta_destino = ContaRepository.buscar_por_numero(numero_conta_destino)
                if not conta_destino:
                    lbl_status.config(text="Conta de destino não encontrada!", fg="red")
                    return
                
                situacao_destino = conta_destino[8]  # situacao está na posição 8
                
                # Verificar se conta de destino está ativa
                if situacao_destino != 1:
                    lbl_status.config(text="Conta de destino inativa!", fg="red")
                    return
                
                # Verificar se há saldo suficiente na conta de origem
                if saldo_origem < valor:
                    lbl_status.config(text="Saldo insuficiente na conta de origem!", fg="red")
                    return
                
                # Executar transferência - este método já chama criar_transacao internamente
                transacao_id = ContaServico.transferir(numero_conta_origem, numero_conta_destino, valor)
                
                if transacao_id is None:
                    lbl_status.config(text="Erro ao realizar transferência!", fg="red")
                    return
                
                # Buscar novo saldo da conta de origem
                novo_saldo_origem = ContaRepository.buscar_saldo(numero_conta_origem)
                
                lbl_status.config(text=f"Transferência realizada! Novo saldo: R$ {novo_saldo_origem:.2f}", fg="green")
                
                # Limpar campos após sucesso
                entry_valor.delete(0, tk.END)
                entry_descricao.delete(0, tk.END)
                
                # Fechar após 3 segundos
                win.after(3000, win.destroy)
                
            except Exception as e:
                lbl_status.config(text=f"Erro ao realizar transferência: {str(e)}", fg="red")
                
        # Frame para botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(pady=10)
        
        btn_transferir = tk.Button(frame_botoes, text="Transferir", command=executar_transferencia,
                                bg="#28a745", fg="white", font=("Arial", 10, "bold"),
                                width=12, height=2)
        btn_transferir.pack(side='left', padx=5)
        
        btn_limpar = tk.Button(frame_botoes, text="Limpar", command=lambda: [
            entry_conta_origem.delete(0, tk.END),
            entry_conta_destino.delete(0, tk.END),
            entry_valor.delete(0, tk.END),
            entry_descricao.delete(0, tk.END),
            lbl_status.config(text="")
        ], bg="#6c757d", fg="white", font=("Arial", 10, "bold"),
        width=12, height=2)
        btn_limpar.pack(side='left', padx=5)
        
        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=win.destroy,
                            bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_cancelar.pack(side='left', padx=5)
        
        # Configurar grid weights
        frame_campos.columnconfigure(1, weight=1)

    # ------------------ CONSULTAR EXTRATO (REFORMULADA) ------------------
    
    def consultar_extrato():
        win = tk.Toplevel(janela)
        win.title("Consultar Extrato")
        win.geometry("700x800")
        win.resizable(True, True)
        
        # Frame principal
        frame_principal = tk.Frame(win)
        frame_principal.pack(padx=30, pady=30, fill='both', expand=True)
        
        tk.Label(frame_principal, text="CONSULTAR EXTRATO BANCÁRIO", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para busca
        frame_busca = tk.Frame(frame_principal)
        frame_busca.pack(fill='x', pady=(0, 20))
        
        # Número da Conta
        tk.Label(frame_busca, text="Número da Conta:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        entry_conta = tk.Entry(frame_busca, width=15, font=("Arial", 10))
        entry_conta.grid(row=0, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        # Período
        tk.Label(frame_busca, text="Período:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        frame_periodo = tk.Frame(frame_busca)
        frame_periodo.grid(row=1, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        # Data inicial
        tk.Label(frame_periodo, text="De:", font=("Arial", 9)).pack(side='left')
        entry_data_inicio = tk.Entry(frame_periodo, width=10, font=("Arial", 9))
        entry_data_inicio.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        entry_data_inicio.pack(side='left', padx=(5, 10))
        
        # Data final
        tk.Label(frame_periodo, text="Até:", font=("Arial", 9)).pack(side='left')
        entry_data_fim = tk.Entry(frame_periodo, width=10, font=("Arial", 9))
        entry_data_fim.insert(0, datetime.now().strftime("%Y-%m-%d"))
        entry_data_fim.pack(side='left', padx=(5, 0))
        
        def validar_campos():
            """Valida todos os campos do formulário"""
            conta = entry_conta.get().strip()
            
            if not conta:
                return False, "Informe o número da conta!"
            
            if not conta.isdigit():
                return False, "Número da conta deve conter apenas dígitos!"
            
            # Validar datas se informadas
            data_inicio = entry_data_inicio.get().strip()
            data_fim = entry_data_fim.get().strip()
            
            if data_inicio:
                try:
                    datetime.strptime(data_inicio, "%Y-%m-%d")
                except ValueError:
                    return False, "Data inicial em formato inválido! Use AAAA-MM-DD."
            
            if data_fim:
                try:
                    datetime.strptime(data_fim, "%Y-%m-%d")
                except ValueError:
                    return False, "Data final em formato inválido! Use AAAA-MM-DD."
            
            return True, ""
        
        def consultar():
            # Validar campos
            valido, mensagem_erro = validar_campos()
            if not valido:
                lbl_status.config(text=mensagem_erro, fg="red")
                return
            
            # Obter valores
            numero_conta = entry_conta.get().strip()
            data_inicio = entry_data_inicio.get().strip() or None
            data_fim = entry_data_fim.get().strip() or None
            
            try:
                # Verificar se conta existe
                conta = ContaRepository.buscar_por_numero(numero_conta)
                if not conta:
                    lbl_status.config(text="Conta não encontrada!", fg="red")
                    return
                
                # Extrair dados da conta
                saldo_atual = conta[3]  # saldo está na posição 3
                
                # Atualizar saldo
                lbl_saldo_valor.config(text=f"R$ {saldo_atual:.2f}")
                
                # Limpar treeview
                for item in tree.get_children():
                    tree.delete(item)
                
                # Buscar transações com filtro de período
                transacoes = TransacaoRepository.buscar_extrato(numero_conta, data_inicio, data_fim)
                
                if not transacoes:
                    lbl_status.config(text="Nenhuma transação encontrada!", fg="orange")
                    return
                
                # Adicionar transações ao treeview
                for transacao in transacoes:
                    # Estrutura: (id, tipo, valor, conta_origem, conta_destino, data_hora, saldo_apos_transacao)
                    transacao_id, tipo, valor, conta_origem, conta_destino, data_hora, saldo_apos = transacao
                    
                    # Formatar data/hora
                    data_formatada = datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                    
                    # Determinar descrição baseada no tipo
                    if tipo == "DEPOSITO" or tipo == "DEPOSITO_INICIAL":
                        descricao = "Depósito"
                        valor_formatado = f"+R$ {valor:.2f}"
                        tipo_traduzido = "Depósito"
                        cor_valor = "green"
                    elif tipo == "SAQUE":
                        descricao = "Saque"
                        valor_formatado = f"-R$ {valor:.2f}"
                        tipo_traduzido = "Saque"
                        cor_valor = "red"
                    elif tipo == "TRANSFERENCIA":
                        if conta_origem == numero_conta:
                            descricao = f"Transferência para conta {conta_destino}"
                            valor_formatado = f"-R$ {valor:.2f}"
                            tipo_traduzido = "Transf. Saída"
                            cor_valor = "red"
                        else:
                            descricao = f"Transferência da conta {conta_origem}"
                            valor_formatado = f"+R$ {valor:.2f}"
                            tipo_traduzido = "Transf. Entrada"
                            cor_valor = "green"
                    else:
                        descricao = tipo
                        valor_formatado = f"R$ {valor:.2f}"
                        tipo_traduzido = tipo
                        cor_valor = "black"
                    
                    item = tree.insert("", "end", values=(
                        data_formatada,
                        tipo_traduzido,
                        valor_formatado,
                        descricao
                    ))
                    # Definir cor do valor
                    tree.set(item, "valor", valor_formatado)
                    
                lbl_status.config(text=f"Extrato consultado! {len(transacoes)} transações encontradas.", fg="green")
                
            except Exception as e:
                lbl_status.config(text=f"Erro ao consultar extrato: {str(e)}", fg="red")
        
        # Botão de consulta
        btn_consultar = tk.Button(frame_busca, text="Consultar Extrato", command=consultar,
                                bg="#17a2b8", fg="white", font=("Arial", 10, "bold"),
                                width=15)
        btn_consultar.grid(row=2, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        
        # Separador
        ttk.Separator(frame_principal, orient='horizontal').pack(fill='x', pady=(0, 20))
        
        # Frame para resultados
        frame_resultados = tk.Frame(frame_principal)
        frame_resultados.pack(fill='both', expand=True, pady=(0, 20))
        
        # Treeview para exibir o extrato
        columns = ("data", "tipo", "valor", "descricao")
        tree = ttk.Treeview(frame_resultados, columns=columns, show="headings", height=15)
        
        tree.heading("data", text="Data/Hora")
        tree.heading("tipo", text="Tipo")
        tree.heading("valor", text="Valor (R$)")
        tree.heading("descricao", text="Descrição")
        
        tree.column("data", width=120, anchor="center")
        tree.column("tipo", width=100, anchor="center")
        tree.column("valor", width=100, anchor="center")
        tree.column("descricao", width=200, anchor="w")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_resultados, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Frame para saldo
        frame_saldo = tk.Frame(frame_principal)
        frame_saldo.pack(fill='x', pady=(0, 15))
        
        lbl_saldo_titulo = tk.Label(frame_saldo, text="Saldo Atual:", font=("Arial", 10, "bold"))
        lbl_saldo_titulo.pack(side='left')
        
        lbl_saldo_valor = tk.Label(frame_saldo, text="R$ 0,00", font=("Arial", 10, "bold"), fg="green")
        lbl_saldo_valor.pack(side='left', padx=(5, 0))
        
        # Status label
        lbl_status = tk.Label(frame_principal, text="", fg="green", font=("Arial", 10))
        lbl_status.pack(pady=(0, 15))
        
        # Frame para botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(pady=10)

        def limpar_campos():
            entry_conta.delete(0, tk.END)
            entry_data_inicio.delete(0, tk.END)
            entry_data_inicio.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
            entry_data_fim.delete(0, tk.END)
            entry_data_fim.insert(0, datetime.now().strftime("%Y-%m-%d"))
            for item in tree.get_children():
                tree.delete(item)
            lbl_saldo_valor.config(text="R$ 0,00")
            lbl_status.config(text="")

        def imprimir_extrato(tree):
            """Função para imprimir o extrato (simulação)"""
            items = tree.get_children()
            if not items:
                messagebox.showinfo("Imprimir", "Nenhum dado para imprimir!")
                return
            
        messagebox.showinfo("Imprimir", "Extrato enviado para impressão!")

        btn_limpar = tk.Button(frame_botoes, text="Limpar", command=limpar_campos,
                            bg="#6c757d", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_limpar.pack(side='left', padx=5)

        btn_imprimir = tk.Button(frame_botoes, text="Imprimir", command=lambda: imprimir_extrato(tree),
                            bg="#17a2b8", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_imprimir.pack(side='left', padx=5)

        btn_fechar = tk.Button(frame_botoes, text="Fechar", command=win.destroy,
                            bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_fechar.pack(side='left', padx=5)

        # Configurar grid weights
        frame_busca.columnconfigure(1, weight=1)
        frame_resultados.columnconfigure(0, weight=1)
        frame_resultados.rowconfigure(0, weight=1)

    
    # ------------------ LISTAR TODOS OS CLIENTES (REFORMULADA) ------------------
    def listar_todos_clientes():
        win = tk.Toplevel(janela)
        win.title("Listar Todos os Clientes")
        win.geometry("1000x700")
        win.resizable(True, True)
        
        # Frame principal
        frame_principal = tk.Frame(win)
        frame_principal.pack(padx=30, pady=30, fill='both', expand=True)
        
        tk.Label(frame_principal, text="LISTA DE TODOS OS CLIENTES", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para filtros
        frame_filtros = tk.LabelFrame(frame_principal, text=" Filtros ", font=("Arial", 11, "bold"))
        frame_filtros.pack(fill='x', pady=(0, 20), ipadx=10, ipady=10)
        
        # Tipo de cliente
        tk.Label(frame_filtros, text="Tipo de Cliente:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=5, padx=10)
        
        # Variável para agrupamento visual dos radio buttons
        tipo_var = tk.StringVar(value="TODOS")
        
        def set_tipo_filtro(valor):
            global tipo_filtro
            tipo_filtro = valor
        
        rdb_todos = tk.Radiobutton(frame_filtros, text="Todos", variable=tipo_var, value="TODOS", 
                                font=("Arial", 9), command=lambda: set_tipo_filtro("TODOS"))
        rdb_todos.grid(row=0, column=1, sticky='w', padx=(10, 0))
        
        rdb_pf = tk.Radiobutton(frame_filtros, text="Pessoa Física", variable=tipo_var, value="PF", 
                            font=("Arial", 9), command=lambda: set_tipo_filtro("PF"))
        rdb_pf.grid(row=0, column=2, sticky='w', padx=(10, 0))
        
        rdb_pj = tk.Radiobutton(frame_filtros, text="Pessoa Jurídica", variable=tipo_var, value="PJ", 
                            font=("Arial", 9), command=lambda: set_tipo_filtro("PJ"))
        rdb_pj.grid(row=0, column=3, sticky='w', padx=(10, 0))
        
        # Situação
        tk.Label(frame_filtros, text="Situação:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=5, padx=10)
        
        # Variável para agrupamento visual dos radio buttons
        situacao_var = tk.StringVar(value="TODOS")
        
        def set_situacao_filtro(valor):
            global situacao_filtro
            situacao_filtro = valor
        
        rdb_sit_todos = tk.Radiobutton(frame_filtros, text="Todos", variable=situacao_var, value="TODOS", 
                                    font=("Arial", 9), command=lambda: set_situacao_filtro("TODOS"))
        rdb_sit_todos.grid(row=1, column=1, sticky='w', padx=(10, 0))
        
        rdb_sit_ativo = tk.Radiobutton(frame_filtros, text="Ativos", variable=situacao_var, value="1", 
                                    font=("Arial", 9), command=lambda: set_situacao_filtro("1"))
        rdb_sit_ativo.grid(row=1, column=2, sticky='w', padx=(10, 0))
        
        rdb_sit_inativo = tk.Radiobutton(frame_filtros, text="Inativos", variable=situacao_var, value="0", 
                                    font=("Arial", 9), command=lambda: set_situacao_filtro("0"))
        rdb_sit_inativo.grid(row=1, column=3, sticky='w', padx=(10, 0))
        
        # Frame para botões de filtro
        frame_botoes_filtro = tk.Frame(frame_filtros)
        frame_botoes_filtro.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        # Função para carregar todos os clientes
        def carregar_clientes():
            """Carrega todos os clientes sem filtro"""
            for item in tree.get_children():
                tree.delete(item)
            
            try:
                # Buscar clientes PF
                clientes_pf = ClienteRepository.buscar_todos_pf()
                for cliente in clientes_pf:
                    id, cpf, nome, endereco, situacao_cliente, data_cadastro = cliente
                    situacao_texto = "Ativo" if situacao_cliente == 1 else "Inativo"
                    tree.insert("", "end", values=(
                        "PF", cpf, nome, endereco if endereco else "", situacao_texto, data_cadastro
                    ))
                
                # Buscar clientes PJ
                clientes_pj = ClienteRepository.buscar_todos_pj()
                for cliente in clientes_pj:
                    id, cnpj, razao_social, endereco, situacao_cliente, data_cadastro = cliente
                    situacao_texto = "Ativo" if situacao_cliente == 1 else "Inativo"
                    tree.insert("", "end", values=(
                        "PJ", cnpj, razao_social, endereco if endereco else "", situacao_texto, data_cadastro
                    ))
                
                total = len(clientes_pf) + len(clientes_pj)
                lbl_status.config(text=f"Total de clientes: {total}", fg="green")
                
            except Exception as e:
                lbl_status.config(text=f"Erro ao carregar clientes: {str(e)}", fg="red")
        
        # Função para filtrar clientes
        def filtrar_clientes():
            """Filtra os clientes com base nos critérios selecionados"""
            for item in tree.get_children():
                tree.delete(item)
            
            try:
                total = 0
                situacao_param = None if situacao_filtro == "TODOS" else int(situacao_filtro)
                
                # Buscar e exibir PF
                if tipo_filtro in ["TODOS", "PF"]:
                    clientes_pf = ClienteRepository.buscar_todos_pf(situacao_param)
                    
                    for cliente in clientes_pf:
                        id, cpf, nome, endereco, sit_cliente_db, data_cadastro = cliente
                        situacao_texto = "Ativo" if sit_cliente_db == 1 else "Inativo"
                        tree.insert("", "end", values=(
                            "PF", cpf, nome, endereco or "", situacao_texto, data_cadastro or ""
                        ))
                        total += 1

                # Buscar e exibir PJ
                if tipo_filtro in ["TODOS", "PJ"]:
                    clientes_pj = ClienteRepository.buscar_todos_pj(situacao_param)
                    
                    for cliente in clientes_pj:
                        id, cnpj, razao_social, endereco, sit_cliente_db, data_cadastro = cliente
                        situacao_texto = "Ativo" if sit_cliente_db == 1 else "Inativo"
                        tree.insert("", "end", values=(
                            "PJ", cnpj, razao_social, endereco or "", situacao_texto, data_cadastro or ""
                        ))
                        total += 1

                lbl_status.config(text=f"Clientes encontrados: {total}", fg="green")

            except Exception as e:
                lbl_status.config(text=f"Erro ao filtrar clientes: {str(e)}", fg="red")
        
        btn_filtrar = tk.Button(frame_botoes_filtro, text="Aplicar Filtros", command=filtrar_clientes,
                            bg="#17a2b8", fg="white", font=("Arial", 10, "bold"),
                            width=15, height=1)
        btn_filtrar.pack(side='left', padx=5)
        
        btn_limpar_filtros = tk.Button(frame_botoes_filtro, text="Limpar Filtros", 
                                    command=lambda: [tipo_var.set("TODOS"), situacao_var.set("TODOS"),
                                                    set_tipo_filtro("TODOS"), set_situacao_filtro("TODOS")],
                                    bg="#6c757d", fg="white", font=("Arial", 10),
                                    width=15, height=1)
        btn_limpar_filtros.pack(side='left', padx=5)
        
        # Frame para resultados
        frame_resultados = tk.LabelFrame(frame_principal, text=" Resultados ", font=("Arial", 11, "bold"))
        frame_resultados.pack(fill='both', expand=True, pady=(0, 20), ipadx=10, ipady=10)
        
        # Treeview para exibir os clientes
        columns = ("tipo", "documento", "nome", "endereco", "situacao", "data_cadastro")
        tree = ttk.Treeview(frame_resultados, columns=columns, show="headings", height=15)

        tree.heading("tipo", text="Tipo")
        tree.heading("documento", text="CPF/CNPJ")
        tree.heading("nome", text="Nome/Razão Social")
        tree.heading("endereco", text="Endereço")
        tree.heading("situacao", text="Situação")
        tree.heading("data_cadastro", text="Data Cadastro")

        tree.column("tipo", width=80, anchor="center")
        tree.column("documento", width=120, anchor="center")
        tree.column("nome", width=180, anchor="w")
        tree.column("endereco", width=150, anchor="w")
        tree.column("situacao", width=80, anchor="center")
        tree.column("data_cadastro", width=100, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_resultados, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Configurar grid weights para expansão
        frame_resultados.grid_rowconfigure(0, weight=1)
        frame_resultados.grid_columnconfigure(0, weight=1)

        # Status label
        lbl_status = tk.Label(frame_principal, text="", fg="green", font=("Arial", 10))
        lbl_status.pack(pady=(0, 15))

        # Separador
        ttk.Separator(frame_principal, orient='horizontal').pack(fill='x', pady=(0, 20))

        # Frame para botões de ação
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(pady=10)

        btn_atualizar = tk.Button(frame_botoes, text="Atualizar", command=carregar_clientes,
                                bg="#28a745", fg="white", font=("Arial", 10, "bold"),
                                width=12, height=1)
        btn_atualizar.pack(side='left', padx=5)

        def visualizar_cliente():
            """Abre a visualização do cliente selecionado"""
            selecionado = tree.focus()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione um cliente para visualizar!")
                return
            
            item = tree.item(selecionado)
            tipo_cliente = item['values'][0]
            documento = item['values'][1]
            
            # Aqui você pode implementar a abertura da tela de visualização
            messagebox.showinfo("Visualizar", f"Visualizando {tipo_cliente}: {documento}")

        btn_visualizar = tk.Button(frame_botoes, text="Visualizar", command=visualizar_cliente,
                                bg="#17a2b8", fg="white", font=("Arial", 10, "bold"),
                                width=12, height=1)
        btn_visualizar.pack(side='left', padx=5)

        btn_fechar = tk.Button(frame_botoes, text="Fechar", command=win.destroy,
                            bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=1)
        btn_fechar.pack(side='left', padx=5)

        # Configurar grid weights
        for i in range(4):
            frame_filtros.columnconfigure(i, weight=1)
        
        frame_resultados.columnconfigure(0, weight=1)
        frame_resultados.rowconfigure(0, weight=1)

        # Carregar todos os clientes inicialmente
        carregar_clientes()
##############################################################################################################################

    def cadastrar_funcionario():
        if tipo_usuario != "gerente":
            messagebox.showerror("Acesso Negado", "Apenas gerentes podem cadastrar funcionários!")
            return

        win = tk.Toplevel(janela)
        win.title("Cadastrar Funcionário")
        win.geometry("500x600")
        win.resizable(True, True)
        
        # Frame principal
        frame_principal = tk.Frame(win)
        frame_principal.pack(padx=30, pady=30, fill='both', expand=True)
        
        tk.Label(frame_principal, text="CADASTRAR FUNCIONÁRIO/GERENTE", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para os campos
        frame_campos = tk.Frame(frame_principal)
        frame_campos.pack(fill='x', pady=(0, 20))
        
        # CPF
        tk.Label(frame_campos, text="CPF:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        entry_cpf = tk.Entry(frame_campos, width=20, font=("Arial", 10))
        entry_cpf.grid(row=0, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Nome
        tk.Label(frame_campos, text="Nome Completo:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        entry_nome = tk.Entry(frame_campos, width=30, font=("Arial", 10))
        entry_nome.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Cargo
        tk.Label(frame_campos, text="Cargo:*", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=(0, 5))
        entry_cargo = tk.Entry(frame_campos, width=25, font=("Arial", 10))
        entry_cargo.grid(row=2, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Tipo de usuário
        tk.Label(frame_campos, text="Tipo de Usuário:*", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky='w', pady=(0, 5))
        frame_tipo = tk.Frame(frame_campos)
        frame_tipo.grid(row=3, column=1, sticky='w', pady=(0, 10), padx=(10, 0))
        tipo_var = tk.StringVar(value="funcionario")
        tk.Radiobutton(frame_tipo, text="Funcionário", variable=tipo_var, value="funcionario", 
                    font=("Arial", 9)).pack(side='left')
        tk.Radiobutton(frame_tipo, text="Gerente", variable=tipo_var, value="gerente", 
                    font=("Arial", 9)).pack(side='left', padx=(10, 0))
        
        # Situação
        tk.Label(frame_campos, text="Situação:*", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky='w', pady=(0, 5))
        frame_situacao = tk.Frame(frame_campos)
        frame_situacao.grid(row=4, column=1, sticky='w', pady=(0, 15), padx=(10, 0))
        situacao_var = tk.StringVar(value="1")
        tk.Radiobutton(frame_situacao, text="Ativo", variable=situacao_var, value="1", 
                    font=("Arial", 9)).pack(side='left')
        tk.Radiobutton(frame_situacao, text="Inativo", variable=situacao_var, value="0", 
                    font=("Arial", 9)).pack(side='left', padx=(10, 0))
        
        # Separador
        ttk.Separator(frame_principal, orient='horizontal').pack(fill='x', pady=(0, 20))
        
        tk.Label(frame_principal, text="DADOS DE ACESSO", font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Frame para dados de acesso
        frame_acesso = tk.Frame(frame_principal)
        frame_acesso.pack(fill='x', pady=(0, 20))
        
        # Login
        tk.Label(frame_acesso, text="Login:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        entry_login = tk.Entry(frame_acesso, width=20, font=("Arial", 10))
        entry_login.grid(row=0, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Senha
        tk.Label(frame_acesso, text="Senha:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        entry_senha = tk.Entry(frame_acesso, width=20, show="*", font=("Arial", 10))
        entry_senha.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Confirmar Senha
        tk.Label(frame_acesso, text="Confirmar Senha:*", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=(0, 5))
        entry_confirmar_senha = tk.Entry(frame_acesso, width=20, show="*", font=("Arial", 10))
        entry_confirmar_senha.grid(row=2, column=1, sticky='ew', pady=(0, 15), padx=(10, 0))
        
        # Status label
        lbl_status = tk.Label(frame_principal, text="", fg="green", font=("Arial", 10))
        lbl_status.pack(pady=(0, 15))
        
        def validar_cpf(cpf):
            """Validação simples de CPF"""
            cpf = ''.join(filter(str.isdigit, cpf))
            return len(cpf) == 11
        
        def validar_campos():
            """Valida todos os campos do formulário"""
            cpf = entry_cpf.get().strip()
            nome = entry_nome.get().strip()
            cargo = entry_cargo.get().strip()
            login = entry_login.get().strip()
            senha = entry_senha.get().strip()
            confirmar_senha = entry_confirmar_senha.get().strip()
            
            if not all([cpf, nome, cargo, login, senha, confirmar_senha]):
                return False, "Preencha todos os campos obrigatórios!"
            
            if not validar_cpf(cpf):
                return False, "CPF inválido! Deve ter 11 dígitos."
            
            if senha != confirmar_senha:
                return False, "As senhas não coincidem!"
            
            if len(senha) < 5:
                return False, "A senha deve ter pelo menos 6 caracteres!"
            
            return True, ""
        
        def salvar():
            # Validar campos
            valido, mensagem_erro = validar_campos()
            if not valido:
                lbl_status.config(text=mensagem_erro, fg="red")
                return
            
            # Obter valores
            cpf = ''.join(filter(str.isdigit, entry_cpf.get().strip()))
            nome = entry_nome.get().strip()
            cargo = entry_cargo.get().strip()
            login = entry_login.get().strip()
            senha = entry_senha.get().strip()
            tipo = tipo_var.get()
            situacao = int(situacao_var.get())
            data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                # Verificar se CPF já existe
                if FuncionarioRepository.buscar_funcionario(cpf):
                    lbl_status.config(text="CPF já cadastrado para outro funcionário!", fg="red")
                    return
                
                # Verificar se login já existe
                if UsuarioRepository.buscar_por_login(login):
                    lbl_status.config(text="Login já está em uso! Escolha outro.", fg="red")
                    return
                
                # Salvar funcionário
                funcionario_id = FuncionarioRepository.salvar_funcionario(
                    cpf=cpf,
                    nome=nome,
                    cargo=cargo,
                    data_cadastro=data_cadastro,
                    situacao_funcionario=situacao
                )
                
                # Salvar usuário
                UsuarioServico.cadastrar(
                    login=login,
                    senha=senha,
                    tipo_usuario=tipo,
                    funcionario_id=funcionario_id,
                    data_cadastro=data_cadastro
                )
                
                lbl_status.config(text="Funcionário cadastrado com sucesso!", fg="green")
                
                # Limpar campos após sucesso
                entry_cpf.delete(0, tk.END)
                entry_nome.delete(0, tk.END)
                entry_cargo.delete(0, tk.END)
                entry_login.delete(0, tk.END)
                entry_senha.delete(0, tk.END)
                entry_confirmar_senha.delete(0, tk.END)
                
                # Fechar após 2 segundos
                win.after(2000, win.destroy)
                
            except Exception as e:
                lbl_status.config(text=f"Erro ao cadastrar: {str(e)}", fg="red")
        
        # Frame para botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(pady=10)
        
        btn_salvar = tk.Button(frame_botoes, text="Cadastrar", command=salvar,
                            bg="#28a745", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_salvar.pack(side='left', padx=5)
        
        btn_limpar = tk.Button(frame_botoes, text="Limpar", command=lambda: [
            entry_cpf.delete(0, tk.END),
            entry_nome.delete(0, tk.END),
            entry_cargo.delete(0, tk.END),
            entry_login.delete(0, tk.END),
            entry_senha.delete(0, tk.END),
            entry_confirmar_senha.delete(0, tk.END),
            lbl_status.config(text="")
        ], bg="#6c757d", fg="white", font=("Arial", 10, "bold"),
        width=12, height=2)
        btn_limpar.pack(side='left', padx=5)
        
        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=win.destroy,
                            bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_cancelar.pack(side='left', padx=5)
        
        # Configurar grid weights
        frame_campos.columnconfigure(1, weight=1)
        frame_acesso.columnconfigure(1, weight=1)
#####################################################################################################

    def atualizar_login_senha_usuario():
        """Interface para atualizar login e senha de usuários"""
        win = tk.Toplevel(janela)
        win.title("Atualizar Login e Senha")
        win.geometry("500x500")
        win.resizable(True, True)
        
        # Frame principal
        frame_principal = tk.Frame(win)
        frame_principal.pack(padx=30, pady=30, fill='both', expand=True)
        
        tk.Label(frame_principal, text="ATUALIZAR LOGIN E SENHA", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para seleção do usuário
        frame_selecao = tk.Frame(frame_principal)
        frame_selecao.pack(fill='x', pady=(0, 20))
        
        # Selecionar Usuário
        tk.Label(frame_selecao, text="Selecionar Usuário:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        # Buscar todos os usuários
        usuarios = UsuarioRepository.buscar_todos_usuarios()
        usuarios_combo = []
        usuarios_dict = {}
        
        for usuario in usuarios:
            usuario_id, login, tipo_usuario, data_cadastro = usuario
            display_text = f"{login} ({tipo_usuario})"
            usuarios_combo.append(display_text)
            usuarios_dict[display_text] = usuario_id
        
        usuario_var = tk.StringVar()
        combo_usuario = ttk.Combobox(frame_selecao, textvariable=usuario_var, 
                                values=usuarios_combo, state="readonly",
                                font=("Arial", 10), width=25)
        combo_usuario.grid(row=0, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Separador----------
        ttk.Separator(frame_principal, orient='horizontal').pack(fill='x', pady=(0, 20))
        
        tk.Label(frame_principal, text="NOVOS DADOS DE ACESSO", 
                font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Frame para dados de acesso
        frame_dados = tk.Frame(frame_principal)
        frame_dados.pack(fill='x', pady=(0, 20))
        
        # Novo Login
        tk.Label(frame_dados, text="Novo Login:*", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5))
        entry_novo_login = tk.Entry(frame_dados, width=25, font=("Arial", 10))
        entry_novo_login.grid(row=0, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Nova Senha
        tk.Label(frame_dados, text="Nova Senha:*", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5))
        entry_nova_senha = tk.Entry(frame_dados, width=25, show="*", font=("Arial", 10))
        entry_nova_senha.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Confirmar Senha
        tk.Label(frame_dados, text="Confirmar Senha:*", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=(0, 5))
        entry_confirmar_senha = tk.Entry(frame_dados, width=25, show="*", font=("Arial", 10))
        entry_confirmar_senha.grid(row=2, column=1, sticky='ew', pady=(0, 15), padx=(10, 0))
        
        # Status label
        lbl_status = tk.Label(frame_principal, text="", fg="green", font=("Arial", 10))
        lbl_status.pack(pady=(0, 15))
        
        def carregar_dados_usuario(event):
            """Carrega os dados do usuário selecionado"""
            usuario_selecionado = usuario_var.get()
            if usuario_selecionado in usuarios_dict:
                usuario_id = usuarios_dict[usuario_selecionado]
                try:
                    usuario = UsuarioRepository.buscar_por_id(usuario_id)
                    if usuario:
                        # usuario[1] é o login atual
                        entry_novo_login.delete(0, tk.END)
                        entry_novo_login.insert(0, usuario[1])
                except Exception as e:
                    lbl_status.config(text=f"Erro ao carregar dados: {str(e)}", fg="red")
        
        combo_usuario.bind("<<ComboboxSelected>>", carregar_dados_usuario)
        
        def validar_campos():
            """Valida todos os campos do formulário"""
            usuario_selecionado = usuario_var.get()
            novo_login = entry_novo_login.get().strip()
            nova_senha = entry_nova_senha.get().strip()
            confirmar_senha = entry_confirmar_senha.get().strip()
            
            if not usuario_selecionado:
                return False, "Selecione um usuário!"
            
            if not novo_login:
                return False, "O novo login não pode estar vazio!"
            
            if not nova_senha:
                return False, "A nova senha não pode estar vazia!"
            
            if nova_senha != confirmar_senha:
                return False, "As senhas não coincidem!"
            
            if len(nova_senha) < 4:
                return False, "A senha deve ter pelo menos 4 caracteres!"
            
            return True, ""
        
        def atualizar_dados():
            """Atualiza o login e senha do usuário selecionado"""
            # Validar campos
            valido, mensagem_erro = validar_campos()
            if not valido:
                lbl_status.config(text=mensagem_erro, fg="red")
                return
            
            usuario_selecionado = usuario_var.get()
            usuario_id = usuarios_dict[usuario_selecionado]
            novo_login = entry_novo_login.get().strip()
            nova_senha = entry_nova_senha.get().strip()
            
            # Confirmação
            if not messagebox.askyesno("Confirmar", 
                                    f"Tem certeza que deseja atualizar os dados de {usuario_selecionado}?"):
                return
            
            try:
                # Verificar se o novo login já existe (exceto para o próprio usuário)
                usuario_existente = UsuarioRepository.buscar_por_login(novo_login)
                if usuario_existente and usuario_existente[0] != usuario_id:
                    lbl_status.config(text="Este login já está em uso por outro usuário!", fg="red")
                    return
                
                # Atualizar os dados
                sucesso = UsuarioServico.atualizar_login_senha_pelo_gerente(usuario_id, novo_login, nova_senha)
                
                if sucesso:
                    lbl_status.config(text="Dados atualizados com sucesso!", fg="green")
                    
                    # Atualizar a lista de usuários
                    usuarios_novos = UsuarioRepository.buscar_todos_usuarios()
                    usuarios_combo.clear()
                    usuarios_dict.clear()
                    
                    for usuario in usuarios_novos:
                        usuario_id, login, tipo_usuario, data_cadastro = usuario
                        display_text = f"{login} ({tipo_usuario})"
                        usuarios_combo.append(display_text)
                        usuarios_dict[display_text] = usuario_id
                    
                    combo_usuario['values'] = usuarios_combo
                    usuario_var.set('')
                    entry_novo_login.delete(0, tk.END)
                    entry_nova_senha.delete(0, tk.END)
                    entry_confirmar_senha.delete(0, tk.END)
                    
                    # Fechar após 2 segundos
                    win.after(2000, win.destroy)
                else:
                    lbl_status.config(text="Erro ao atualizar os dados!", fg="red")
                    
            except Exception as e:
                lbl_status.config(text=f"Erro ao atualizar: {str(e)}", fg="red")
        
        def limpar_campos():
            """Limpa todos os campos"""
            usuario_var.set('')
            entry_novo_login.delete(0, tk.END)
            entry_nova_senha.delete(0, tk.END)
            entry_confirmar_senha.delete(0, tk.END)
            lbl_status.config(text="")
        
        # Frame para botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(pady=10)
        
        btn_atualizar = tk.Button(frame_botoes, text="Atualizar", command=atualizar_dados,
                                bg="#28a745", fg="white", font=("Arial", 10, "bold"),
                                width=12, height=2)
        btn_atualizar.pack(side='left', padx=5)
        
        btn_limpar = tk.Button(frame_botoes, text="Limpar", command=limpar_campos,
                            bg="#6c757d", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_limpar.pack(side='left', padx=5)
        
        btn_cancelar = tk.Button(frame_botoes, text="Cancelar", command=win.destroy,
                            bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=2)
        btn_cancelar.pack(side='left', padx=5)
        
        # Configurar grid weights
        frame_selecao.columnconfigure(1, weight=1)
        frame_dados.columnconfigure(1, weight=1)


##################################################################################################
    
    def consultar_conta_por_cliente():
        win = tk.Toplevel(janela)
        win.title("Consultar Conta por Cliente")
        win.geometry("900x700")  # Tamanho ajustado
        win.resizable(True, True)
        
        # Frame principal
        frame_principal = tk.Frame(win)
        frame_principal.pack(padx=30, pady=30, fill='both', expand=True)
        
        tk.Label(frame_principal, text="CONSULTAR CONTA POR CLIENTE", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para busca
        frame_busca = tk.LabelFrame(frame_principal, text=" Dados da Busca ", font=("Arial", 11, "bold"))
        frame_busca.pack(fill='x', pady=(0, 20), ipadx=10, ipady=10)
        
        # Tipo de busca
        tk.Label(frame_busca, text="Buscar por:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=(0, 5), padx=10)

        frame_tipo_busca = tk.Frame(frame_busca)
        frame_tipo_busca.grid(row=0, column=1, sticky='w', pady=(0, 10), padx=(10, 0))

        # Variável simples para armazenar o tipo de busca
        tipo_busca = "CPF"

        def set_tipo_busca(novo_tipo):
            global tipo_busca
            tipo_busca = novo_tipo
            #print("Tipo de busca Selecionado:", tipo_busca)
            
            # Atualizar visualmente qual radio button está selecionado
            if novo_tipo == "CPF":
                rdb_cpf.config(relief=tk.SUNKEN)
                rdb_cnpj.config(relief=tk.RAISED)
            else:
                rdb_cpf.config(relief=tk.RAISED)
                rdb_cnpj.config(relief=tk.SUNKEN)

        # Criar os radio buttons como botões normais com estilo diferenciado
        rdb_cpf = tk.Button(frame_tipo_busca, text="CPF", font=("Arial", 9),
                        command=lambda: set_tipo_busca("CPF"),
                        relief=tk.SUNKEN,  # Inicialmente selecionado
                        bg="#f0f0f0", width=10)
        rdb_cpf.pack(side='left')

        rdb_cnpj = tk.Button(frame_tipo_busca, text="CNPJ", font=("Arial", 9),
                            command=lambda: set_tipo_busca("CNPJ"),
                            relief=tk.RAISED,  # Inicialmente não selecionado
                            bg="#f0f0f0", width=10)
        rdb_cnpj.pack(side='left', padx=(10, 0))

        # Verificar o valor inicial
        #print("Tipo de busca Inicial:", tipo_busca)

        # Número do documento
        tk.Label(frame_busca, text="Número do CPF/CNPJ:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=(0, 5), padx=10)
        
        entry_busca = tk.Entry(frame_busca, width=25, font=("Arial", 10))
        entry_busca.grid(row=1, column=1, sticky='ew', pady=(0, 10), padx=(10, 0))
        
        # Frame para botão de busca
        frame_btn_busca = tk.Frame(frame_busca)
        frame_btn_busca.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        # Status label
        lbl_status = tk.Label(frame_principal, text="", fg="green", font=("Arial", 10))
        lbl_status.pack(pady=(0, 15))
        
        # Frame para resultados
        frame_resultados = tk.LabelFrame(frame_principal, text=" Resultados ", font=("Arial", 11, "bold"))
        frame_resultados.pack(fill='both', expand=True, pady=(0, 20), ipadx=10, ipady=10)
        
        # Treeview para mostrar as contas
        columns = ("Número da Conta", "Agência", "Tipo Cliente", "Saldo", "Situação", "Data Abertura")
        tree = ttk.Treeview(frame_resultados, columns=columns, show="headings", height=8)
        
        # Definir headings com larguras personalizadas
        tree.heading("Número da Conta", text="Número da Conta")
        tree.heading("Agência", text="Agência")
        tree.heading("Tipo Cliente", text="Tipo Cliente")
        tree.heading("Saldo", text="Saldo")
        tree.heading("Situação", text="Situação")
        tree.heading("Data Abertura", text="Data Abertura")
        
        tree.column("Número da Conta", width=120, anchor="center")
        tree.column("Agência", width=80, anchor="center")
        tree.column("Tipo Cliente", width=100, anchor="center")
        tree.column("Saldo", width=100, anchor="center")
        tree.column("Situação", width=80, anchor="center")
        tree.column("Data Abertura", width=100, anchor="center")
        
        # Scrollbar para a treeview
        scrollbar_y = ttk.Scrollbar(frame_resultados, orient="vertical", command=tree.yview)
        scrollbar_x = ttk.Scrollbar(frame_resultados, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        # Configurar grid weights para expansão
        frame_resultados.grid_rowconfigure(0, weight=1)
        frame_resultados.grid_columnconfigure(0, weight=1)
        
        def buscar_contas():
            # Declarar a variável como global
            global tipo_busca
            
            numero = entry_busca.get().strip()
            
            # Agora pode usar a variável global
            tipo_busca_utilizar = tipo_busca
            
            #print(f"Buscando por: {tipo_busca_utilizar}, Número: {numero}")  # Para debug
            
            if not numero:
                lbl_status.config(text="Digite um número para buscar!", fg="red")
                return
            
            # Resto do código da função buscar_contas...
            if tipo_busca_utilizar == "CPF":
                # Buscar cliente PF
                cliente = ClienteRepository.buscar_pf(numero)
                # ... resto do código para CPF
            else:
                # Buscar cliente PJ
                cliente = ClienteRepository.buscar_pj(numero)
                # ... resto do código para CNPJ
                    
            # Resto do código...
            
            # Limpar treeview
            for item in tree.get_children():
                tree.delete(item)
            
            try:
                if tipo_busca == "CPF":
                    # Buscar cliente PF primeiro
                    cliente = ClienteRepository.buscar_pf(numero)
                    if not cliente:
                        lbl_status.config(text="Cliente PF não encontrado!", fg="red")
                        return
                    
                    cliente_id, cpf, nome, endereco, situacao, data_cadastro = cliente
                    lbl_status.config(text=f"Cliente encontrado: {nome}", fg="green")
                    
                    # Buscar contas do cliente usando CPF
                    contas = ContaRepository.buscar_contas_por_cliente(numero, "PF")
                    
                else:  # CNPJ
                    # Buscar cliente PJ primeiro
                    cliente = ClienteRepository.buscar_pj(numero)
                    if not cliente:
                        lbl_status.config(text="Cliente PJ não encontrado!", fg="red")
                        return
                    
                    cliente_id, cnpj, razao_social, endereco, situacao, data_cadastro = cliente
                    lbl_status.config(text=f"Cliente encontrado: {razao_social}", fg="green")
                    
                    # Buscar contas do cliente usando CNPJ
                    contas = ContaRepository.buscar_contas_por_cliente(numero, "PJ")
                
                if not contas:
                    lbl_status.config(text="Cliente não possui contas cadastradas!", fg="orange")
                    return
                
                # Preencher treeview com as contas
                for conta in contas:
                    # Verifica o formato da conta retornada
                    if len(conta) >= 5:  # numero_conta, agencia, tipo_cliente, saldo, situacao, data_abertura
                        num_conta = conta[0]
                        agencia = conta[1] if len(conta) > 1 else "N/A"
                        tipo_cliente = conta[2] if len(conta) > 2 else "N/A"
                        saldo = conta[3] if len(conta) > 3 else 0
                        situacao_conta = conta[4] if len(conta) > 4 else 1
                        data_abertura = conta[5] if len(conta) > 5 else None
                        
                        # Converter valores para exibição
                        situacao_str = "Ativa" if situacao_conta == 1 else "Inativa"
                        saldo_str = f"R$ {saldo:,.2f}" if saldo is not None else "R$ 0,00"
                        data_str = data_abertura if data_abertura else "N/A"
                        
                        tree.insert("", "end", values=(num_conta, agencia, tipo_cliente, saldo_str, situacao_str, data_str))
                
                lbl_status.config(text=f"Encontradas {len(contas)} conta(s) para este cliente", fg="green")
                
            except Exception as e:
                lbl_status.config(text=f"Erro na busca: {str(e)}", fg="red")
        
        # Botão de busca
        btn_buscar = tk.Button(frame_btn_busca, text="Buscar Contas", command=buscar_contas,
                            bg="#17a2b8", fg="white", font=("Arial", 10, "bold"),
                            width=15, height=1)
        btn_buscar.pack(side='left', padx=5)
        
        def limpar_campos():
            """Limpa todos os campos"""
            entry_busca.delete(0, tk.END)
            for item in tree.get_children():
                tree.delete(item)
            lbl_status.config(text="")
        
        btn_limpar_busca = tk.Button(frame_btn_busca, text="Limpar", command=limpar_campos,
                                bg="#6c757d", fg="white", font=("Arial", 10),
                                width=12, height=1)
        btn_limpar_busca.pack(side='left', padx=5)
        
        # Frame para botões de ação
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(pady=10)
        
        def visualizar_conta():
            """Abre a visualização da conta selecionada"""
            selecionado = tree.focus()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione uma conta para visualizar!")
                return
            
            item = tree.item(selecionado)
            numero_conta = item['values'][0]
            
            # Aqui você pode implementar a abertura da tela de visualização da conta
            messagebox.showinfo("Visualizar", f"Visualizando conta: {numero_conta}")
        
        btn_visualizar = tk.Button(frame_botoes, text="Visualizar Conta", command=visualizar_conta,
                                bg="#17a2b8", fg="white", font=("Arial", 10, "bold"),
                                width=15, height=1)
        btn_visualizar.pack(side='left', padx=5)
        
        btn_fechar = tk.Button(frame_botoes, text="Fechar", command=win.destroy,
                            bg="#dc3545", fg="white", font=("Arial", 10, "bold"),
                            width=12, height=1)
        btn_fechar.pack(side='left', padx=5)
        
        # Configurar grid weights
        frame_busca.columnconfigure(1, weight=1)
        frame_resultados.columnconfigure(0, weight=1)
        frame_resultados.rowconfigure(0, weight=1)
        
        # Focar no campo de busca
        entry_busca.focus()



    # ---------- BOTÕES PRINCIPAIS ----------
    tk.Label(janela, text=f"Bem-vindo, {tipo_usuario.capitalize()}!", font=("Arial", 14)).pack(pady=10)
    tk.Button(janela, text="Cadastrar Cliente Pessoa Fisica", width=25, command=cadastrar_cliente_pf).pack(pady=5)
    tk.Button(janela, text="Cadastrar Cliente Pessoa Juridica", width=25, command=cadastrar_cliente_pj).pack(pady=5)
    tk.Button(janela, text="Consulta Conta por Cliente", width=25, command=consultar_conta_por_cliente).pack(pady=5)
    tk.Button(janela, text="Listar Todos os Clientes", width=25, command=listar_todos_clientes).pack(pady=5)
    tk.Button(janela, text="Criar Conta", width=25, command=criar_conta).pack(pady=5)
    tk.Button(janela, text="Depositar", width=25, command=depositar).pack(pady=5)
    tk.Button(janela, text="Sacar", width=25, command=sacar).pack(pady=5)
    tk.Button(janela, text="Transferir", width=25, command=transferir).pack(pady=5)
    tk.Button(janela, text="Consultar Extrato", width=25, command=consultar_extrato).pack(pady=5)
    tk.Button(janela, text="Atualizar Dados do Cliente", width=25, command=atualizar_cliente).pack(pady=5)

    # SOMENTE GERENTE pode cadastrar funcionários
    if tipo_usuario == "gerente":
        tk.Button(janela, text="Cadastrar Funcionário/Gerente", width=25, command=cadastrar_funcionario).pack(pady=5)
        tk.Button(janela, text="Atualizar Login/Senha Usuário", width=25, command=atualizar_login_senha_usuario).pack(pady=5)
    tk.Button(janela, text="Sair", width=25, command=janela.destroy).pack(pady=20)
    
    janela.mainloop()
    tela_login() # Volta para a tela de login ao fechar a janela principal
# ------------------ MAIN ------------------
if __name__ == "__main__":
    connection.criar_tabelas()
    with connection.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo_usuario='gerente'")
        qtd_gerentes = cursor.fetchone()[0]

    if qtd_gerentes == 0:
        tela_super_gerente()
    else:
        tela_login()
