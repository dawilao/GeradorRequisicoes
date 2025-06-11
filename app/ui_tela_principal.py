import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import re
from datetime import datetime
import locale

from .utils import *
from .gerador_excel import gerar_excel, DadosRequisicao
from .bd.utils_bd import acessa_bd_contratos, acessa_bd_usuarios
from .CTkDatePicker import *
from .CTkFloatingNotifications import *
from .componentes import CustomEntry, CustomComboBox

locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')

def on_return_press(event):
    # Verifica qual aba está selecionada
    aba_atual = tabview.get()  # Retorna o nome da aba selecionada
    print(f"Aba atual: {aba_atual}")

    aba_atual = tabview.get()
    if aba_atual == "PAGAMENTO":
        gerar_button.invoke()
    elif aba_atual == "E-MAIL":
        if aba_dados_email:
            aba_dados_email.gerar_texto_email()
    elif aba_atual == "AQUISIÇÃO":
        if aba_dados_aquisicao:
            aba_dados_aquisicao.gerar_texto_aquisicao()
        gerar_button_tab3.invoke()

def limpar_dados():
    """
    Limpar widgets da aba ativa
    """
    
    aba_ativa  = tabview.get()
    
    if aba_ativa == "PAGAMENTO":
        if editando_item_pagamento is None:
            # Limpar os widgets da Tab 1
            for widget in widgets_para_limpar:
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, tk.END)
                elif isinstance(widget, ctk.CTkTextbox):
                    widget.delete("0.0", tk.END)
                elif isinstance(widget, ctk.CTkComboBox):
                    widget.set("")

                itens_pagamento.clear()
                atualizar_lista_itens_pagamento()
                add_campos()
        else:
            notification_manager = NotificationManager(root)  # passando a instância da janela principal
            notification_manager.show_notification("Item em edição!\nSalve-o para habilitar a limpeza dos campos.", NotifyType.WARNING, bg_color="#404040", text_color="#FFFFFF")
            pass 
    elif aba_ativa == "E-MAIL":
        # Limpar os widgets da Tab 2
        for widget in widgets_para_limpar_tab2:
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, tk.END)
            elif isinstance(widget, ctk.CTkTextbox):
                widget.delete("0.0", tk.END)
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set("")
    elif aba_ativa == "AQUISIÇÃO":
        if editando_item is None:
            # Limpar os widgets da Tab 3
            for widget in widgets_para_limpar_tab3:
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, tk.END)
                elif isinstance(widget, ctk.CTkTextbox):
                    widget.delete("0.0", tk.END)
                elif isinstance(widget, ctk.CTkComboBox):
                    widget.set("")
                elif isinstance(widget, CTkDatePicker):
                    widget.set("")

                servicos_tab3.clear()
                atualizar_lista_itens_tab3()
                add_campos_tab3()
        else:
            notification_manager = NotificationManager(root)  # passando a instância da janela principal
            notification_manager.show_notification("Item em edição!\nSalve-o para habilitar a limpeza dos campos.", NotifyType.WARNING, bg_color="#404040", text_color="#FFFFFF")
            pass

def janela_principal(nome_completo_usuario, abas_permitidas):
    global aba_dados_pagamento, aba_dados_email, aba_dados_aquisicao

    # Variáveis globais principais
    global root, tabview, frame, widgets_para_limpar, widgets_para_limpar_tab2, widgets_para_limpar_tab3
    global usuarios_varios_departamentos, usuarios_gerais, notification_manager

    # Widgets da aba PAGAMENTO
    global nome_usuario_entry, tipo_servico_combobox, nome_fornecedor_entry, prefixo_entry, agencia_entry
    global os_entry, contrato_combobox, motivo_entry, valor_entry, valor_label, tipo_pagamento_combobox, tecnicos_entry
    global saida_destino_entry, competencia_combobox, porcentagem_entry
    global tipo_aquisicao_combobox, tipo_chave_pix_combobox, chave_pix_entry
    global texto_solicitacao, switch_autocopia_var, contratos, switch_gerar_excel_var
    global tipo_chave_pix_label, chave_pix_label, opcao_os_parceiro_label, opcao_os_parceiro_combobox
    global competencia_label, porcentagem_label, motivo_label, saida_destino_label
    global tecnicos_label, prefixo_label, os_label, agencia_label, contrato_label
    global nome_benef_pix_label, nome_benef_pix_entry
    global tipo_aquisicao_label, gerar_button
    global descricao_utilidades_label, descricao_utilidades_entry
    global frame_caixa_itens_pagamento, frame_lista_itens_pagamento
    global descricao_do_item_pagamento_label, descricao_do_item_pagamento_entry
    global editando_item_pagamento, btn_adicionar_servico_pagamento
    global valor_caixa_itens_label, valor_caixa_itens_entry

    # Configuração da interface gráfica
    root = ctk.CTk()
    root.title("Gerador de Requisições")
    root.geometry("680x600")
    ctk.set_default_color_theme("green")
    notification_manager = NotificationManager(root)  # passando a instância da janela principal

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
        from .ui_aba_pagamento import AbaPagamento

        frame_tab1 = ctk.CTkScrollableFrame(master=tabview.tab("PAGAMENTO"))
        frame_tab1.pack(fill="both", expand=True, padx=2, pady=2)

        global aba_dados_pagamento
        aba_dados_pagamento = AbaPagamento(
            master=frame_tab1,
            tabview=tabview,
            nome_completo_usuario=nome_completo_usuario,
            contratos=contratos,
        )

    if "E-MAIL" in abas_permitidas:
        # -------------------------------
        # Aba "E-MAIL"
        # -------------------------------
        from .ui_aba_email import AbaEmail

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
        from .ui_aba_aquisicao import AbaAquisicao

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
        from app.ui_aba_dados_pagamentos import AbaDadosPagamentos

        frame_tab4 = ctk.CTkScrollableFrame(master=tabview.tab("DADOS PAGAMENTOS"))
        frame_tab4.pack(fill="both", expand=True, padx=2, pady=2)

        aba_dados_pagamentos = AbaDadosPagamentos(master=frame_tab4)

    root.mainloop()
