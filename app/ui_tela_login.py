"""
Módulo responsável pela autenticação de usuários no sistema.

Inclui funções para:
- Tela de login com validação de credenciais;
- Alteração de senha;
- Interface gráfica com CustomTkinter;
- Integração com banco de dados SQLite para verificação de dados de login.
"""

import sqlite3
from tkinter import messagebox
from typing import Optional

import customtkinter as ctk

try:
    from .CTkFloatingNotifications import NotificationManager, NotifyType
    from .version_checker import get_version
    from .bd.utils_bd import DatabaseManager
    from .componentes import CustomEntry
    from .utils import handle_error, IconManager
except ImportError:
    from CTkFloatingNotifications import NotificationManager, NotifyType
    from version_checker import get_version
    from bd.utils_bd import DatabaseManager
    from componentes import CustomEntry
    from utils import handle_error, IconManager

class LoginManager:
    """
    Classe responsável pela gestão do login do usuário.
    
    Inclui métodos para validação de login e alteração de senha.
    """
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.root_login = None
        self.janela_alterar = None
        self.notificacao = NotificationManager(master=None)
        self.icon_manager = IconManager()

    def validacao_login(self, root_login: ctk.CTk, entry_usuario: CustomEntry, entry_senha: CustomEntry):
        """
        Valida os dados de login inseridos pelo usuário.

        Verifica se o nome de usuário e a senha correspondem aos registros do banco de dados.
        Em caso de sucesso, fecha a janela de login e abre a tela principal.
        Caso contrário, exibe uma notificação de erro.
        
        Args:
            root_login (ctk.CTk): Janela principal da tela de login.
            entry_usuario (CustomEntry): Campo de entrada do nome de usuário.
            entry_senha (CustomEntry): Campo de entrada da senha.
        """
        from .ui_tela_principal import janela_principal

        usuario = entry_usuario.get().strip().lower()
        senha = entry_senha.get()

        try:
            resultado = self.db_manager.validar_credenciais(usuario, senha)

            if resultado:
                nome_completo_usuario = resultado[0]
                abas_permitidas = resultado[1].split(",")
                messagebox.showinfo("Login sucedido", f"Bem vindo, {nome_completo_usuario.title()}!")
                root_login.destroy()
                janela_principal(nome_completo_usuario, abas_permitidas)
            else:
                self.notificacao.show_notification(
                    "Usuário ou senha inválidos!",
                    NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
                )

        except sqlite3.Error as erro_conexao:
            mensagem_erro = (
                f"Não foi possível conectar ao banco de dados: {erro_conexao}\n\n"
                "Certifique-se de que o Drive está conectado e de que há conexão com a internet."
            )
            handle_error("Erro de conexão", mensagem_erro, self.root_login)
                
    def _validar_nova_senha(self, nova_senha: str, senha_atual_banco: str) -> bool:
        """
        Valida os critérios da nova senha.

        Args:
            nova_senha (str): Nova senha a ser validada.
            senha_atual_banco (str): Senha atual do banco de dados.
            
        Returns:
            bool: True se a senha é válida, False caso contrário.
        """
        if nova_senha == senha_atual_banco:
            self.notificacao.show_notification(
                "A nova senha não pode ser igual à senha atual!",
                NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return False

        if len(nova_senha) < 4:
            self.notificacao.show_notification(
                "A nova senha deve ter no mínimo 4 caracteres!",
                NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return False

        if len(nova_senha) > 10:
            self.notificacao.show_notification(
                "A nova senha deve ter no máximo 10 caracteres!", 
                NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return False

        return True

    def _alterar_senha (self, entry_usuario_alt: CustomEntry, entry_senha_atual: CustomEntry,
                        entry_nova_senha: CustomEntry):
        """
        Processa a alteração de senha do usuário.

        Args:
            entry_usuario_alt (CustomEntry): Campo de entrada do nome de usuário.
            entry_senha_atual (CustomEntry): Campo de entrada da senha atual.
            entry_nova_senha (CustomEntry): Campo de entrada da nova senha.
        """
        usuario = entry_usuario_alt.get().strip()
        senha_atual = entry_nova_senha.get()
        nova_senha = entry_nova_senha.get()

        # Verificar campos vazios
        campos_obrigatorios = [
            (usuario, "Usuário"),
            (senha_atual, "Senha atual"),
            (nova_senha, "Nova senha")
        ]

        campos_vazios = [nome for valor, nome in campos_obrigatorios if not valor]

        if campos_vazios:
            self.notificacao.show_notification(
                "Preencha os campos em branco!",
                NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
            )
            return

        try:
            # Verificar se a senha atual está correta
            senha_atual_banco = self.db_manager.verificar_senha_atual(usuario)

            if not senha_atual_banco or senha_atual_banco != senha_atual:
                self.notificacao.show_notification(
                    "Senha atual inválida ou usuário não encontrado!",
                    NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
                )
                return

            if not self._validar_nova_senha(nova_senha, senha_atual_banco):
                return

            # Alterar a senha no banco de dados
            if self.db_manager.alterar_senha(usuario, nova_senha):
                self.notificacao.show_notification(
                    "Sua senha foi alterada com sucesso!",
                    NotifyType.SUCCESS, bg_color="#404040", text_color="#FFFFFF"
                )
                self.janela_alterar.destroy()
                self.criar_janela_login()
            else:
                self.notificacao.show_notification(
                    "Erro ao alterar a senha!",
                    NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
                )

        except sqlite3.Error as e_altera_senha:
            handle_error(
                e_altera_senha,
                f"Erro ao alterar a senha: {e_altera_senha}",
                "Não foi possível alterar a senha no banco de dados."
            )

    def _voltar_para_login():
        """Volta para a tela de login principal."""
        if self.janela_alterar:
            self.janela_alterar.destroy()
        
        self.criar_janela_login()
    
    def _set_window_icon(self, window):
            """Define o ícone da janela usando o primeiro caminho válido encontrado."""
            for path in self.icon_path:
                if exists(path):
                    try:
                        window.iconbitmap(path)
                        return  # Se conseguiu definir o ícone, encerra a função
                    except Exception as e:
                        print(f"Erro ao carregar o ícone de {path}: {e}")
                        continue  # Tenta o próximo caminho se houver erro
            
            print("Não foi possível carregar o ícone de nenhum dos caminhos disponíveis")

    def criar_janela_alterar_senha(self):
        """
        Cria e exibe a janela de alteração de senha para o usuário.

        Permite que o usuário insira seu nome de usuário, senha atual e uma nova senha.
        A função valida a senha atual com o banco de dados, verifica se a nova senha 
        atende aos critérios de segurança e, caso tudo esteja correto, atualiza a senha 
        no banco de dados.
        """
        if self.root_login:
            self.root_login.destroy()

        # Criar janela de alteração de senha
        self.janela_alterar = ctk.CTk()
        self.janela_alterar.title("Gerador de Requisições - Alterar Senha")
        self.janela_alterar.geometry("380x450")
        self.janela_alterar.resizable(False, False)
        ctk.set_default_color_theme("green")
        
        self.icon_manager.set_window_icon(self.janela_alterar)
        
        frame = ctk.CTkFrame(master=self.janela_alterar)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        titulo = ctk.CTkLabel(
            master=frame, 
            text="PDFMaster", 
            font=("Segoe UI", 32, "bold")
        )
        titulo.grid(row=0, column=1, pady=(15, 0), padx=20)

        subtitulo = ctk.CTkLabel(
            master=frame, 
            text="Alterar senha", 
            font=("Segoe UI", 16, "bold")
        )
        subtitulo.grid(row=1, column=1, pady=(0, 0), padx=20)

        # Criação dos campos para usuário e senha
        label_usuario_alt = ctk.CTkLabel(master=frame, text="Usuário:", anchor="w")
        label_usuario_alt.grid(row=2, column=1, sticky="w", pady=(15, 0))

        entry_usuario_alt = CustomEntry(master=frame, placeholder_text="Insira o usuário")
        entry_usuario_alt.grid(row=3, column=1, sticky="ew")

        label_senha_atual = ctk.CTkLabel(master=frame, text="Senha Atual:", anchor="w")
        label_senha_atual.grid(row=4, column=1, sticky="w", pady=(10, 0))

        entry_senha_atual = CustomEntry(master=frame, show="*", placeholder_text="Insira a senha atual")
        entry_senha_atual.grid(row=5, column=1, sticky="ew")

        label_nova_senha = ctk.CTkLabel(master=frame, text="Nova Senha:", anchor="w")
        label_nova_senha.grid(row=6, column=1, sticky="w", pady=(10, 0))

        entry_nova_senha = CustomEntry(master=frame, show="*", placeholder_text="Insira a nova senha")
        entry_nova_senha.grid(row=7, column=1, sticky="ew")

        # Botão para alterar a senha
        botao_alterar_senha = ctk.CTkButton(
            master=frame, 
            text="Alterar Senha", 
            command=lambda: self._alterar_senha(entry_usuario_alt, entry_senha_atual, entry_nova_senha)
        )
        botao_alterar_senha.grid(row=8, column=1, sticky="ew", pady=(15, 0))

        self.janela_alterar.bind("<Return>", lambda enter: botao_alterar_senha.invoke())

        # Botão para voltar para a tela de login
        botao_voltar = ctk.CTkButton(
            master=frame,
            text="Voltar",
            fg_color="#B31312",
            hover_color="Dark red",
            command=self._voltar_para_login
        )
        botao_voltar.grid(row=9, column=1, sticky="ew", pady=(10, 5))

        self.janela_alterar.mainloop()

    def criar_janela_login(self):
        """
        Cria e exibe a interface gráfica de login do sistema.
        
        Permite que o usuário insira seu nome de usuário e senha,
        faça login, altere sua senha ou encerre o programa.
        
        Returns:
            tuple: Tupla contendo (root_login, entry_usuario, entry_senha)
        """
        self.root_login = ctk.CTk()
        self.root_login.title("Gerador de Requisições - Login")
        self.root_login.geometry("340x430")
        self.root_login.resizable(False, False)
        ctk.set_default_color_theme("green")

        self.icon_manager.set_window_icon(self.root_login)

        # Título da janela
        titulo = ctk.CTkLabel(
            master=self.root_login,
            text="Gerador de\nRequisições",
            font=("Segoe UI", 32, "bold"
            ))
        titulo.pack(pady=(15, 0))

        # Cria um rótulo (label) para o campo de entrada do nome de usuário
        label_usuario = ctk.CTkLabel(master=self.root_login, text="Usuário:", anchor="w")
        label_usuario.pack(pady=(15,0), padx=100, fill="x")

        # Cria um campo de entrada (Entry) para o usuário digitar seu nome de usuário
        entry_usuario = CustomEntry(master=self.root_login, placeholder_text="Insira o usuário")
        entry_usuario.pack(pady=(0,15))

        # Cria um rótulo (label) para o campo de entrada da senha
        label_senha = ctk.CTkLabel(master=self.root_login, text="Senha:", anchor="w")
        label_senha.pack(pady=0, padx=100, fill="x")

        # Cria um campo de entrada (Entry) para o usuário digitar sua senha
        entry_senha = CustomEntry(master=self.root_login, show='*', placeholder_text="Insira a senha")
        entry_senha.pack(pady=(0,20))

        # Botão de login
        botao_login = ctk.CTkButton(
            master=self.root_login,
            text="Login",
            command=lambda: self.validacao_login(self.root_login, entry_usuario, entry_senha)
        )
        botao_login.pack(pady=(0,15))

        # Botão para sair
        botao_sair = ctk.CTkButton(
            master=self.root_login, 
            text="Sair", 
            fg_color="#B31312",
            hover_color="Dark red", 
            command=self.root_login.destroy
        )
        botao_sair.pack(pady=(0,15))

        # Botão para alterar senha
        botao_alterar_senha = ctk.CTkButton(
            master=self.root_login,
            text="Alterar Senha",
            command=self.criar_janela_alterar_senha
        )
        botao_alterar_senha.pack(pady=(0,13))

        self.root_login.bind("<Return>", lambda enter: botao_login.invoke())

        versao_atual = get_version()
        label_versao = ctk.CTkLabel(
            master=self.root_login,
            text=f"Versão {versao_atual}",
            font=("Segoe UI", 9),
            text_color="#888888",
        )
        label_versao.pack(side="bottom", pady=0)

        self.root_login.mainloop()

        return self.root_login, entry_usuario, entry_senha


# Função de conveniência para manter compatibilidade
def janela_login():
    """Função de conveniência para criar a janela de login."""
    login_manager = LoginManager()
    return login_manager.criar_janela_login()


if __name__ == "__main__":
    janela_login()
