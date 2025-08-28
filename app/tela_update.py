import customtkinter as ctk
import sys
import webbrowser
from .utils import IconManager

class TelaUpdate:
    """Janela de diálogo para atualização obrigatória."""
    
    def __init__(self, current_version, latest_version, download_url):
        """
        Inicializa a janela de diálogo de atualização.
        
        Args:
            current_version (str): Versão atual do aplicativo
            latest_version (str): Versão mais recente disponível
            download_url (str): URL para download da nova versão
        """
        self.current_version = current_version
        self.latest_version = latest_version
        self.download_url = download_url
        self.icone = IconManager()
        
        # Configurar janela
        self.root = ctk.CTk()
        self.root.title("Gerador de Requisições - Atualização Necessária")
        self.root.geometry("430x420")
        self.root.resizable(False, False)
        self.icone.set_window_icon(self.root)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura a interface de usuário."""
        # Frame principal
        frame = ctk.CTkFrame(master=self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        titulo = ctk.CTkLabel(
            master=frame, 
            text="Atualização Obrigatória", 
            font=("Segoe UI", 24, "bold"),
            text_color="#FF6B35"  # Usando a cor de alerta do sistema
        )
        titulo.pack(pady=(20, 5))
        
        # Ícone ou separador
        separador = ctk.CTkFrame(master=frame, height=2, width=320)
        separador.pack(pady=(0, 15))
        
        # Mensagem
        mensagem = ctk.CTkLabel(
            master=frame,
            text="Uma nova versão do Gerador de Requisições está disponível.\nVocê precisa atualizar para continuar usando o aplicativo.",
            font=("Segoe UI", 14),
            justify="center"
        )
        mensagem.pack(pady=(0, 15))
        
        # Frame para informações de versão
        info_frame = ctk.CTkFrame(master=frame)
        info_frame.pack(pady=(0, 20), padx=20, fill="x")
        
        # Versão atual
        versao_atual_label = ctk.CTkLabel(
            master=info_frame,
            text=f"Sua versão:",
            font=("Segoe UI", 12),
            anchor="w"
        )
        versao_atual_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        versao_atual = ctk.CTkLabel(
            master=info_frame,
            text=self.current_version,
            font=("Segoe UI", 14, "bold"),
            text_color="#B31312"  # Vermelho para versão desatualizada
        )
        versao_atual.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Versão nova
        versao_nova_label = ctk.CTkLabel(
            master=info_frame,
            text=f"Nova versão:",
            font=("Segoe UI", 12),
            anchor="w"
        )
        versao_nova_label.pack(anchor="w", padx=10, pady=(0, 0))
        
        versao_nova = ctk.CTkLabel(
            master=info_frame,
            text=self.latest_version,
            font=("Segoe UI", 14, "bold"),
            text_color="#4CAF50"  # Verde para nova versão
        )
        versao_nova.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Botões
        botoes_frame = ctk.CTkFrame(master=frame, fg_color="transparent")
        botoes_frame.pack(fill="x", pady=(10, 0))
        
        # Botão para baixar
        botao_baixar = ctk.CTkButton(
            master=botoes_frame,
            text="Baixar Nova Versão",
            font=("Segoe UI", 14),
            command=self._download
        )
        botao_baixar.pack(pady=(0, 10), padx=20, fill="x")
        
        # Botão para sair
        botao_sair = ctk.CTkButton(
            master=botoes_frame,
            text="Sair",
            font=("Segoe UI", 14),
            fg_color="#B31312",
            hover_color="Dark red",
            command=self._exit
        )
        botao_sair.pack(pady=(0, 10), padx=20, fill="x")
        
    def _download(self):
        """Abre o navegador com a URL de download e fecha o aplicativo."""
        webbrowser.open(self.download_url)
        self._exit()
        
    def _exit(self):
        """Fecha o aplicativo."""
        self.root.destroy()
        sys.exit(0)
        
    def _on_close(self):
        """Trata o fechamento da janela pelo X como uma escolha de sair."""
        # Quando o usuário clica no X, fechamos o aplicativo
        self._exit()
        
    def show(self):
        """Exibe a janela de atualização e bloqueia até uma escolha ser feita."""
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.focus_force()
        self.root.mainloop()