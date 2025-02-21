import sqlite3
import customtkinter as ctk
from tkinter import messagebox
from .CTkFloatingNotifications import *

# Função de validação dos dados de login
def validacao_login():
    from .ui_tela_principal import janela_principal
    notification_manager = NotificationManager(root_login)


    global nome_completo_usuario, abas_permitidas
    usuario = entry_usuario.get().strip().lower()  # Remover espaços e converter para minúsculas
    senha = entry_senha.get()  # Recebe a senha do entrybox

    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect(r'app\bd\login.db')  # Caminho para o banco de dados
        cursor = conn.cursor()

        # Consultar se o usuário existe no banco de dados (sem diferenciar maiúsculas e minúsculas)
        cursor.execute("SELECT senha, nome_completo, abas FROM dados_login WHERE LOWER(nome_usuario) = ?", (usuario,))
        resultado = cursor.fetchone()

        # Fechar a conexão com o banco de dados
        conn.close()

        # Verifica se o usuário foi encontrado e a senha corresponde
        if resultado and resultado[0] == senha:
            nome_completo_usuario = resultado[1]
            abas_permitidas = resultado[2].split(",")  # Obtém as abas permitidas, separando-as por vírgulas
            messagebox.showinfo("Login sucedido", f"Bem vindo, {nome_completo_usuario.title()}!")
            root_login.destroy()  # Fecha a tela de login
            janela_principal()  # Abre a tela principal
        else:
            notification_manager.show_notification("Usuário ou senha inválidos!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")

    except sqlite3.Error as e:
        print(f"Erro na conexão com o banco de dados: {e}")
        messagebox.showerror("Erro de conexão", f"Não foi possível conectar ao banco de dados: {e}")

# Função para abrir a tela de alteração de senha
def janela_alterar_senha():
    from .ui_tela_principal import CustomEntry
    def valida_nova_senha(nova_senha, senha_atual_banco):
        notification_manager = NotificationManager(janela_alterar)

        if nova_senha == senha_atual_banco:
            notification_manager.show_notification("A nova senha não pode ser igual à senha atual!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return False        
        elif len(nova_senha) < 4:
            notification_manager.show_notification("A nova senha deve ter no mínimo 4 caracteres!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return False
        elif len(nova_senha) > 10:
            notification_manager.show_notification("A nova senha deve ter no máximo 10 caracteres!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return False
        return True

    def alterar_senha():
        notification_manager = NotificationManager(janela_alterar)
        usuario = entry_usuario_alt.get().strip().lower()
        senha_atual = entry_senha_atual.get()
        nova_senha = entry_nova_senha.get()
        
        dados_obrigatorios = [
            (usuario, "Usuário"),
            (senha_atual, "Senha atual"),
            (nova_senha, "Nova senha")
        ]

        # Verificar campos vazios
        campos_vazios = [nome for valor, nome in dados_obrigatorios if not valor]

        if campos_vazios:
            notification_manager.show_notification("Preencha os campos em branco!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return

        try:
            # Conectar ao banco de dados
            conn = sqlite3.connect(r'app\bd\login.db')
            cursor = conn.cursor()

            # Verificar se a senha atual está correta
            cursor.execute("SELECT senha FROM dados_login WHERE LOWER(nome_usuario) = ?", (usuario,))
            resultado = cursor.fetchone()

            # Se a senha atual estiver correta, atualize para a nova senha
            if resultado and resultado[0] == senha_atual:
                if not valida_nova_senha(nova_senha, resultado[0]):
                    return
                
                cursor.execute("UPDATE dados_login SET senha = ? WHERE LOWER(nome_usuario) = ?", (nova_senha, usuario))
                conn.commit()

                messagebox.showinfo("Senha Alterada", "Sua senha foi alterada com sucesso!")
                janela_alterar.destroy()  # Fecha a tela de alteração de senha
                janela_login()
            else:
                notification_manager.show_notification("Senha atual inválida ou usuário não encontrado!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
                return

            # Fechar a conexão com o banco de dados
            conn.close()

        except sqlite3.Error as e:
            print(f"Erro ao alterar a senha: {e}")
            messagebox.showerror("Erro", f"Não foi possível alterar a senha: {e}")

    def voltar_para_login():
        janela_alterar.destroy()
        janela_login()

    root_login.destroy()
    # Tela para alteração de senha
    janela_alterar = ctk.CTk()
    janela_alterar.title("Alterar Senha")
    janela_alterar.geometry("400x370")
    ctk.set_default_color_theme("green")

    frame = ctk.CTkFrame(master=janela_alterar)
    frame.pack(fill="both", expand=True, padx=5, pady=5)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_columnconfigure(2, weight=1)

    # Criação dos campos para usuário e senha
    label_usuario_alt = ctk.CTkLabel(master=frame, text="Usuário:", anchor="w")
    label_usuario_alt.grid(row=0, column=1, sticky="w", pady=(5, 0))

    entry_usuario_alt = CustomEntry(master=frame, placeholder_text="Insira o usuário")
    entry_usuario_alt.grid(row=1, column=1, sticky="ew")

    label_senha_atual = ctk.CTkLabel(master=frame, text="Senha Atual:", anchor="w")
    label_senha_atual.grid(row=2, column=1, sticky="w", pady=(10, 0))

    entry_senha_atual = CustomEntry(master=frame, show="*", placeholder_text="Insira a senha atual")
    entry_senha_atual.grid(row=3, column=1, sticky="ew")

    label_nova_senha = ctk.CTkLabel(master=frame, text="Nova Senha:", anchor="w")
    label_nova_senha.grid(row=4, column=1, sticky="w", pady=(10, 0))

    entry_nova_senha = CustomEntry(master=frame, show="*", placeholder_text="Insira a nova senha")
    entry_nova_senha.grid(row=5, column=1, sticky="ew")

    # Botão para alterar a senha
    botao_alterar_senha = ctk.CTkButton(master=frame, text="Alterar Senha", command=alterar_senha)
    botao_alterar_senha.grid(row=6, column=1, sticky="ew", pady=(15, 0))

    # Botão para voltar para a tela de login
    botao_voltar = ctk.CTkButton(master=frame, text="Voltar", fg_color="#B31312", hover_color="Dark red", command=voltar_para_login)
    botao_voltar.grid(row=7, column=1, sticky="ew", pady=(10, 5))

    janela_alterar.mainloop()

# Função de login
def janela_login():
    from .ui_tela_principal import CustomEntry
    global root_login, entry_usuario, entry_senha
    
    # Configuração da interface gráfica principal, com título e tamanho da janela
    root_login = ctk.CTk()
    root_login.title("Login")
    root_login.geometry("300x350")
    ctk.set_default_color_theme("green")

    # Cria um rótulo (label) para o campo de entrada do nome de usuário
    label_usuario = ctk.CTkLabel(master=root_login, text="Usuário:", anchor="w")
    label_usuario.pack(pady=(10,0), padx=80, fill="x")

    # Cria um campo de entrada (Entry) para o usuário digitar seu nome de usuário
    entry_usuario = CustomEntry(master=root_login, placeholder_text="Insira o usuário")
    entry_usuario.pack(pady=(0,15))

    # Cria um rótulo (label) para o campo de entrada da senha
    label_senha = ctk.CTkLabel(master=root_login, text="Senha:", anchor="w")
    label_senha.pack(pady=0, padx=80, fill="x")

    # Cria um campo de entrada (Entry) para o usuário digitar sua senha
    entry_senha = CustomEntry(master=root_login, show='*', placeholder_text="Insira a senha")
    entry_senha.pack(pady=(0,20))

    # Botão de login
    botao_login = ctk.CTkButton(master=root_login, text="Login", command=validacao_login)
    botao_login.pack(pady=(0,15))
    
    # Botão para sair
    botao_sair = ctk.CTkButton(master=root_login,
                                         text="Sair",
                                         fg_color="#B31312",
                                         hover_color="Dark red",
                                         text_color=("black", "white"),
                                         command=root_login.destroy)
    
    botao_sair.pack(pady=(0,15))

    # Botão para alterar senha
    botao_alterar_senha = ctk.CTkButton(master=root_login,
                                         text="Alterar Senha",
                                         command=janela_alterar_senha)  # Chama a janela para alterar a senha
    botao_alterar_senha.pack(pady=(0,15))

    root_login.mainloop()
