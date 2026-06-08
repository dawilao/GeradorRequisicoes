import sqlite3
import traceback
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import re
from datetime import datetime
import locale

try:
    from .utils import IconManager
    from .bd.utils_bd import acessa_bd_contratos
    from .ui_aba_pagamento import AbaPagamento
    from .ui_aba_email import AbaEmail
    from .ui_aba_aquisicao import AbaAquisicao
    from .ui_aba_dados_pagamentos import AbaDadosPagamentos
    from .ui_aba_controle_entregas import AbaPrazoEntregas
    from .version_checker import get_version
except ImportError:
    from utils import IconManager
    from bd.utils_bd import acessa_bd_contratos
    from ui_aba_pagamento import AbaPagamento
    from ui_aba_email import AbaEmail
    from ui_aba_aquisicao import AbaAquisicao
    from ui_aba_dados_pagamentos import AbaDadosPagamentos
    from ui_aba_controle_entregas import AbaPrazoEntregas
    from version_checker import get_version


locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')


def _mostrar_erro_aba(frame: ctk.CTkFrame, nome_aba: str, erro: Exception):
    """Renderiza uma mensagem de erro dentro do frame da aba que falhou ao carregar."""
    tb = traceback.format_exc()

    container = ctk.CTkFrame(frame, fg_color="transparent")
    container.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(
        container,
        text=f"Não foi possível carregar a aba '{nome_aba}'",
        font=("Segoe UI", 14, "bold"),
        text_color="#E05252",
    ).pack(pady=(0, 6))

    mensagem = str(erro)
    if isinstance(erro, sqlite3.DatabaseError):
        mensagem = (
            "O banco de dados está corrompido (database disk image is malformed).\n"
            "Execute o script recuperar_banco.py para tentar recuperar os dados."
        )

    ctk.CTkLabel(
        container,
        text=mensagem,
        font=("Segoe UI", 11),
        wraplength=500,
        justify="center",
    ).pack(pady=(0, 12))

    detalhes_visivel = tk.BooleanVar(value=False)
    caixa_detalhes = ctk.CTkTextbox(container, width=520, height=160, state="disabled")

    def _toggle_detalhes():
        if detalhes_visivel.get():
            caixa_detalhes.pack_forget()
            detalhes_visivel.set(False)
            btn_detalhes.configure(text="Ver detalhes do erro")
        else:
            caixa_detalhes.configure(state="normal")
            caixa_detalhes.delete("1.0", "end")
            caixa_detalhes.insert("end", tb)
            caixa_detalhes.configure(state="disabled")
            caixa_detalhes.pack(pady=(0, 8))
            detalhes_visivel.set(True)
            btn_detalhes.configure(text="Ocultar detalhes")

    btn_detalhes = ctk.CTkButton(
        container,
        text="Ver detalhes do erro",
        command=_toggle_detalhes,
        width=180,
        fg_color="transparent",
        border_width=1,
        text_color=("gray30", "gray70"),
        border_color=("gray60", "gray40"),
    )
    btn_detalhes.pack()

# Inicializar variáveis globais para evitar NameError em on_return_press
aba_dados_pagamento = None
aba_dados_email = None
aba_dados_aquisicao = None
tabview = None

def on_return_press(event):
    aba_atual = tabview.get()

    if aba_atual == "PAGAMENTO":
        if aba_dados_pagamento:
            aba_dados_pagamento._gerar_solicitacao()
    elif aba_atual == "E-MAIL":
        if aba_dados_email:
            aba_dados_email.gerar_texto_email()
    elif aba_atual == "AQUISIÇÃO":
        if aba_dados_aquisicao:
            aba_dados_aquisicao.gerar_texto_aquisicao()

def janela_principal(nome_completo_usuario, abas_permitidas):
    global aba_dados_pagamento, aba_dados_email, aba_dados_aquisicao, tabview

    # Configuração da interface gráfica
    root = ctk.CTk()
    root.title("Gerador de Requisições")
    root.geometry("680x620")
    root.minsize(680, 620)
    ctk.set_default_color_theme("green")

    icon_manager = IconManager()
    icon_manager.set_window_icon(root)

    ''' CRIAÇÃO DAS ABAS PARA SELEÇAO DOS TIPOS DE MODELOS DE TEXTO '''
    tabview = ctk.CTkTabview(master=root)
    tabview.pack(fill="both", expand=True, padx=10, pady=(10, 0))

    # Criação das abas dinamicamente com base nas permissões
    for aba in abas_permitidas:
        tabview.add(aba)  # Adiciona uma aba para cada item em abas_permitidas

    # Define a aba que estará visível por padrão
    if abas_permitidas:
        tabview.set(abas_permitidas[0])

    root.bind("<Return>", on_return_press)

    # pegar todos os contratos do banco de dados
    contratos = acessa_bd_contratos()

    if "PAGAMENTO" in abas_permitidas:
        # -------------------------------
        # Aba "PAGAMENTO"
        # -------------------------------
        frame_tab1 = ctk.CTkScrollableFrame(master=tabview.tab("PAGAMENTO"))
        frame_tab1.pack(fill="both", expand=True, padx=2, pady=2)
        try:
            global aba_dados_pagamento
            aba_dados_pagamento = AbaPagamento(
                master=frame_tab1,
                tabview=tabview,
                nome_completo_usuario=nome_completo_usuario,
                contratos=contratos,
                tela_para_notifcacao=root,
            )
        except Exception as e:
            _mostrar_erro_aba(frame_tab1, "PAGAMENTO", e)

    if "E-MAIL" in abas_permitidas:
        # -------------------------------
        # Aba "E-MAIL"
        # -------------------------------
        frame_tab2 = ctk.CTkScrollableFrame(master=tabview.tab("E-MAIL"))
        frame_tab2.pack(fill="both", expand=True, padx=2, pady=2)
        try:
            global aba_dados_email
            aba_dados_email = AbaEmail(
                master=frame_tab2,
                tabview=tabview,
                nome_completo_usuario=nome_completo_usuario,
            )
        except Exception as e:
            _mostrar_erro_aba(frame_tab2, "E-MAIL", e)

    if "AQUISIÇÃO" in abas_permitidas:
        # -------------------------------
        # Aba "AQUISIÇÃO"
        # -------------------------------
        frame_tab3 = ctk.CTkScrollableFrame(master=tabview.tab("AQUISIÇÃO"))
        frame_tab3.pack(fill="both", expand=True, padx=2, pady=2)
        try:
            global aba_dados_aquisicao
            aba_dados_aquisicao = AbaAquisicao(
                master=frame_tab3,
                tabview=tabview,
                nome_completo_usuario=nome_completo_usuario,
                contratos=contratos,
            )
        except Exception as e:
            _mostrar_erro_aba(frame_tab3, "AQUISIÇÃO", e)

    if "DADOS PAGAMENTOS" in abas_permitidas:
        # -------------------------------
        # Aba "DADOS PAGAMENTOS"
        # -------------------------------
        frame_tab4 = ctk.CTkScrollableFrame(master=tabview.tab("DADOS PAGAMENTOS"))
        frame_tab4.pack(fill="both", expand=True, padx=2, pady=2)
        try:
            aba_dados_pagamentos = AbaDadosPagamentos(master=frame_tab4, root=root)
        except Exception as e:
            _mostrar_erro_aba(frame_tab4, "DADOS PAGAMENTOS", e)

    if "CONTROLE ENTREGAS" in abas_permitidas:
        # -------------------------------
        # Aba "CONTROLE ENTREGAS"
        # -------------------------------
        # Usar frame normal (não scrollable) pois a aba já tem scroll interno
        frame_tab5 = ctk.CTkFrame(master=tabview.tab("CONTROLE ENTREGAS"), fg_color="transparent")
        frame_tab5.pack(fill="both", expand=True, padx=0, pady=0)
        try:
            aba_prazo_entregas = AbaPrazoEntregas(
                master=frame_tab5,
                tabview=tabview,
                nome_completo_usuario=nome_completo_usuario,
                contratos=contratos,
                tela_para_notifcacao=root,
            )
        except Exception as e:
            _mostrar_erro_aba(frame_tab5, "CONTROLE ENTREGAS", e)

    # Adiciona o label de versão na parte inferior da janela principal
    versao_atual = get_version()
    label_versao = ctk.CTkLabel(
        master=root,
        text=f"Versão {versao_atual}",
        font=("Segoe UI", 9),
        text_color="#888888",
    )
    label_versao.pack(side="bottom", pady=0)    

    root.mainloop()


if __name__ == "__main__":
    nome_completo_usuario = "User_teste"
    abas_permitidas = ['PAGAMENTO', 'E-MAIL', 'AQUISIÇÃO', 'DADOS PAGAMENTOS', 'CONTROLE ENTREGAS']
    janela_principal(nome_completo_usuario, abas_permitidas)
