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
except ImportError:
    try:
        from app.utils import IconManager
        from app.bd.utils_bd import acessa_bd_contratos
        from app.ui_aba_pagamento import AbaPagamento
        from app.ui_aba_email import AbaEmail
        from app.ui_aba_aquisicao import AbaAquisicao
        from app.ui_aba_dados_pagamentos import AbaDadosPagamentos
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from utils import IconManager
        from bd.utils_bd import acessa_bd_contratos
        from ui_aba_pagamento import AbaPagamento
        from ui_aba_email import AbaEmail
        from ui_aba_aquisicao import AbaAquisicao
        from ui_aba_dados_pagamentos import AbaDadosPagamentos


locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')

def on_return_press(event):
    # Verifica qual aba está selecionada
    aba_atual = tabview.get()  # Retorna o nome da aba selecionada
    print(f"Aba atual: {aba_atual}")

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
    global aba_dados_pagamento, aba_dados_email, aba_dados_aquisicao

    # Configuração da interface gráfica
    root = ctk.CTk()
    root.title("Gerador de Requisições")
    root.geometry("680x600")
    root.minsize(680, 600)
    ctk.set_default_color_theme("green")

    icon_manager = IconManager()
    icon_manager.set_window_icon(root)

    ''' CRIAÇÃO DAS ABAS PARA SELEÇAO DOS TIPOS DE MODELOS DE TEXTO '''
    tabview = ctk.CTkTabview(master=root)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)

    # Criação das abas dinamicamente com base nas permissões
    for aba in abas_permitidas:
        tabview.add(aba)  # Adiciona uma aba para cada item em abas_permitidas

    # Define a aba que estará visível por padrão
    if abas_permitidas:
        tabview.set(abas_permitidas[0])  # Define a primeira aba como a aba ativa (opcional)

    print("Abas permitidas:", abas_permitidas)

    root.bind("<Return>", on_return_press)

    # pegar todos os contratos do banco de dados
    contratos = acessa_bd_contratos()

    if "PAGAMENTO" in abas_permitidas:
        # -------------------------------
        # Aba "PAGAMENTO"
        # -------------------------------
        frame_tab1 = ctk.CTkScrollableFrame(master=tabview.tab("PAGAMENTO"))
        frame_tab1.pack(fill="both", expand=True, padx=2, pady=2)

        global aba_dados_pagamento
        aba_dados_pagamento = AbaPagamento(
            master=frame_tab1,
            tabview=tabview,
            nome_completo_usuario=nome_completo_usuario,
            contratos=contratos,
            tela_para_notifcacao=root,
        )

    if "E-MAIL" in abas_permitidas:
        # -------------------------------
        # Aba "E-MAIL"
        # -------------------------------
        frame_tab2 = ctk.CTkScrollableFrame(master=tabview.tab("E-MAIL"))
        frame_tab2.pack(fill="both", expand=True, padx=2, pady=2)

        global aba_dados_email
        aba_dados_email = AbaEmail(
            master=frame_tab2,
            tabview=tabview,
            nome_completo_usuario=nome_completo_usuario,
        )

    if "AQUISIÇÃO" in abas_permitidas:
        # -------------------------------
        # Aba "AQUISIÇÃO"
        # -------------------------------
        frame_tab3 = ctk.CTkScrollableFrame(master=tabview.tab("AQUISIÇÃO"))
        frame_tab3.pack(fill="both", expand=True, padx=2, pady=2)

        global aba_dados_aquisicao
        aba_dados_aquisicao = AbaAquisicao(
            master=frame_tab3,
            tabview=tabview,
            nome_completo_usuario=nome_completo_usuario,
            contratos=contratos,
        )

    if "DADOS PAGAMENTOS" in abas_permitidas:
        # -------------------------------
        # Aba "DADOS PAGAMENTOS"
        # -------------------------------
        frame_tab4 = ctk.CTkScrollableFrame(master=tabview.tab("DADOS PAGAMENTOS"))
        frame_tab4.pack(fill="both", expand=True, padx=2, pady=2)

        aba_dados_pagamentos = AbaDadosPagamentos(
            master=frame_tab4,
            nome_completo_usuario=nome_completo_usuario,
            root=root
        )

    root.mainloop()


if __name__ == "__main__":
    nome_completo_usuario = "User_teste"
    abas_permitidas = ['PAGAMENTO', 'E-MAIL', 'AQUISIÇÃO', 'DADOS PAGAMENTOS']
    janela_principal(nome_completo_usuario, abas_permitidas)
