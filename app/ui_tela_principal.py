import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import pyperclip
import re
from os.path import splitext
from datetime import datetime
import locale

from .utils import *
from .gerador_excel import gerar_excel, DadosRequisicao
from .bd.utils_bd import acessa_bd_contratos, acessa_bd_usuarios
from .CTkDatePicker import *
from .CTkFloatingNotifications import *
from .componentes import CustomEntry, CustomComboBox

locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')

def identifica_preenchimento_pref_os_age(prefixo, agencia, os_num):
    notification_manager = NotificationManager(root)  # passando a instância da janela principal

    campos_preenchidos = {
        "PREFIXO": bool(prefixo),
        "AGÊNCIA": bool(agencia),
        "OS": bool(os_num),
    }

    faltantes = [campo for campo, preenchido in campos_preenchidos.items() if not preenchido]
    preenchidos = [campo for campo, preenchido in campos_preenchidos.items() if preenchido]

    def formatar_lista(lista):
        """Formata uma lista para usar 'e' antes do último item."""
        if len(lista) > 1:
            return f"{', '.join(lista[:-1])} e {lista[-1]}"
        return lista[0]

    if len(preenchidos) == 1:
        notification_manager.show_notification(
            f"Campo {preenchidos[0]} está preenchido\nPor favor, insira {formatar_lista(faltantes)}.",
            NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
        )
        return True
    elif len(preenchidos) == 2:
        notification_manager.show_notification(
            f"Os campos {formatar_lista(preenchidos)} estão preenchidos\nPor favor, insira {faltantes[0]}.",
            NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
        )
        return True

# -------------------------------
# Funções da aba "Pagamento"
# -------------------------------

itens_pagamento = []

def add_item_pagamento():
    global descricao_base

    if tipo_servico in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
        entrada = arrumar_texto(descricao_do_item_pagamento_entry.get().upper().strip())
        possui_os = opcao_os_parceiro_combobox.get()

        descricao_formatada, descricao_base, erro = validar_item_pagamento(entrada, tipo_servico, possui_os)

        if erro:
            notification_manager.show_notification(f"Campo DESCRIÇÃO DO ITEM\n{erro}", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return
        
        # Adiciona dicionário com dados completos
        item = {
            "descricao": descricao_formatada,
            "descricao_base": descricao_base
        }
    elif tipo_servico == "REEMBOLSO UBER":
        saida_e_destino = arrumar_texto(saida_destino_entry.get().upper().strip())
        motivo = arrumar_texto(motivo_entry.get().upper().strip())
        valor = verificar_se_numero(valor_caixa_itens_entry.get())

        # Verificações de campos obrigatórios
        if not motivo and not valor and not saida_e_destino:
            erro = "Campos DESCRIÇÃO DO ITEM, MOTIVO e SAÍDA/DESTINO não podem ser vazios!"
        elif not motivo and not saida_e_destino:
            erro = "Campos MOTIVO e SAÍDA/DESTINO não podem ser vazios!"
        elif not motivo and not valor:
            erro = "Campos DESCRIÇÃO DO ITEM e MOTIVO não podem ser vazios!"
        elif not saida_e_destino and not valor:
            erro = "Campos DESCRIÇÃO DO ITEM e SAÍDA/DESTINO não podem ser vazios!"
        elif not motivo:
            erro = "Campo MOTIVO não pode ser vazio!"
        elif not valor:
            erro = "Campo VALOR não pode ser vazio!"
        elif not saida_e_destino:
            erro = "Campo SAÍDA/DESTINO não pode ser vazio!"
        elif valor is ValueError:
            erro = "Campo VALOR\nPor favor, insira um número válido!"
        else:
            erro = None

        # Exibição de erro, se houver
        if erro:
            notification_manager.show_notification(
                erro, 
                NotifyType.ERROR,
                bg_color="#404040", 
                text_color="#FFFFFF"
            )
            return

        # Adiciona dicionário com dados completos
        item = {
            "saida_e_destino": saida_e_destino,
            "motivo": motivo,
            "valor": valor,
            "descricao": f"{saida_e_destino} - {motivo} - R$ {valor}"
        }
    else:
        motivo = arrumar_texto(motivo_entry.get().upper().strip())
        valor = verificar_se_numero(valor_caixa_itens_entry.get())

        # Verificações de campos obrigatórios
        if not motivo and not valor:
            erro = "Campos DESCRIÇÃO DO ITEM e MOTIVO não podem ser vazios!"
        elif not motivo:
            erro = "Campo MOTIVO não pode ser vazio!"
        elif not valor:
            erro = "Campo VALOR não pode ser vazio!"
        elif valor is ValueError:
            erro = "Campo VALOR\nPor favor, insira um número válido!"
        else:
            erro = None

        # Exibição de erro, se houver
        if erro:
            notification_manager.show_notification(
                erro, 
                NotifyType.ERROR,
                bg_color="#404040", 
                text_color="#FFFFFF"
            )
            return

        # Adiciona dicionário com dados completos
        item = {
            "motivo": motivo,
            "valor": valor,
            "descricao": f"{motivo} - R$ {valor}"
        }

    itens_pagamento.append(item)

    if tipo_servico in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
        descricao_do_item_pagamento_entry.delete(0, tk.END)
        descricao_do_item_pagamento_entry.focus()

    if tipo_servico not in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
        motivo_entry.delete(0, tk.END)
        valor_caixa_itens_entry.delete(0, tk.END)
            
        if tipo_servico == "REEMBOLSO UBER":
            saida_destino_entry.delete(0, tk.END)
            saida_destino_entry.focus()
        else:
            motivo_entry.focus()

    atualizar_lista_itens_pagamento()

def atualizar_lista_itens_pagamento():
    for widget in frame_lista_itens_pagamento.winfo_children():
        widget.destroy()

    if len(itens_pagamento) > 0:
        frame_lista_itens_pagamento.grid(row=11, column=0, columnspan=2, sticky="ew", padx=(10, 10), pady=(0, 10))
    else:
        frame_lista_itens_pagamento.grid_forget()

    for index, item in enumerate(itens_pagamento):
        row_frame_pagamento = ctk.CTkFrame(frame_lista_itens_pagamento, width=400)
        row_frame_pagamento.grid(row=index, column=0, columnspan=2, sticky="ew", padx=(10, 10), pady=5)

        label_itens_gerados_pagamento = ctk.CTkLabel(
            row_frame_pagamento,
            text=item["descricao"],
            anchor="w", justify="left", wraplength=340
        )
        label_itens_gerados_pagamento.grid(row=0, column=0, padx=2)

        btn_editar_item_pagamento = ctk.CTkButton(
            row_frame_pagamento, text="Editar", width=30, 
            command=lambda i=index: editar_item_pagamento(i)
        )
        btn_editar_item_pagamento.grid(row=0, column=1, padx=2)

        btn_excluir_item_pagamento = ctk.CTkButton(
            row_frame_pagamento, text="❌", width=30, 
            fg_color="red", hover_color="darkred", 
            command=lambda i=index: remover_item_pagamento(i)
        )
        btn_excluir_item_pagamento.grid(row=0, column=2, padx=2)
    
def editar_item_pagamento(index):
    global editando_item_pagamento
    editando_item_pagamento = index

    item = itens_pagamento[index]
    descricao_nova = item["descricao"]

    if tipo_servico in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
        if tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":  # para remover o texto "ADIANTAMENTO DE"
            descricao_nova = descricao_nova.replace("ADIANTAMENTO DE ", "").strip()
        
        descricao_do_item_pagamento_entry.delete(0, tk.END)
        descricao_do_item_pagamento_entry.insert(0, descricao_nova)
        
        descricao_do_item_pagamento_entry.focus()
    elif tipo_servico == "REEMBOLSO UBER":
        saida_destino_entry.delete(0, tk.END)
        saida_destino_entry.insert(0, item.get("saida_e_destino", ""))

        motivo_entry.delete(0, tk.END)
        motivo_entry.insert(0, item.get("motivo", ""))

        valor_caixa_itens_entry.delete(0, tk.END)
        valor_caixa_itens_entry.insert(0, str(item.get("valor", "")))

        saida_destino_entry.focus()
    else:
        motivo_entry.delete(0, tk.END)
        motivo_entry.insert(0, item.get("motivo", ""))

        valor_caixa_itens_entry.delete(0, tk.END)
        valor_caixa_itens_entry.insert(0, str(item.get("valor", "")))

        motivo_entry.focus()

    btn_adicionar_servico_pagamento.configure(text="Salvar", command=lambda: salvar_edicao_pagamento(index))

    atualizar_lista_itens_pagamento()

def salvar_edicao_pagamento(index):
    global editando_item_pagamento
    global descricao_base

    if tipo_servico in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
        entrada = arrumar_texto(descricao_do_item_pagamento_entry.get().upper().strip())
        possui_os = opcao_os_parceiro_combobox.get()

        descricao_formatada, descricao_base, erro = validar_item_pagamento(entrada, tipo_servico, possui_os)

        if erro:
            notification_manager.show_notification(f"Campo DESCRIÇÃO DO ITEM\n{erro}", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return
        
        item_editado = {
            "descricao": descricao_formatada,
            "descricao_base": descricao_base
        }

    elif tipo_servico == "REEMBOLSO UBER":
        saida_e_destino = arrumar_texto(saida_destino_entry.get().upper().strip())
        motivo = arrumar_texto(motivo_entry.get().upper().strip())
        valor = verificar_se_numero(valor_caixa_itens_entry.get())

        # Verificações de campos obrigatórios
        if not motivo and not valor and not saida_e_destino:
            erro = "Campos DESCRIÇÃO DO ITEM, MOTIVO e SAÍDA/DESTINO não podem ser vazios!"
        elif not motivo and not saida_e_destino:
            erro = "Campos MOTIVO e SAÍDA/DESTINO não podem ser vazios!"
        elif not motivo and not valor:
            erro = "Campos DESCRIÇÃO DO ITEM e MOTIVO não podem ser vazios!"
        elif not saida_e_destino and not valor:
            erro = "Campos DESCRIÇÃO DO ITEM e SAÍDA/DESTINO não podem ser vazios!"
        elif not motivo:
            erro = "Campo MOTIVO não pode ser vazio!"
        elif not valor:
            erro = "Campo VALOR não pode ser vazio!"
        elif not saida_e_destino:
            erro = "Campo SAÍDA/DESTINO não pode ser vazio!"
        elif valor is ValueError:
            erro = "Campo VALOR\nPor favor, insira um número válido!"
        else:
            erro = None

        # Exibição de erro, se houver
        if erro:
            notification_manager.show_notification(
                erro, 
                NotifyType.ERROR,
                bg_color="#404040", 
                text_color="#FFFFFF"
            )
            return

        # Adiciona dicionário com dados completos
        item_editado = {
            "saida_e_destino": saida_e_destino,
            "motivo": motivo,
            "valor": valor,
            "descricao": f"{saida_e_destino} - {motivo} - R$ {valor}"
        }
    else:
        motivo = arrumar_texto(motivo_entry.get().upper().strip())
        valor = verificar_se_numero(valor_caixa_itens_entry.get())

        # Verificações de campos obrigatórios
        if not motivo and not valor:
            erro = "Campos DESCRIÇÃO DO ITEM e MOTIVO não podem ser vazios!"
        elif not motivo:
            erro = "Campo MOTIVO não pode ser vazio!"
        elif not valor:
            erro = "Campo VALOR não pode ser vazio!"
        elif valor is ValueError:
            erro = "Campo VALOR\nPor favor, insira um número válido!"
        else:
            erro = None

        # Exibição de erro, se houver
        if erro:
            notification_manager.show_notification(
                erro, 
                NotifyType.ERROR, 
                bg_color="#404040", 
                text_color="#FFFFFF"
            )
            return

        # Adiciona dicionário com dados completos
        item_editado = {
            "motivo": motivo,
            "valor": valor,
            "descricao": f"{motivo} - R$ {valor}"
        } 

    itens_pagamento[index] = item_editado

    if tipo_servico in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
        descricao_do_item_pagamento_entry.delete(0, tk.END)

    if tipo_servico not in {"ADIANTAMENTO/PAGAMENTO PARCEIRO", "RELATÓRIO EXTRA"}:
        if tipo_servico == "REEMBOLSO UBER":
            saida_destino_entry.delete(0, tk.END)
        valor_caixa_itens_entry.delete(0, tk.END)
        motivo_entry.delete(0, tk.END)

    btn_adicionar_servico_pagamento.configure(text="Adicionar", command=add_item_pagamento)

    editando_item_pagamento = None  # Reabilita o botão de excluir

    descricao_do_item_pagamento_entry.focus()

    atualizar_lista_itens_pagamento()

def remover_item_pagamento(index):
    global editando_item_pagamento
    if editando_item_pagamento is None:  # Só permite excluir se não estiver editando
        del itens_pagamento[index]
        atualizar_lista_itens_pagamento()
    else:
        notification_manager.show_notification("Item em edição!\nSalve-o para habilitar a exclusão.", NotifyType.WARNING, bg_color="#404040", text_color="#FFFFFF")
        pass

def add_campos():
    global tipo_servico, aparece_lista_itens_aba_pagamentos, valor_atual_combobox

    # Verificar se há um item em edição
    if editando_item_pagamento is not None:
        notification_manager.show_notification(
            "Item em edição!\nSalve-o para alterar o tipo de serviço.",
            NotifyType.WARNING,
            bg_color="#404040",
            text_color="#FFFFFF"
        )
        tipo_servico_combobox.set(valor_atual_combobox)
        return

    tipo_servico = tipo_servico_combobox.get()

    # Salvar o valor atual do combobox
    valor_atual_combobox = tipo_servico

    prefixo_label.configure(text="PREFIXO:")
    agencia_label.configure(text="AGÊNCIA:")
    os_label.configure(text="OS ou Nº DO CONTRATO (CAIXA):")

    if tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO" and "ESCRITÓRIO" in contratos:
        contrato_sem_escritorio = contratos.copy()
        contrato_sem_escritorio.remove("ESCRITÓRIO")
        contrato_combobox.configure(values=contrato_sem_escritorio)
        contrato_combobox.set("")
    else:
        contrato_combobox.configure(values=contratos)
        contrato_combobox.set("")

    tipo_pagamento_combobox.set("")
    tipo_chave_pix_label.grid_forget()
    tipo_chave_pix_combobox.grid_forget()
    tipo_chave_pix_combobox.set("")
    chave_pix_label.grid_forget()
    chave_pix_entry.grid_forget()
    nome_benef_pix_label.grid_forget()
    nome_benef_pix_entry.grid_forget()

    # Deixa o campo valor como padrão para todos os tipos_servico
    valor_label.grid(row=11, column=0, sticky="w", padx=(10, 10))
    valor_entry.grid(row=11, column=1, sticky="ew", padx=(0, 10), pady=2)

    # Oculta todos os campos por padrão
    for widget in [
        competencia_label, competencia_combobox,
        porcentagem_label, porcentagem_entry,
        motivo_label, motivo_entry,
        saida_destino_label, saida_destino_entry,
        tecnicos_label, tecnicos_entry, descricao_utilidades_label, 
        descricao_utilidades_entry, frame_caixa_itens_pagamento,
        opcao_os_parceiro_label, opcao_os_parceiro_combobox,
    ]:
        widget.grid_forget()

    # Limpa os campos de entrada por padrão
    competencia_combobox.set("")
    opcao_os_parceiro_combobox.set("")
    porcentagem_entry.delete(0, tk.END)
    motivo_entry.delete(0, tk.END)
    saida_destino_entry.delete(0, tk.END)
    tecnicos_entry.delete(0, tk.END)

    aparece_lista_itens_aba_pagamentos = {
        "RELATÓRIO EXTRA", "ADIANTAMENTO/PAGAMENTO PARCEIRO",
        "REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS",
        "SOLICITAÇÃO COM OS", "REEMBOLSO COM OS",
        "REEMBOLSO UBER",
    }

    if tipo_servico == "PREST. SERVIÇO/MÃO DE OBRA":
        competencia_label.grid(row=9, column=0, sticky="w", padx=(10, 10))
        competencia_combobox.grid(row=9, column=1, sticky="ew", padx=(0, 10), pady=2)
        porcentagem_label.grid(row=10, column=0, sticky="w", padx=(10, 10))
        porcentagem_entry.grid(row=10, column=1, sticky="ew", padx=(0, 10), pady=2)

    elif tipo_servico in {"ABASTECIMENTO", "ESTACIONAMENTO", "HOSPEDAGEM"}:
        tecnicos_label.grid(row=2, column=0, sticky="w", padx=(10, 10))
        tecnicos_entry.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=2)

    elif tipo_servico in aparece_lista_itens_aba_pagamentos:
        if tipo_servico in {"SOLICITAÇÃO COM OS", "REEMBOLSO COM OS", "REEMBOLSO UBER"}:
            frame_caixa_itens_pagamento.grid(row=9, column=0, columnspan=2, sticky="nsew", pady=5)
        elif tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
            # opções relacionadas ao opcao_os_parceiro_combobox estão na função atualizar_exibicao_frame_caixa_itens()
            opcao_os_parceiro_label.grid(row=5, column=0, sticky="w", padx=(10, 10))
            opcao_os_parceiro_combobox.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)
        else:    
            frame_caixa_itens_pagamento.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=5)

        if len(itens_pagamento) > 0:
            itens_pagamento.clear()
            atualizar_lista_itens_pagamento()
            add_campos()

        for widget in [
            descricao_do_item_pagamento_label, descricao_do_item_pagamento_entry,
            motivo_label, motivo_entry,
            valor_caixa_itens_label, valor_caixa_itens_entry,
            saida_destino_label, saida_destino_entry,
        ]:
            widget.grid_forget()
        
        for entry in [descricao_do_item_pagamento_entry, motivo_entry]:
            entry.delete(0, tk.END)

        if tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
            descricao_do_item_pagamento_label.grid(row=3, column=0, sticky="w", padx=(10, 10))
            descricao_do_item_pagamento_entry.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=2)
            root.focus()
        elif tipo_servico == "RELATÓRIO EXTRA":
            descricao_do_item_pagamento_label.grid(row=3, column=0, sticky="w", padx=(10, 10))
            descricao_do_item_pagamento_entry.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=2)
            descricao_do_item_pagamento_entry.configure(placeholder_text="PREFIXO - AGÊNCIA - OS - VALOR")
            root.focus()
        else:
            valor_label.grid_forget()
            valor_entry.grid_forget()

            if tipo_servico == "REEMBOLSO UBER":
                saida_destino_label.grid(row=3, column=0, sticky="w", padx=(10, 10))
                saida_destino_entry.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=2)
                saida_destino_entry.configure(placeholder_text="Informe a saída e o destino")

            motivo_label.grid(row=4, column=0, sticky="w", padx=(10, 10))
            motivo_entry.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)
            motivo_entry.configure(placeholder_text="Informe o motivo")
            valor_caixa_itens_label.grid(row=5, column=0, sticky="w", padx=(10, 10))
            valor_caixa_itens_entry.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)
            valor_caixa_itens_entry.configure(placeholder_text="Informe o valor")

        # forçar o label a mover a coluna 0, de modo a
        # padronizar o tamanho dos entrys
        for entry in [motivo_label, valor_caixa_itens_label]:
            entry.configure(text="")

        if tipo_servico in {"REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS"}:
            motivo_label.configure(text="MOTIVO:\t\t      ")
            valor_caixa_itens_label.configure(text="VALOR:")
        elif tipo_servico in {"SOLICITAÇÃO COM OS", "REEMBOLSO COM OS"}:
            motivo_label.configure(text="MOTIVO:\t\t\t     ")
            valor_caixa_itens_label.configure(text="VALOR:")
        elif tipo_servico == "REEMBOLSO UBER":
            saida_destino_label.configure(text="SAÍDA X DESTINO:\t\t")
            motivo_label.configure(text="MOTIVO:\t\t\t     ")
            valor_caixa_itens_label.configure(text="VALOR:")

    if tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
        competencia_label.grid(row=7, column=0, sticky="w", padx=(10, 10))
        competencia_combobox.grid(row=7, column=1, sticky="ew", padx=(0, 10), pady=2)

    # Mostrar ou esconder PREFIXO, OS e AGÊNCIA
    esconde_pref_age_os = {
        "REEMBOLSO SEM OS",
        "SOLICITAÇÃO SEM OS",
        "ABASTECIMENTO",
        "ENVIO DE MATERIAL",
        "AQUISIÇÃO SEM OS",
        "RELATÓRIO EXTRA",
        "ADIANTAMENTO/PAGAMENTO PARCEIRO"
    }

    prefixo_entry.delete(0, tk.END)
    agencia_entry.delete(0, tk.END)
    os_entry.delete(0, tk.END)
    if tipo_servico in esconde_pref_age_os:
        prefixo_label.grid_forget()
        prefixo_entry.grid_forget()
        os_label.grid_forget()
        os_entry.grid_forget()
        agencia_label.grid_forget()
        agencia_entry.grid_forget()
    elif tipo_servico in {"REEMBOLSO UBER", "PREST. SERVIÇO/MÃO DE OBRA"}:
        prefixo_label.grid(row=5, column=0, sticky="w", padx=(10, 10))
        prefixo_entry.configure(placeholder_text="Opcional")
        prefixo_entry.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)

        agencia_label.grid(row=6, column=0, sticky="w", padx=(10, 10))
        agencia_entry.configure(placeholder_text="Opcional")
        agencia_entry.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)

        os_label.grid(row=7, column=0, sticky="w", padx=(10, 10))
        os_entry.configure(placeholder_text="Opcional")
        os_entry.grid(row=7, column=1, sticky="ew", padx=(0, 10), pady=2)
    else:
        prefixo_label.grid(row=5, column=0, sticky="w", padx=(10, 10))
        prefixo_entry.configure(placeholder_text="")
        prefixo_entry.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)
        agencia_label.grid(row=6, column=0, sticky="w", padx=(10, 10))
        agencia_entry.configure(placeholder_text="")
        agencia_entry.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)
        os_label.grid(row=7, column=0, sticky="w", padx=(10, 10))
        os_entry.configure(placeholder_text="")
        os_entry.grid(row=7, column=1, sticky="ew", padx=(0, 10), pady=2)

    tipo_pagamento_combobox.set("") # limpar a seleção antes de configurar os valores
    if tipo_servico in {"PREST. SERVIÇO/MÃO DE OBRA", "ABASTECIMENTO", "ADIANTAMENTO/PAGAMENTO PARCEIRO"}:
        opcoes_pagamento = ["PIX"]
    elif tipo_servico in {"ORÇAMENTO APROVADO", "AQUISIÇÃO SEM OS", "AQUISIÇÃO COM OS", "ENVIO DE MATERIAL", "TRANSPORTADORA"}:
        opcoes_pagamento = ["PIX", "VEXPENSES", "FATURAMENTO"]
    else:
        opcoes_pagamento = ["PIX", "VEXPENSES"]

    tipo_pagamento_combobox.configure(values=opcoes_pagamento)

    if tipo_servico == "ENVIO DE MATERIAL":
        contrato_label.grid_forget()
        contrato_combobox.grid_forget()
    else:
        contrato_label.grid(row=3, column=0, sticky="w", padx=(10, 10))
        contrato_combobox.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=2)
    
    if tipo_servico == "AQUISIÇÃO COM OS":
        tipo_aquisicao_combobox.configure(values=["CORRETIVA DIÁRIA" , "LOCAÇÃO"])
        tipo_aquisicao_combobox.set("")
        tipo_aquisicao_label.grid(row=2, column=0, sticky="w", padx=(10, 10))
        tipo_aquisicao_combobox.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=2)
    elif tipo_servico == "AQUISIÇÃO SEM OS":
        tipo_aquisicao_combobox.configure(values=["EPI", "CRACHÁ", "FERRAMENTAS", "FARDAMENTO", "ESTOQUE", "UTILIDADES"])
        tipo_aquisicao_combobox.set("")
        tipo_aquisicao_label.grid(row=2, column=0, sticky="w", padx=(10, 10))
        tipo_aquisicao_combobox.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=2)
    elif tipo_servico == "COMPRA IN LOCO":
        tipo_aquisicao_label.grid(row=2, column=0, sticky="w", padx=(10, 10))
        tipo_aquisicao_combobox.configure(values=["CORRETIVA DIÁRIA", "ORÇAMENTO APROVADO"])
        tipo_aquisicao_combobox.set("")
        tipo_aquisicao_combobox.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=2)        
    else:
        tipo_aquisicao_label.grid_forget()
        tipo_aquisicao_combobox.grid_forget()

def atualizar_exibicao_frame_caixa_itens():
    if tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
        if opcao_os_parceiro_combobox.get() in {"SIM", "NÃO"}:
            frame_caixa_itens_pagamento.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=5)
            root.focus()
        else:
            frame_caixa_itens_pagamento.grid_forget()

        # Atualizar o placeholder do campo de descrição
        if opcao_os_parceiro_combobox.get() == "SIM":
            descricao_do_item_pagamento_entry.configure(placeholder_text="OS - PREFIXO - AGÊNCIA - PORCENTAGEM")
            itens_pagamento.clear()
            atualizar_lista_itens_pagamento()
        else:
            descricao_do_item_pagamento_entry.configure(placeholder_text="MOTIVO - PORCENTAGEM")
            itens_pagamento.clear()
            atualizar_lista_itens_pagamento()

def adiciona_campo_pix():
    tipo_pagamento = tipo_pagamento_combobox.get()

    # Mostrar ou esconder campos para PIX
    if tipo_pagamento == 'PIX':
        tipo_chave_pix_label.grid(row=13, column=0, sticky="w", padx=(10, 10))
        tipo_chave_pix_combobox.grid(row=13, column=1, sticky="ew", padx=(0, 10), pady=2)
        chave_pix_label.grid(row=14, column=0, sticky="w", padx=(10, 10))
        chave_pix_entry.grid(row=14, column=1, sticky="ew", padx=(0, 10), pady=2)
        nome_benef_pix_label.grid(row=15, column=0, sticky="w", padx=(10, 10))
        nome_benef_pix_entry.grid(row=15, column=1, sticky="ew", padx=(0, 10), pady=2)
    else:
        tipo_chave_pix_label.grid_forget()
        tipo_chave_pix_combobox.grid_forget()
        tipo_chave_pix_combobox.set("")
        chave_pix_label.grid_forget()
        chave_pix_entry.grid_forget()
        chave_pix_entry.delete(0, tk.END)
        nome_benef_pix_label.grid_forget()
        nome_benef_pix_entry.grid_forget()
        nome_benef_pix_entry.delete(0, tk.END)

def esconde_campos_pagamento_qrcode():
    tipo_chave = tipo_chave_pix_combobox.get()

    if tipo_chave == "QR CODE":
        chave_pix_label.grid_forget()
        chave_pix_entry.grid_forget()
        nome_benef_pix_label.grid_forget()
        nome_benef_pix_entry.grid_forget()

        chave_pix_entry.delete(0, tk.END)
        nome_benef_pix_entry.delete(0, tk.END)
    else:
        chave_pix_label.grid(row=14, column=0, sticky="w", padx=(10, 10))
        chave_pix_entry.grid(row=14, column=1, sticky="ew", padx=(0, 10), pady=2)
        nome_benef_pix_label.grid(row=15, column=0, sticky="w", padx=(10, 10))
        nome_benef_pix_entry.grid(row=15, column=1, sticky="ew", padx=(0, 10), pady=2)

def campo_descricao_utilidades():
    tipo_aquisicao = tipo_aquisicao_combobox.get()

    if tipo_aquisicao == "UTILIDADES":
        descricao_utilidades_label.grid(row=4, column=0, sticky="w", padx=(10, 10))
        descricao_utilidades_entry.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)
    else:
        descricao_utilidades_label.grid_forget()
        descricao_utilidades_entry.grid_forget()
        descricao_utilidades_entry.delete(0, tk.END)

def gerar_solicitacao():
    nome_usuario = arrumar_texto(nome_usuario_entry.get().upper())
    tipo_servico = arrumar_texto(tipo_servico_combobox.get().upper())
    nome_fornecedor = arrumar_texto(nome_fornecedor_entry.get().upper())
    prefixo = valida_prefixo(prefixo_entry.get())
    agencia = arrumar_texto(agencia_entry.get().upper())
    os_num = valida_os(os_entry.get())
    contrato = arrumar_texto(contrato_combobox.get().upper())
    motivo = arrumar_texto(motivo_entry.get().upper())
    
    if tipo_servico in {
        "REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS",
        "SOLICITAÇÃO COM OS", "REEMBOLSO COM OS",
        "REEMBOLSO UBER",
    }:
        total_valor = sum(float(str(item.get("valor", 0)).replace(".", "").replace(",", ".")) for item in itens_pagamento)
        valor_tab1 = verificar_se_numero(str(total_valor).replace(".", ","))
    else:
        valor_tab1 = verificar_se_numero(valor_entry.get())

    tipo_pagamento = arrumar_texto(tipo_pagamento_combobox.get().upper())
    tecnicos = arrumar_texto(tecnicos_entry.get().upper())
    competencia = arrumar_texto(competencia_combobox.get().upper())
    porcentagem = valida_porcentagem(porcentagem_entry.get().upper())
    tipo_aquisicao = arrumar_texto(tipo_aquisicao_combobox.get().upper())
    descricao_utilidades = arrumar_texto(descricao_utilidades_entry.get().upper())

    if tipo_pagamento == "PIX":
        tipo_chave_pix = arrumar_texto(tipo_chave_pix_combobox.get())
        chave_pix = arrumar_texto(chave_pix_entry.get())
        nome_benef_pix = arrumar_texto(nome_benef_pix_entry.get().upper())

    # Facilitar a identificação do erro pelo nome de usuário
    # logging.info(f"Aplicação iniciada. User: {nome_usuario}")

    departamento, sigla_contrato = acessa_bd_contratos(contrato)
    print(f"Departamento: {departamento}, Sigla: {sigla_contrato}")

    # Verificar se algum campo obrigatório está vazio
    campos_obrigatorios = [
        (nome_usuario, "USUÁRIO"),
        (tipo_servico, "TIPO DE SERVIÇO"),
        (nome_fornecedor, "NOME DO FORNECEDOR/BENEFICIÁRIO"),
        (contrato, "CONTRATO"),
        (valor_tab1, "VALOR"),
        (tipo_pagamento, "TIPO DE PAGAMENTO")
    ]

    if tipo_servico == "ABASTECIMENTO":
        campos_obrigatorios.append((tecnicos, "TÉCNICOS"))
    elif tipo_servico == "PREST. SERVIÇO/MÃO DE OBRA":
        campos_obrigatorios.extend([
            (competencia, "COMPETÊNCIA"),
            (porcentagem, "% DO ADIANTAMENTO DO PARCEIRO")
        ])
    elif tipo_servico in {"AQUISIÇÃO COM OS", "COMPRA IN LOCO"}:
        campos_obrigatorios.extend([
            (tipo_aquisicao, "TIPO DE AQUISIÇÃO"),
            (prefixo, "PREFIXO"),
            (agencia, "AGÊNCIA"),
            (os_num, "OS")
        ])
    elif tipo_servico == "AQUISIÇÃO SEM OS":
        campos_obrigatorios.append((tipo_aquisicao, "TIPO DE AQUISIÇÃO"))
        if tipo_aquisicao == "UTILIDADES":
            campos_obrigatorios.append((descricao_utilidades, "DESCRIÇÃO UTILIDADES"))
    elif tipo_servico == "ENVIO DE MATERIAL":
        campos_obrigatorios.remove((contrato, "CONTRATO"))
    elif tipo_servico in {"ESTACIONAMENTO", "HOSPEDAGEM"}:
        campos_obrigatorios.extend([
            (tecnicos, "TÉCNICOS"),
            (prefixo, "PREFIXO"),
            (agencia, "AGÊNCIA"),
            (os_num, "OS")
        ])        
    elif tipo_servico in {"CARRETO", "ORÇAMENTO APROVADO", "TRANSPORTADORA"}:
        campos_obrigatorios.extend([
            (prefixo, "PREFIXO"),
            (agencia, "AGÊNCIA"),
            (os_num, "OS")
        ])
    elif tipo_servico in aparece_lista_itens_aba_pagamentos:
        campos_obrigatorios.append((itens_pagamento if itens_pagamento else None, "DESCRIÇÃO DO ITEM"))
        
        if tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
            campos_obrigatorios.append((competencia, "COMPETÊNCIA"))

        if tipo_servico in {
            "REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS",
            "SOLICITAÇÃO COM OS", "REEMBOLSO COM OS",
            "REEMBOLSO UBER"
        }:
            campos_obrigatorios = [campo for campo in campos_obrigatorios if campo != (valor_tab1, "VALOR")]

        if tipo_servico in {"REEMBOLSO COM OS", "SOLICITAÇÃO COM OS"}:
            campos_obrigatorios.extend([
                (prefixo, "PREFIXO"),
                (agencia, "AGÊNCIA"),
                (os_num, "OS")
            ])

    if tipo_pagamento == "PIX" and tipo_chave_pix != "QR CODE":
        campos_obrigatorios.extend([
            (tipo_chave_pix, "TIPO DA CHAVE PIX"),
            (chave_pix, "CHAVE PIX")
        ])

    if contrato in {"ESCRITÓRIO", "ATA BB CURITIBA", "CAIXA BAHIA", "CAIXA CURITIBA", "CAIXA MANAUS", "INFRA CURITIBA"}:
        campos_obrigatorios = [
            item for item in campos_obrigatorios
            if item not in [(prefixo, "PREFIXO"), (agencia, "AGÊNCIA"), (os_num, "OS")]
        ]

    # Verificar campos vazios
    campos_vazios = [nome for valor, nome in campos_obrigatorios if not valor]

    notification_manager = NotificationManager(root)  # passando a instância da janela principal

    if campos_vazios:
        if campos_vazios == ["DESCRIÇÃO DO ITEM"]:
            notification_manager.show_notification("Campo DESCRIÇÃO DO ITEM\nPor favor, adicione um item à lista.", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return
        else:
            notification_manager.show_notification("Preencha os campos em branco!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return

    if prefixo == "Prefixo inválido":
        notification_manager.show_notification("Campo PREFIXO\nPrefixo inválido. Use o padrão XXXX/XX.", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return     

    if os_num == "OS_invalida":
        notification_manager.show_notification("Campo OS\nPor favor, insira uma OS válida!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return
    
    if valor_tab1 is ValueError:
        notification_manager.show_notification("Campo VALOR\nPor favor, insira um número válido!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return
    
    if porcentagem == ValueError:
        notification_manager.show_notification("Campo PORCENTAGEM\nPor favor, insira um número válido!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return
    elif porcentagem == "RangeError":
        notification_manager.show_notification("Campo PORCENTAGEM\nPor favor, insira um número entre 1 e 100.", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return
        
    if identifica_preenchimento_pref_os_age(prefixo, agencia, os_num):
        return

    # Definindo o nome do arquivo
    data_atual = datetime.now().strftime("%d.%m.%Y")
    
    if os_num == "":
        nome_arquivo = f"{valor_tab1} - {data_atual} - OC {nome_fornecedor} - {tipo_servico} - {sigla_contrato}.xlsx"
    else:
        nome_arquivo = f"{valor_tab1} - {data_atual} - OC {nome_fornecedor} - {os_num} - {agencia} - {prefixo} - {tipo_servico} - {sigla_contrato}.xlsx"    
    
    nome_arquivo = re.sub(r'[<>:"/\\|?*\x00]', ".", nome_arquivo)

    nome_arquivo_sem_ext, ext = splitext(nome_arquivo)

    # Gerar texto da solicitação
    if tipo_servico == "PREST. SERVIÇO/MÃO DE OBRA":
        texto = (
            f"Solicito o pagamento para {nome_fornecedor}, referente à obra: "
            f"{prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
            if prefixo
            else
            f"Solicito o pagamento para {nome_fornecedor}, para {contrato}.\n\n"
        )
        texto += f"SERVIÇO: {tipo_servico}\n\n"
        texto += f"COMPETÊNCIA: {competencia}\n\n"
        texto += f"PORCENTAGEM DO ADIANTAMENTO: {porcentagem}%\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif tipo_servico == "AQUISIÇÃO COM OS" or tipo_servico == "COMPRA IN LOCO":
        texto = (
            f"Solicito o pagamento para {nome_fornecedor}, referente à obra: "
            f"{prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
        )
        texto += f"SERVIÇO: {tipo_servico} - {tipo_aquisicao}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif tipo_servico == "AQUISIÇÃO SEM OS":
        texto = f"Solicito o pagamento para {nome_fornecedor}, para {contrato}.\n\n"
        
        if descricao_utilidades:
            texto += f"SERVIÇO: {tipo_servico} - {tipo_aquisicao}: {descricao_utilidades}\n\n"
        else:
            texto += f"SERVIÇO: {tipo_servico} - {tipo_aquisicao}\n\n"

        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif tipo_servico in {"REEMBOLSO COM OS", "SOLICITAÇÃO COM OS"}:
        texto = (
            f"Solicito o pagamento para {nome_fornecedor}, referente à obra: "
            f"{prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
        )
        texto += f"SERVIÇO: {tipo_servico}\n\n"

        if len(itens_pagamento) == 1:
            item = itens_pagamento[0]
            texto += f"MOTIVO: {item['motivo']}\n\n"
            texto += f"*VALOR: R$ {valor_tab1}*\n\n"
        else:
            texto += "MOTIVOS:\n"
            for idx, item in enumerate(itens_pagamento, start=1):
                texto += f"{idx}. {item['motivo']} (R$ {item['valor']})\n"
            texto += f"\n*VALOR TOTAL: R$ {valor_tab1}*\n\n"
    elif tipo_servico in {"REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS"}:
        texto = f"Solicito o pagamento para {nome_fornecedor}, para {contrato}.\n\n"
        texto += f"SERVIÇO: {tipo_servico}\n\n"

        if len(itens_pagamento) == 1:
            item = itens_pagamento[0]
            texto += f"MOTIVO: {item['motivo']}\n\n"
            texto += f"*VALOR: R$ {valor_tab1}*\n\n"
        else:
            texto += "MOTIVOS:\n"
            for idx, item in enumerate(itens_pagamento, start=1):
                texto += f"{idx}. {item['motivo']} (R$ {item['valor']})\n"
            texto += f"\n*VALOR TOTAL: R$ {valor_tab1}*\n\n"
    elif tipo_servico == "ABASTECIMENTO":
        texto = (
            f"Solicito o pagamento ao fornecedor {nome_fornecedor}, referente ao "
            f"abastecimento dos técnicos {tecnicos}, para {contrato}.\n\n"
        )
        texto += f"SERVIÇO: {tipo_servico}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif tipo_servico == "ESTACIONAMENTO":
        texto = (
            f"Solicito o pagamento ao fornecedor {nome_fornecedor}, pelo estacionamento "
            f"dos técnicos {tecnicos}, referente à obra: {prefixo} - {agencia} - {os_num}, "
            f"para {contrato}.\n\n"
        )
        texto += f"SERVIÇO: {tipo_servico}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif tipo_servico == "REEMBOLSO UBER":
        if len(itens_pagamento) == 1:
            item = itens_pagamento[0]
            texto = (
                f"Solicito reembolso referente ao deslocamento de {nome_fornecedor}, para {item['saida_e_destino']}, "
                f"referente à obra: {prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
                if prefixo
                else f"Solicito reembolso referente ao deslocamento de {nome_fornecedor}, para {item['saida_e_destino']}, "
                f"para {contrato}.\n\n"
            )
            texto += f"SERVIÇO: {tipo_servico}\n\n"
            texto += f"MOTIVO: {item['motivo']}\n\n"
            texto += f"*VALOR: R$ {valor_tab1}*\n\n"
        else:
            texto = (
                f"Solicito reembolso referente ao deslocamento de {nome_fornecedor} "
                f"referente à obra: {prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
                if prefixo
                else f"Solicito reembolso referente ao deslocamento de {nome_fornecedor} para {contrato}.\n\n"
            )
            texto += f"SERVIÇO: {tipo_servico}\n\n"
            texto += "DESLOCAMENTOS:\n"
            for idx, item in enumerate(itens_pagamento, start=1):
                texto += f"{idx}. {item['saida_e_destino']} - {item['motivo']} (R$ {item['valor']})\n"
            texto += f"\n*VALOR TOTAL: R$ {valor_tab1}*\n\n"
    elif tipo_servico == "HOSPEDAGEM":
        texto = (
            f"Solicito o pagamento ao fornecedor {nome_fornecedor} pela hospedagem dos "
            f"técnicos {tecnicos} referente à obra: {prefixo} - {agencia} - {os_num}, "
            f"para {contrato}.\n\n"
        )
        texto += f"SERVIÇO: {tipo_servico}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif tipo_servico == "ENVIO DE MATERIAL":
        texto = f"Solicito o pagamento ao fornecedor {nome_fornecedor}.\n\n"
        texto += f"SERVIÇO: {tipo_servico}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif tipo_servico == "RELATÓRIO EXTRA":
        texto = f"Solicito o pagamento ao fornecedor {nome_fornecedor} pela confecção de relatório(s) técnico(s) relacionado(s) abaixo, para o {contrato}:\n\n"
        texto += f"SERVIÇO: CONFECÇÃO DE {tipo_servico}\n\n"

        for item in itens_pagamento:
            texto += f"{item["descricao"]}\n"

        texto += "\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
        if opcao_os_parceiro_combobox.get() == "SIM":
            if len(itens_pagamento) == 1:
                texto = (
                    f"Solicito o pagamento para {nome_fornecedor}, referente à obra listada abaixo, para {contrato}:\n\n"
                )
            else:
                texto = (
                    f"Solicito o pagamento para {nome_fornecedor}, referente as obras listadas abaixo, para {contrato}:\n\n"
                )
            texto += f"SERVIÇO: {tipo_servico}\n\n"
            texto += f"COMPETÊNCIA: {competencia}\n\n"
            
            for item in itens_pagamento:
                texto += f"{item["descricao"]}\n"
            
            texto += f"\nVALOR: R$ {valor_tab1}\n\n"
        else:
            texto = (
                f"Solicito o pagamento para {nome_fornecedor}, referente ao listado abaixo, para {contrato}:\n\n"
            )
            texto += f"SERVIÇO: {tipo_servico}\n\n"
            texto += f"COMPETÊNCIA: {competencia}\n\n"

            for item in itens_pagamento:
                texto += f"{item["descricao"]}\n"

            texto += f"\nVALOR: R$ {valor_tab1}\n\n"
    elif contrato == "ESCRITÓRIO" and tipo_aquisicao:
        texto = f"Solicito o pagamento para {nome_fornecedor}, para {contrato}.\n\n"
        texto += f"SERVIÇO: {tipo_servico} - {tipo_aquisicao}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    else:
        texto = (
            f"Solicito o pagamento ao fornecedor {nome_fornecedor}, referente à obra: "
            f"{prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
        )
        texto += f"SERVIÇO: {tipo_servico}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"

    if tipo_pagamento == "FATURAMENTO":
        texto = (
            f"Assunto: {nome_arquivo_sem_ext}\n\n"
            "Prezado(a),\n\n"
            "Solicito autorização para compra referente aos materiais descritos na "
            "ordem de compra e orçamento em anexo."
        )
    elif tipo_pagamento == "PIX":
        if tipo_chave_pix == "QR CODE":
            texto += f"Pagamento PIX via {tipo_chave_pix}"
        else:
            texto += f"Segue PIX {tipo_chave_pix} ⬇\n\n{chave_pix}"
            texto += f"\n\n{nome_benef_pix}" if nome_benef_pix else ""
    else:
        texto += "Pagamento via VEXPENSES"

    # Exibir texto na caixa de texto
    texto_solicitacao.delete(1.0, tk.END)
    texto_solicitacao.insert(tk.END, texto)

    # Insere os dados no BD
    from .bd import conecta_banco_pagamentos
    conecta_banco_pagamentos(nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
        contrato, motivo, valor_tab1, tipo_pagamento, tecnicos, competencia,
        porcentagem, tipo_aquisicao)

    # Copiar automaticamente o texto gerado caso o switch esteja ativo
    if switch_autocopia_var.get():
        pyperclip.copy(texto)

    if switch_gerar_excel_var.get():
        descricao_itens = ""
        valor_itens = ""

        if tipo_servico in {"RELATÓRIO EXTRA", "ADIANTAMENTO/PAGAMENTO PARCEIRO"} and itens_pagamento:
            descricao_itens = "\n".join(item["descricao"] for item in itens_pagamento)

            if opcao_os_parceiro_combobox.get() == "SIM" and len(itens_pagamento) == 1:
                partes = [parte.strip() for parte in descricao_base.split('-')]

                os_num = partes[0]
                prefixo = partes[1]
                agencia = partes[2]

                print(f"Prefixo: {prefixo}, Agência: {agencia}, OS: {os_num}")
        
        if tipo_servico in {
            "REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS",
            "SOLICITAÇÃO COM OS", "REEMBOLSO COM OS", "REEMBOLSO UBER"
        }:
            if tipo_servico == "REEMBOLSO UBER":
                descricao_itens = "\n".join(
                    f"{item['saida_e_destino']} - {item['motivo']}" for item in itens_pagamento
                )
            else:
                descricao_itens = "\n".join(item["motivo"] for item in itens_pagamento)

            valor_itens = "\n".join(str(item["valor"]) for item in itens_pagamento)

        # Criando uma instância do dataclass DadosRequisicao
        dados = DadosRequisicao(
            root=root,
            nome_arquivo=nome_arquivo,
            tipo_servico=tipo_servico,
            nome_fornecedor=nome_fornecedor,
            os_num=os_num,
            prefixo=prefixo,
            agencia=agencia,
            contrato=contrato,
            nome_usuario=nome_usuario,
            tipo_pagamento=tipo_pagamento,
            departamento=departamento,
            valor=valor_tab1,
            tecnicos=tecnicos,
            usuarios_varios_departamentos=usuarios_varios_departamentos,
            usuarios_gerais=usuarios_gerais,
            motivo=motivo,
            descricao_itens=descricao_itens,
            valor_itens=valor_itens,
        )

        gerar_excel(dados)

# -------------------------------
# Fim das funções da aba "Pagamento"
# -------------------------------

def gerar_texto_email():
    # Coletar dados dos campos
    nome_usuario_tab2 = arrumar_texto(nome_usuario_entry_tab2.get().upper())
    tipo_servico_tab2 = arrumar_texto(tipo_servico_combobox_tab2.get().upper())
    nome_fornecedor_tab2 = arrumar_texto(nome_fornecedor_entry_tab2.get().upper())
    prefixo_tab2 = valida_prefixo(prefixo_entry_tab2.get())
    agencia_tab2 = arrumar_texto(agencia_entry_tab2.get().upper())
    os_num_tab2 = valida_os(os_entry_tab2.get())
    endereco_tab2 = arrumar_texto(endereco_entry_tab2.get().upper())
    valor_tab2 = verificar_se_numero(valor_entry_tab2.get())
    tipo_pagamento_tab2 = arrumar_texto(tipo_pagamento_combobox_tab2.get().upper())
    num_orcamento_tab2 = arrumar_texto(num_orcamento_entry_tab2.get().upper())

    # Verificar se algum campo obrigatório está vazio
    campos_obrigatorios = [
        (nome_usuario_tab2, "USUÁRIO"),
        (tipo_servico_tab2, "TIPO DE SERVIÇO"),
        (nome_fornecedor_tab2, "NOME DO FORNECEDOR/BENEFICIÁRIO"),
        (valor_tab2, "VALOR"),
        (tipo_pagamento_tab2, "TIPO DE PAGAMENTO")
    ]

    if tipo_servico_tab2 in {"COMPRAS EM GERAL - COM OS", "LOCAÇÃO"}:
        # Adiciona os campos comuns para os dois tipos
        campos_obrigatorios.extend([
            (prefixo_tab2, "PREFIXO"),
            (agencia_tab2, "AGÊNCIA"),
            (os_num_tab2, "OS")
        ])
        
        # Adiciona o campo "ENDEREÇO" apenas para "LOCAÇÃO"
        if tipo_servico_tab2 == "LOCAÇÃO":
            campos_obrigatorios.append((endereco_tab2, "ENDEREÇO"))           

    # Verificar campos vazios
    campos_vazios = [nome for valor, nome in campos_obrigatorios if not valor]

    if prefixo_tab2 == "Prefixo inválido":
        notification_manager.show_notification("Campo PREFIXO\nPrefixo inválido. Use o padrão XXXX/XX.", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return  

    if valor_tab2 == ValueError:
        notification_manager.show_notification(f"Campo VALOR\nPor favor, insira um número válido!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return

    if os_num_tab2 == "OS_invalida":
        notification_manager.show_notification(f"Campo OS\nPor favor, insira uma OS válida!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return

    if campos_vazios:
        notification_manager.show_notification(f"Preencha os campos obrigatórios em branco!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return

    if tipo_servico_tab2 == "COMPRAS EM GERAL - COM OS":
        texto = f"Prezado Fornecedor {nome_fornecedor_tab2},\n\n"
        
        if tipo_pagamento_combobox_tab2 == "FATURAMENTO":
            texto += f"Comunico que está autorizado para FATURAMENTO o pedido {os_num_tab2}, no valor de R$ {valor_tab2}.\n\n"
        else:
            texto += f"Comunico que está autorizado para pagamento via {tipo_pagamento_tab2} o pedido {num_orcamento_tab2}, no valor de R$ {valor_tab2}.\n\n" if num_orcamento_tab2 else f"Comunico que está autorizado para pagamento via {tipo_pagamento_tab2} o pedido S/N, no valor de R$ {valor_tab2}.\n\n"
        
        texto += f"SEGUE INFORMAÇÕES PARA NOTA FISCAL:\n{prefixo_tab2} - {agencia_tab2} - {os_num_tab2}\n\n"
        texto += f"Prezado fornecedor, solicito por gentileza que a partir deste momento todos os e-mails enviados sejam respondidos para todos.\n"
        texto += f"Nossa empresa solicita que seja incluída na nota fiscal as informações referentes a obra enviada no corpo do e-mail no momento da autorização da compra.\n"
        texto += f"Gostaria de solicitar, por gentileza, o envio da nota fiscal, boleto e ordem de compra para compras faturadas. Para pagamentos à vista, solicito apenas a nota fiscal e a ordem de compra.\n"
        texto += f"Por favor, encaminhem todos os documentos para o e-mail, respondendo para todos os envolvidos."
    
    elif tipo_servico_tab2 == "COMPRAS EM GERAL - SEM OS":
        texto = f"Prezado(a),\n\n"
        texto += f"Comunico que está autorizado para pagamento via {tipo_pagamento_tab2} o pedido {num_orcamento_tab2}, no valor de R$ {valor_tab2}.\n\n" if num_orcamento_tab2 else f"Comunico que está autorizado para pagamento via {tipo_pagamento_tab2} o pedido S/N, no valor de R$ {valor_tab2}.\n\n"
    
    else:
        texto = f"Prezado Fornecedor {nome_fornecedor_tab2},\n\n"
        texto += f"Comunico que está autorizado a locação de EQUIPAMENTO via {tipo_pagamento_tab2}, referente ao pedido {num_orcamento_tab2}, no valor de R$ {valor_tab2}.\n\n" if num_orcamento_tab2 else f"Comunico que está autorizado a locação de EQUIPAMENTO via {tipo_pagamento_tab2}, no valor de R$ {valor_tab2}.\n\n"
        texto += f"Segue informação referente ao local para entrega do material:\n{endereco_tab2}\n\n"
        texto += f"SEGUE INFORMAÇÕES PARA NOTA FISCAL:\n{prefixo_tab2} - {agencia_tab2} - {os_num_tab2}\n\n"
        texto += f"Prezado fornecedor, solicito por gentileza que a partir deste momento todos os e-mails enviados sejam respondidos para todos.\n"
        texto += f"Nossa empresa solicita que seja incluída na nota fiscal as informações referentes a obra enviada no corpo do e-mail no momento da autorização da compra.\n"
        texto += f"Gostaria de solicitar, por gentileza, o envio da nota fiscal, boleto e ordem de compra para compras faturadas. Para pagamentos à vista, solicito apenas a nota fiscal e a ordem de compra.\n"
        texto += f"Por favor, encaminhem todos os documentos para o e-mail, respondendo para todos os envolvidos."

    # Exibir texto na caixa de texto
    texto_email.delete(1.0, tk.END)
    texto_email.insert(tk.END, texto)

    # Copiar automaticamente o texto gerado caso o switch esteja ativo
    if switch_autocopia_frame_tab2_var.get():
        pyperclip.copy(texto)

# -------------------------------
# Funções da aba "Aquisições"
# -------------------------------

def add_campos_tab3():
    tipo_aquisicao_tab3 = tipo_aquisicao_combobox_tab3.get()
    contrato_tab3 = contrato_combobox_tab3.get()
 
    if tipo_aquisicao_tab3 == "COMPRA":
        data_label_tab3.grid_forget()
        data_entry_tab3.grid_forget()
        #quantidade_label_tab3.grid(row=4, column=0, sticky="w", padx=(10, 10))
        #quantidade_entry_tab3.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)
        frame_caixa_itens.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=5)       
        btn_adicionar_servico.grid(row=10, column=1, sticky="ew", padx=(0, 10), pady=5)
        prazo_label_tab3.grid(row=12, column=0, sticky="w", padx=(10, 10))
        prazo_entry_tab3.grid(row=12, column=1, sticky="ew", padx=(0, 10), pady=2)
        servico_label_tab3.grid_forget()
        servico_entry_tab3.grid_forget()
        periodo_locacao_label_tab3.grid_forget()
        periodo_locacao_combobox_tab3.grid_forget()
        quantidade_locacao_label_tab3.grid_forget()
        quantidade_locacao_entry_tab3.grid_forget()
        prefixo_label_tab3.grid(row=13, column=0, sticky="w", padx=(10, 10))
        prefixo_entry_tab3.grid(row=13, column=1, sticky="ew", padx=(0, 10), pady=2)
        prefixo_entry_tab3.configure(placeholder_text="Opcional")
        agencia_label_tab3.grid(row=14, column=0, sticky="w", padx=(10, 10))
        agencia_entry_tab3.grid(row=14, column=1, sticky="ew", padx=(0, 10), pady=2)
        agencia_entry_tab3.configure(placeholder_text="Opcional")
        os_label_tab3.grid(row=15, column=0, sticky="w", padx=(10, 10))
        os_entry_tab3.grid(row=15, column=1, sticky="ew", padx=(0, 10), pady=2)
        os_entry_tab3.configure(placeholder_text="Opcional")
        opcao_entrega_label_tab3.grid(row=16, column=0, sticky="w", padx=(10, 10))
        opcao_entrega_combobox_tab3.grid(row=16, column=1, sticky="ew", padx=(0, 10), pady=2)
        nome_responsavel_label_tab3.grid(row=18, column=0, sticky="w", padx=(10, 10))
        nome_responsavel_entry_tab3.grid(row=18, column=1, sticky="ew", padx=(0, 10), pady=2)
        contato_responsavel_agencia_label_tab3.grid(row=19, column=0, sticky="w", padx=(10, 10))
        contato_responsavel_entry_tab3.grid(row=19, column=1, sticky="ew", padx=(0, 10), pady=2)
        observacoes_label_tab3.grid(row=20, column=0, sticky="w", padx=(10, 10))
        observacoes_entry_tab3.grid(row=20, column=1, sticky="ew", padx=(0, 10), pady=2)
    elif tipo_aquisicao_tab3 == "LOCAÇÃO":
        frame_caixa_itens.grid_forget()
        prazo_label_tab3.grid_forget()
        prazo_entry_tab3.grid_forget()
        descricao_locacao_label_tab3.grid(row=3, column=0, sticky="w", padx=(10, 10))
        descricao_locacao_entry_tab3.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=2)
        data_label_tab3.grid(row=4, column=0, sticky="w", padx=(10, 10))
        data_entry_tab3.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)
        servico_label_tab3.grid(row=5, column=0, sticky="w", padx=(10, 10))
        servico_entry_tab3.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)
        periodo_locacao_label_tab3.grid(row=6, column=0, sticky="w", padx=(10, 10))
        periodo_locacao_combobox_tab3.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)
        quantidade_locacao_label_tab3.grid(row=7, column=0, sticky="w", padx=(10, 10))
        quantidade_locacao_entry_tab3.grid(row=7, column=1, sticky="ew", padx=(0, 10), pady=2)
        prefixo_label_tab3.grid(row=8, column=0, sticky="w", padx=(10, 10))
        prefixo_entry_tab3.grid(row=8, column=1, sticky="ew", padx=(0, 10), pady=2)
        prefixo_entry_tab3.configure(placeholder_text="")
        agencia_label_tab3.grid(row=9, column=0, sticky="w", padx=(10, 10))
        agencia_entry_tab3.grid(row=9, column=1, sticky="ew", padx=(0, 10), pady=2)
        agencia_entry_tab3.configure(placeholder_text="")
        os_label_tab3.grid(row=10, column=0, sticky="w", padx=(10, 10))
        os_entry_tab3.grid(row=10, column=1, sticky="ew", padx=(0, 10), pady=2)
        os_entry_tab3.configure(placeholder_text="")
        opcao_entrega_label_tab3.grid(row=11, column=0, sticky="w", padx=(10, 10))
        opcao_entrega_combobox_tab3.grid(row=11, column=1, sticky="ew", padx=(0, 10), pady=2)
        nome_responsavel_label_tab3.grid(row=18, column=0, sticky="w", padx=(10, 10))
        nome_responsavel_entry_tab3.grid(row=18, column=1, sticky="ew", padx=(0, 10), pady=2)
        contato_responsavel_agencia_label_tab3.grid(row=19, column=0, sticky="w", padx=(10, 10))
        contato_responsavel_entry_tab3.grid(row=19, column=1, sticky="ew", padx=(0, 10), pady=2)
        observacoes_label_tab3.grid(row=20, column=0, sticky="w", padx=(10, 10))
        observacoes_entry_tab3.grid(row=20, column=1, sticky="ew", padx=(0, 10), pady=2)
    
    if contrato_tab3 == "ESCRITÓRIO":
        prefixo_label_tab3.grid_forget()
        prefixo_entry_tab3.grid_forget()
        prefixo_entry_tab3.delete(0, tk.END)
        os_label_tab3.grid_forget()
        os_entry_tab3.grid_forget()
        os_entry_tab3.delete(0, tk.END)
        agencia_label_tab3.grid_forget()
        agencia_entry_tab3.grid_forget()
        agencia_entry_tab3.delete(0, tk.END)

    if opcao_entrega_combobox_tab3.get() == "":
        local_retirada_label_tab3.grid_forget()
        local_retirada_entry_tab3.grid_forget()
        endereco_agencia_label_tab3.grid_forget()
        endereco_agencia_entry_tab3.grid_forget()
    elif opcao_entrega_combobox_tab3.get() == "ENTREGA":
        local_retirada_label_tab3.grid_forget()
        local_retirada_entry_tab3.grid_forget()
        endereco_agencia_label_tab3.grid(row=17, column=0, sticky="w", padx=(10, 10))
        endereco_agencia_entry_tab3.grid(row=17, column=1, sticky="ew", padx=(0, 10), pady=2)
    elif opcao_entrega_combobox_tab3.get() == "RETIRADA":
        endereco_agencia_label_tab3.grid_forget()
        endereco_agencia_entry_tab3.grid_forget()
        local_retirada_label_tab3.grid(row=17, column=0, sticky="w", padx=(10, 10))
        local_retirada_entry_tab3.grid(row=17, column=1, sticky="ew", padx=(0, 10), pady=2)

# Lista para armazenar serviços e quantidades
servicos_tab3 = []  # Exemplo: [("Abertura de porta", 1, "2m", "1m", "3m", "2cm", "http://exemplo.com")]

# Função para adicionar serviços à lista
def adicionar_item_tab3():
    servico = descricao_compra_entry_tab3.get().strip().upper()
    quantidade = quantidade_entry_tab3.get().strip().upper()
    altura = altura_entry_tab3.get().strip().upper()
    largura = largura_entry_tab3.get().strip().upper()
    comprimento = comprimento_entry_tab3.get().strip().upper()
    espessura = espessura_entry_tab3.get().strip().upper()
    link = link_entry_tab3.get().strip().upper()

    if servico and not quantidade:
        notification_manager.show_notification(
            "Campo QUANTIDADE\nPreencha o campo!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
        )
        return
    elif not servico and quantidade:
        notification_manager.show_notification(
            "Campo DESCRIÇÃO\nPreencha o campo!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
        )
        return
    elif not servico and not quantidade:
        notification_manager.show_notification(
            "Campos DESCRIÇÃO e QUANTIDADE\nPreencha os campos!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
        )
        return
    else:
        servicos_tab3.append([
            servico, quantidade, altura, largura, comprimento, espessura, link
        ])
        descricao_compra_entry_tab3.delete(0, "end")

        quantidade_entry_tab3.delete(0, "end")

        altura_entry_tab3.delete(0, "end")
        altura_entry_tab3.focus()  # Foca em outro elemento para atualizar o placeholder

        largura_entry_tab3.delete(0, "end")
        largura_entry_tab3.focus()

        comprimento_entry_tab3.delete(0, "end")
        comprimento_entry_tab3.focus()

        espessura_entry_tab3.delete(0, "end")
        espessura_entry_tab3.focus()

        link_entry_tab3.delete(0, "end")
        link_entry_tab3.focus()

        descricao_compra_entry_tab3.focus()

        atualizar_lista_itens_tab3()

def atualizar_lista_itens_tab3():
    for widget in frame_lista_itens.winfo_children():
        widget.destroy()

    if len(servicos_tab3) > 0:
        frame_lista_itens.grid(row=11, column=0, columnspan=2, sticky="ew", padx=(10, 10), pady=5)
    else:
        frame_lista_itens.grid_forget()

    for index, (nome_item, quantidade, altura, largura, comprimento, espessura, link) in enumerate(servicos_tab3):
        row_frame = ctk.CTkFrame(frame_lista_itens, width=400)
        row_frame.grid(row=index, column=0, columnspan=2, sticky="ew", padx=10, pady=2)

        detalhes = f"Descrição: {nome_item}, Quantidade: {quantidade}"
        if altura:
            detalhes += f", Altura: {altura}"
        if largura:
            detalhes += f", Largura: {largura}"
        if comprimento:
            detalhes += f", Comprimento: {comprimento}"
        if espessura:
            detalhes += f", Espessura: {espessura}"
        if link:
            detalhes += f", Link: {link}"

        label_servico_gerado = ctk.CTkLabel(
            row_frame, 
            text=detalhes,
            anchor="w", justify="left", wraplength=340
        )
        label_servico_gerado.grid(row=0, column=0, padx=2)

        btn_editar = ctk.CTkButton(
            row_frame, text="Editar", width=30, 
            command=lambda i=index: editar_item_tab3(i)
        )
        btn_editar.grid(row=0, column=1, padx=2)

        btn_excluir = ctk.CTkButton(
            row_frame, text="❌", width=30, 
            fg_color="red", hover_color="darkred", 
            command=lambda i=index: remover_item_tab3(i)
        )
        btn_excluir.grid(row=0, column=2, padx=2)

# Função para editar um serviço
def editar_item_tab3(index):
    global editando_item
    editando_item = index  # Marca que o item está sendo editado

    servico_atual, quantidade_atual, altura_atual, largura_atual, \
    comprimento_atual, espessura_atual, link_atual = servicos_tab3[index]

    # Preenche os campos de entrada com os valores do item selecionado
    descricao_compra_entry_tab3.delete(0, "end")
    descricao_compra_entry_tab3.insert(0, servico_atual)

    quantidade_entry_tab3.delete(0, "end")
    quantidade_entry_tab3.insert(0, str(quantidade_atual))

    altura_entry_tab3.delete(0, "end")
    altura_entry_tab3.insert(0, altura_atual)
    altura_entry_tab3.focus()

    largura_entry_tab3.delete(0, "end")
    largura_entry_tab3.insert(0, largura_atual)
    largura_entry_tab3.focus()

    comprimento_entry_tab3.delete(0, "end")
    comprimento_entry_tab3.insert(0, comprimento_atual)
    comprimento_entry_tab3.focus()

    espessura_entry_tab3.delete(0, "end")
    espessura_entry_tab3.insert(0, espessura_atual)
    espessura_entry_tab3.focus()

    link_entry_tab3.delete(0, "end")
    link_entry_tab3.insert(0, link_atual)
    link_entry_tab3.focus()

    descricao_compra_entry_tab3.focus()

    btn_adicionar_servico.configure(text="Salvar", command=lambda: salvar_edicao(index))

    # Desabilita o botão de excluir
    atualizar_lista_itens_tab3()

# Função para salvar a edição
def salvar_edicao(index):
    global editando_item
    novo_servico = descricao_compra_entry_tab3.get().strip()
    nova_quantidade = quantidade_entry_tab3.get().strip()
    nova_altura = altura_entry_tab3.get().strip()
    nova_largura = largura_entry_tab3.get().strip()
    novo_comprimento = comprimento_entry_tab3.get().strip()
    nova_espessura = espessura_entry_tab3.get().strip()
    novo_link = link_entry_tab3.get().strip()

    if novo_servico and not nova_quantidade:
        notification_manager.show_notification(
            "Campo QUANTIDADE\nA quantidade não pode ser nula!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
        )
        return
    elif not novo_servico and nova_quantidade:
        notification_manager.show_notification(
            "Campo DESCRIÇÃO\nO campo deve ser preenchido!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
        )
        return
    elif not novo_servico and not nova_quantidade:
        notification_manager.show_notification(
            "Campos DESCRIÇÃO e QUANTIDADE\nOs campos devem ser preenchidos!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF"
        )
        return
    else:
        servicos_tab3[index] = (novo_servico, nova_quantidade, nova_altura, nova_largura, novo_comprimento, nova_espessura, novo_link)

        # Limpa os campos após a edição
        descricao_compra_entry_tab3.delete(0, "end")
        quantidade_entry_tab3.delete(0, "end")
        altura_entry_tab3.delete(0, "end")
        largura_entry_tab3.delete(0, "end")
        comprimento_entry_tab3.delete(0, "end")
        espessura_entry_tab3.delete(0, "end")
        link_entry_tab3.delete(0, "end")

        # Restaura o texto do botão para "Adicionar item"
        btn_adicionar_servico.configure(text="Adicionar item", command=adicionar_item_tab3)

        # Reabilita o botão de excluir
        editando_item = None  # Desmarca a edição

        descricao_compra_entry_tab3.focus()

        atualizar_lista_itens_tab3()

# Função para remover um serviço da lista
def remover_item_tab3(index):
    global editando_item
    if editando_item is None:  # Só permite excluir se não estiver editando
        del servicos_tab3[index]
        atualizar_lista_itens_tab3()
    else:
        notification_manager = NotificationManager(root)  # passando a instância da janela principal
        notification_manager.show_notification("Item em edição!\nSalve-o para habilitar a exclusão.", NotifyType.WARNING, bg_color="#404040", text_color="#FFFFFF")
        pass

def gerar_texto_aquisicao():
    # Coletar dados dos campos
    nome_usuario_tab3 = arrumar_texto(nome_usuario_entry_tab3.get().upper())
    tipo_aquisicao_tab3 = arrumar_texto(tipo_aquisicao_combobox_tab3.get().upper())
    contrato_tab3 = arrumar_texto(contrato_combobox_tab3.get().upper())
    descricao_tab3 = arrumar_texto(descricao_locacao_entry_tab3.get().upper())
    prazo_tab3 = arrumar_texto(prazo_entry_tab3.get_date().upper())
    data_tab3 = arrumar_texto(data_entry_tab3.get_date().upper())
    servico_tab3 = arrumar_texto(servico_entry_tab3.get().upper())
    periodo_locacao_tab3 = arrumar_texto(periodo_locacao_combobox_tab3.get().upper())
    quantidade_periodo_locacao_tab3 = arrumar_texto(quantidade_locacao_entry_tab3.get().upper())
    prefixo_tab3 = valida_prefixo(prefixo_entry_tab3.get())
    agencia_tab3 = arrumar_texto(agencia_entry_tab3.get().upper())
    os_num_tab3 = valida_os(os_entry_tab3.get())
    opcao_entrega_tab3 = arrumar_texto(opcao_entrega_combobox_tab3.get().upper())
    endereco_agencia_tab3 = arrumar_texto(endereco_agencia_entry_tab3.get().upper())
    local_retirada_tab3 = arrumar_texto(local_retirada_entry_tab3.get().upper())
    nome_responsavel_tab3 = arrumar_texto(nome_responsavel_entry_tab3.get().upper())
    contato_responsavel_tab3 = arrumar_texto(contato_responsavel_entry_tab3.get().upper())
    observacoes_tab3 = arrumar_texto(observacoes_entry_tab3.get().upper())

    # Verificar se algum campo obrigatório está vazio
    campos_obrigatorios = [
        (nome_usuario_tab3, "USUÁRIO"),
        (tipo_aquisicao_tab3, "TIPO DE SERVIÇO"),
        (contrato_tab3, "CONTRATO")
    ]

    if tipo_aquisicao_tab3 == "COMPRA":
        # Adiciona os campos comuns para os dois tipos
        campos_obrigatorios.extend([
            (servicos_tab3 if servicos_tab3 else None, "DESCRIÇÃO E QUANTIDADE"),
            (prazo_tab3, "PRAZO"),
            (opcao_entrega_tab3, "OPÇÃO DE ENTREGA"),
            (nome_responsavel_tab3, "NOME DO RESPONSÁVEL"),
            (contato_responsavel_tab3, "CONTATO DO RESPONSÁVEL")
        ])
        
        if opcao_entrega_tab3 == "ENTREGA":
            campos_obrigatorios.append((endereco_agencia_tab3, "ENDEREÇO"))

    elif tipo_aquisicao_tab3 == "LOCAÇÃO":
        # Adiciona os campos comuns para os dois tipos
        campos_obrigatorios.extend([
            (data_tab3, "DATA DA LOCAÇÃO"),
            (periodo_locacao_tab3, "PERÍODO DE LOCAÇÃO"),
            (quantidade_periodo_locacao_tab3, "QUANTIDADE DE PERÍODOS"),
            (prefixo_tab3, "PREFIXO"),
            (agencia_tab3, "AGÊNCIA"),
            (os_num_tab3, "OS"),
            (opcao_entrega_tab3, "OPÇÃO DE ENTREGA"),
            (nome_responsavel_tab3, "NOME DO RESPONSÁVEL"),
            (contato_responsavel_tab3, "CONTATO DO RESPONSÁVEL")
        ])
        
        if opcao_entrega_tab3 == "ENTREGA":
            campos_obrigatorios.append((endereco_agencia_tab3, "ENDEREÇO"))

    if contrato_tab3 == "ESCRITÓRIO":
        campos_obrigatorios = [
            item for item in campos_obrigatorios
            if item not in [(prefixo_tab3, "PREFIXO"), (agencia_tab3, "AGÊNCIA"), (os_num_tab3, "OS")]
        ]

    # Verificar campos vazios
    campos_vazios = [nome for valor, nome in campos_obrigatorios if not valor]

    if campos_vazios:
        if campos_vazios == ["DESCRIÇÃO E QUANTIDADE"]:
            notification_manager.show_notification("Item(ns) não adicionado(s)", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return
        else:
            notification_manager.show_notification("Preencha os campos obrigatórios em branco!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return

    if prefixo_tab3 == "Prefixo inválido":
        notification_manager.show_notification("Campo PREFIXO\nPrefixo inválido. Use o padrão XXXX/XX.", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return  

    if os_num_tab3 == "OS_invalida":
        notification_manager.show_notification("Campo OS\nPor favor, insira uma OS válida!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return

    if quantidade_periodo_locacao_tab3:
        if quantidade_periodo_locacao_tab3.isdigit():
            quantidade_periodo_locacao_tab3 = int(quantidade_periodo_locacao_tab3)

        if not isinstance(quantidade_periodo_locacao_tab3, int) or quantidade_periodo_locacao_tab3 < 1:
            notification_manager.show_notification("Campo QUANTIDADE DE PERÍODOS\nPor favor, insira um número válido!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return

    if tipo_aquisicao_tab3 == "COMPRA":
        texto = f"*SOLICITAÇÃO DE AQUISIÇÃO - {tipo_aquisicao_tab3}*\n\n"
        texto += f"▪ *Contrato:* {contrato_tab3}\n"
        texto += f"▪ *Prazo para aquisição:* {prazo_tab3}\n"

        if servicos_tab3:  # Verifica se a lista não está vazia
            if len(servicos_tab3) == 1:  # Apenas um item, mantém o formato original
                servico, quantidade, altura, largura, comprimento, espessura, link = servicos_tab3[0]
                texto += f"▪ *Descrição da aquisição:* {servico}\n"
                texto += f"▪ *Altura:* {altura}\n" if altura else ""
                texto += f"▪ *Largura:* {largura}\n" if largura else ""
                texto += f"▪ *Comprimento:* {comprimento}\n" if comprimento else ""
                texto += f"▪ *Espessura:* {espessura}\n" if espessura else ""
                texto += f"▪ *Quantidade:* {quantidade}\n"
                texto += f"▪ *Link:* {link}\n" if link else ""
            else:  # Mais de um item, gera uma lista formatada
                texto += "▪ *Itens da solicitação:*\n"
                for idx, (servico, quantidade, altura, largura, comprimento, espessura, link) in enumerate(servicos_tab3, start=1):
                    texto += f"   {idx}. {servico} - {quantidade} unidade(s)\n"
                    if altura:
                        texto += f"      - *Altura:* {altura}\n"
                    if largura:
                        texto += f"      - *Largura:* {largura}\n"
                    if comprimento:
                        texto += f"      - *Comprimento:* {comprimento}\n"
                    if espessura:
                        texto += f"      - *Espessura:* {espessura}\n"
                    if link:
                        texto += f"      - *Link:* {link}\n"

        texto += f"▪ *Prefixo, Agência e OS:* {prefixo_tab3} - {agencia_tab3} - {os_num_tab3}\n" if os_num_tab3 else ""
        
        if opcao_entrega_tab3 == "ENTREGA":
            texto += f"▪ *Entrega ou Retirada:* ENTREGA\n"
            texto += f"▪ *Endereço da Entrega:* {endereco_agencia_tab3}\n"
        else: 
            texto += "▪ *Entrega ou Retirada:* RETIRADA\n"

            if local_retirada_tab3:
                texto += f"▪ *Local de Retirada:* {local_retirada_tab3}\n"
                
        texto += f"▪ *Nome do responsável:* {nome_responsavel_tab3}\n"
        texto += f"▪ *Contato do responsável:* {contato_responsavel_tab3}\n"
        texto += f"▪ *Observações:* {observacoes_tab3}\n" if observacoes_tab3 else ""
    else:        
        texto = f"*SOLICITAÇÃO DE AQUISIÇÃO - {tipo_aquisicao_tab3}*\n\n"
        texto += f"▪ *Contrato:* {contrato_tab3}\n"
        texto += f"▪ *Descrição da locação:* {descricao_tab3}\n"
        texto += f"▪ *Data da locação:* {data_tab3}\n"
        texto += f"▪ *Serviço:* {servico_tab3}\n"
        
        if periodo_locacao_tab3 == "DIÁRIA":
            if quantidade_periodo_locacao_tab3 == 1:
                texto += f"▪ *Período da locação:* {quantidade_periodo_locacao_tab3} {periodo_locacao_tab3}\n"
            else:
                texto += f"▪ *Período da locação:* {quantidade_periodo_locacao_tab3} {periodo_locacao_tab3}S\n"
        elif periodo_locacao_tab3 == "SEMANAL":
            if quantidade_periodo_locacao_tab3 == 1:
                texto += f"▪ *Período da locação:* {quantidade_periodo_locacao_tab3} SEMANA\n"
            else:
                texto += f"▪ *Período da locação:* {quantidade_periodo_locacao_tab3} SEMANAS\n"
        elif periodo_locacao_tab3 == "QUINZENAL":
            if quantidade_periodo_locacao_tab3 == 1:
                texto += f"▪ *Período da locação:* {quantidade_periodo_locacao_tab3} QUINZENA\n"
            else:
                texto += f"▪ *Período da locação:* {quantidade_periodo_locacao_tab3} QUINZENAS\n"
        else:
            if quantidade_periodo_locacao_tab3 == 1:
                texto += f"▪ *Período da locação:* {quantidade_periodo_locacao_tab3} MÊS\n"
            else:
                texto += f"▪ *Período da locação:* {quantidade_periodo_locacao_tab3} MESES\n"
        
        texto += f"▪ *Prefixo, Agência e OS:* {prefixo_tab3} - {agencia_tab3} - {os_num_tab3}\n" if os_num_tab3 else f""
        
        if opcao_entrega_tab3 == "ENTREGA":
            texto += f"▪ *Entrega ou Retirada:* ENTREGA\n"
            texto += f"▪ *Endereço da Entrega:* {endereco_agencia_tab3}\n"
        else: 
            texto += "▪ *Entrega ou Retirada:* RETIRADA\n"

            if local_retirada_tab3:
                texto += f"▪ *Local de Retirada:* {local_retirada_tab3}\n"

        texto += f"▪ *Nome do responsável:* {nome_responsavel_tab3}\n"
        texto += f"▪ *Contato do responsável:* {contato_responsavel_tab3}\n"
        texto += f"▪ *Observações:* {observacoes_tab3}\n" if observacoes_tab3 else ""

    # Exibir texto na caixa de texto
    texto_aquisicao.delete(1.0, tk.END)
    texto_aquisicao.insert(tk.END, texto)

    # Copiar automaticamente o texto gerado caso o switch esteja ativo
    if switch_autocopia_frame_tab3_var.get():
        pyperclip.copy(texto)

# -------------------------------
# Fim das funções da aba "Aquisições"
# -------------------------------

def add_campos_tab2():
    tipo_servico_tab2 = tipo_servico_combobox_tab2.get()
 
    if tipo_servico_tab2 in {"COMPRAS EM GERAL - COM OS", "LOCAÇÃO"}:
        prefixo_label_tab2.grid(row=4, column=0, sticky="w", padx=(10, 10))
        prefixo_entry_tab2.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)
        agencia_label_tab2.grid(row=5, column=0, sticky="w", padx=(10, 10))
        agencia_entry_tab2.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)
        os_label_tab2.grid(row=6, column=0, sticky="w", padx=(10, 10))
        os_entry_tab2.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)
    else:
        oculta_campos = [
            prefixo_label_tab2, prefixo_entry_tab2,
            os_label_tab2, os_entry_tab2,
            agencia_label_tab2, agencia_entry_tab2
        ]

        for widget in oculta_campos:
            widget.grid_forget()

    if tipo_servico_tab2 == "LOCAÇÃO":
        endereco_agencia_label_tab2.grid(row=7, column=0, sticky="w", padx=(10, 10))
        endereco_entry_tab2.grid(row=7, column=1, sticky="ew", padx=(0, 10), pady=2)
    else:
        endereco_agencia_label_tab2.grid_forget()
        endereco_entry_tab2.grid_forget()        

def on_return_press(event):
    # Verifica qual aba está selecionada
    aba_atual = tabview.get()  # Retorna o nome da aba selecionada

    if aba_atual == "PAGAMENTO":
        gerar_button.invoke()
    elif aba_atual == "E-MAIL":
        gerar_button_tab2.invoke()
    elif aba_atual == "AQUISIÇÃO":
        gerar_button_tab3.invoke()

def restaurar_valores_tipo_aquisicao(event):
    """Se o usuário apagar manualmente, restaura os valores corretos"""
    tipo_atual = tipo_servico_combobox.get()

    # Define os valores corretos para cada tipo de serviço
    if tipo_atual == "AQUISIÇÃO COM OS":
        valores_corretos = ["CORRETIVA DIÁRIA", "LOCAÇÃO"]
    elif tipo_atual == "AQUISIÇÃO SEM OS":
        valores_corretos = ["EPI", "CRACHÁ", "FERRAMENTAS", "FARDAMENTO", "ESTOQUE", "UTILIDADES"]
    elif tipo_atual == "COMPRA IN LOCO":
        valores_corretos = ["CORRETIVA DIÁRIA", "ORÇAMENTO APROVADO"]
    else:
        valores_corretos = []

    # Obtém os valores atuais do combobox
    valores_atuais = tipo_aquisicao_combobox.cget("values")

    # Só atualiza o combobox se os valores estiverem errados ou o campo estiver vazio
    if set(valores_atuais) != set(valores_corretos):
        tipo_aquisicao_combobox.configure(values=valores_corretos)

    # Se o campo estiver vazio, restaura a seleção vazia
    if tipo_aquisicao_combobox.get() == "":
        tipo_aquisicao_combobox.set("")  # Mantém o campo vazio

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

    # Widgets da aba E-MAIL
    global nome_usuario_entry_tab2, tipo_servico_combobox_tab2, prefixo_entry_tab2, agencia_entry_tab2
    global os_entry_tab2, endereco_entry_tab2, nome_fornecedor_entry_tab2, valor_entry_tab2, num_orcamento_label_tab2
    global tipo_pagamento_combobox_tab2, num_orcamento_entry_tab2, texto_email, switch_autocopia_frame_tab2_var
    global prefixo_label_tab2, os_label_tab2, agencia_label_tab2, endereco_agencia_label_tab2, gerar_button_tab2

    # Widgets da aba AQUISIÇÃO
    global nome_usuario_entry_tab3, tipo_aquisicao_combobox_tab3, contrato_combobox_tab3
    global descricao_locacao_label_tab3, descricao_locacao_entry_tab3
    global descricao_compra_label_tab3, descricao_compra_entry_tab3, btn_adicionar_servico
    global prazo_entry_tab3, data_entry_tab3, servico_entry_tab3, espessura_entry_tab3
    global periodo_locacao_combobox_tab3, quantidade_entry_tab3, link_entry_tab3, prefixo_entry_tab3
    global agencia_entry_tab3, os_entry_tab3, opcao_entrega_combobox_tab3, endereco_agencia_entry_tab3
    global nome_responsavel_entry_tab3, contato_responsavel_entry_tab3, texto_aquisicao, switch_autocopia_frame_tab3_var
    global data_label_tab3, prazo_label_tab3, servico_label_tab3, periodo_locacao_label_tab3
    global espessura_label_tab3, quantidade_label_tab3, link_label_tab3, prefixo_label_tab3, os_label_tab3
    global agencia_label_tab3, opcao_entrega_label_tab3, nome_responsavel_label_tab3, contato_responsavel_agencia_label_tab3
    global altura_label_tab3, altura_entry_tab3, largura_label_tab3, largura_entry_tab3, comprimento_label_tab3, comprimento_entry_tab3
    global endereco_agencia_label_tab3, gerar_button_tab3, btn_adicionar_servico, servicos_tab3, frame_lista_itens
    global local_retirada_label_tab3, local_retirada_entry_tab3, observacoes_label_tab3, observacoes_entry_tab3
    global frame_caixa_itens, editando_item, quantidade_locacao_label_tab3, quantidade_locacao_entry_tab3

    # Configuração da interface gráfica
    root = ctk.CTk()
    root.title("Modelo Solicitação de Pagamento")
    root.geometry("650x600")
    ctk.set_default_color_theme("green")
    notification_manager = NotificationManager(root)  # passando a instância da janela principal

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

    # pegar todos os contratos do banco de dados
    contratos = acessa_bd_contratos()

    if "PAGAMENTO" in abas_permitidas:
        # -------------------------------
        # Aba "PAGAMENTO"
        # -------------------------------
        frame = ctk.CTkScrollableFrame(master=tabview.tab("PAGAMENTO"))
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Configurando a coluna do frame para expandir
        frame.grid_rowconfigure(4, weight=1)  # Expande a linha
        frame.grid_rowconfigure(18, weight=1)  # Expande a linha
        frame.grid_columnconfigure(0, weight=1)  # Expande a coluna 0
        frame.grid_columnconfigure(1, weight=1)  # Expande a coluna 1

        # Lista para armazenar os widgets que precisam ser limpos
        widgets_para_limpar = []
        widgets_para_limpar_tab2 = []
        widgets_para_limpar_tab3 = []

        usuarios_gerais = acessa_bd_usuarios()

        usuarios_varios_departamentos = ["AMANDA SAMPAIO",
            "DAWISON NASCIMENTO",
            "JOÃO GABRIEL",
            "TÁCIO BARBOSA",
            "TAIANE MARQUES"
        ]

        # Campos de entrada
        ctk.CTkLabel(master=frame, text="USUÁRIO:").grid(row=0, column=0, sticky="w", padx=(10, 10), pady=(10, 0))
        nome_usuario_entry = CustomEntry(master=frame)
        nome_usuario_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(10, 2))
        nome_usuario_entry.insert(0, nome_completo_usuario)
        nome_usuario_entry.configure(state='disabled')

        ctk.CTkLabel(master=frame, text="TIPO DE SERVIÇO:").grid(row=1, column=0, sticky="w", padx=(10, 10))
        tipo_servico_combobox = CustomComboBox(master=frame, values=[
            "ABASTECIMENTO",
            "ADIANTAMENTO/PAGAMENTO PARCEIRO",
            "AQUISIÇÃO COM OS",
            "AQUISIÇÃO SEM OS",
            "CARRETO",
            "COMPRA IN LOCO",
            "ENVIO DE MATERIAL",
            "ESTACIONAMENTO",
            "HOSPEDAGEM",
            "ORÇAMENTO APROVADO",
            "PREST. SERVIÇO/MÃO DE OBRA",
            "REEMBOLSO COM OS",
            "REEMBOLSO SEM OS",
            "REEMBOLSO UBER",
            "RELATÓRIO EXTRA",
            "SOLICITAÇÃO COM OS",
            "SOLICITAÇÃO SEM OS",
            "TRANSPORTADORA"
        ], command=lambda choice: add_campos())
        tipo_servico_combobox.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=2)

        contrato_label = ctk.CTkLabel(master=frame, text="CONTRATO:")#.grid(row=6, column=0, sticky="w", padx=(10, 10))
        '''Label e Combobox de Contrato apenas aparecem após a seleção do tipo_serviço.
        Iniciado combobox sem valor, já que, ao selecionar determinado tipo_serviço, o Contrato mostra valores específicos
        '''
        contrato_combobox = CustomComboBox(master=frame, values=[])
        #contrato_combobox.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)
        #contrato_combobox.set("")

        opcao_os_parceiro_label = ctk.CTkLabel(master=frame, text="POSSUI OS?")
        opcao_os_parceiro_combobox = CustomComboBox(master=frame, values=["SIM", "NÃO"], command=lambda choice: atualizar_exibicao_frame_caixa_itens())

        # -------------------------------
        # Frame para os itens
        # -------------------------------
        frame_caixa_itens_pagamento = ctk.CTkFrame(master=frame, border_width=1)
        
        frame_caixa_itens_pagamento.grid_columnconfigure(0, weight=1)
        frame_caixa_itens_pagamento.grid_columnconfigure(1, weight=1)
        
        frame_lista_itens_pagamento = ctk.CTkFrame(master=frame_caixa_itens_pagamento)

        # Variável para controlar se um item está sendo editado
        editando_item_pagamento = None

        descricao_do_item_pagamento_label = ctk.CTkLabel(master=frame_caixa_itens_pagamento, text="DESCRIÇÃO DO ITEM: ")
        descricao_do_item_pagamento_entry = CustomEntry(master=frame_caixa_itens_pagamento)

        # Campo para SAÍDA X DESTINO (UBER)
        saida_destino_label = ctk.CTkLabel(master=frame_caixa_itens_pagamento)
        saida_destino_entry = CustomEntry(master=frame_caixa_itens_pagamento)

        # Campo para MOTIVO
        motivo_label = ctk.CTkLabel(master=frame_caixa_itens_pagamento)
        motivo_entry = CustomEntry(master=frame_caixa_itens_pagamento)

        # Campo para valor
        valor_caixa_itens_label = ctk.CTkLabel(master=frame_caixa_itens_pagamento)
        valor_caixa_itens_entry = CustomEntry(master=frame_caixa_itens_pagamento)

        # Botão para adicionar serviço
        btn_adicionar_servico_pagamento = ctk.CTkButton(master=frame_caixa_itens_pagamento, text="Adicionar item", command=add_item_pagamento)
        btn_adicionar_servico_pagamento.grid(row=10, column=1, sticky="ew", padx=(0, 10), pady=5)
        # -------------------------------
        # Fim do frame para os itens
        # -------------------------------

        tipo_aquisicao_label = ctk.CTkLabel(master=frame, text="TIPO DE AQUISIÇÃO:")
        tipo_aquisicao_combobox = CustomComboBox(master=frame, command=lambda choice: campo_descricao_utilidades())
        tipo_aquisicao_combobox.set("")
        widgets_para_limpar.append(tipo_aquisicao_combobox)
        # Associa a função ao evento de exclusão manual (quando o campo perde o foco ou quando uma tecla é liberada)
        tipo_aquisicao_combobox.bind("<FocusOut>", restaurar_valores_tipo_aquisicao)  # Quando o campo perde o foco
        tipo_aquisicao_combobox.bind("<KeyRelease>", restaurar_valores_tipo_aquisicao)  # Quando o usuário digita algo

        descricao_utilidades_label = ctk.CTkLabel(master=frame, text="DESCRIÇÃO DA SOLICITAÇÃO:")
        descricao_utilidades_entry = CustomEntry(master=frame)
        widgets_para_limpar.append(descricao_utilidades_entry)

        tecnicos_label = ctk.CTkLabel(master=frame, text="TÉCNICOS:")
        tecnicos_entry = CustomEntry(master=frame)
        widgets_para_limpar.append(tecnicos_entry)

        prefixo_label = ctk.CTkLabel(master=frame)
        prefixo_entry = CustomEntry(master=frame)
        widgets_para_limpar.append(prefixo_entry)

        agencia_label = ctk.CTkLabel(master=frame)
        agencia_entry = CustomEntry(master=frame)
        widgets_para_limpar.append(agencia_entry)

        os_label = ctk.CTkLabel(master=frame)
        os_entry = CustomEntry(master=frame)
        widgets_para_limpar.append(os_entry)

        ctk.CTkLabel(master=frame, text="NOME FORNEC./BENEF.:").grid(row=8, column=0, sticky="w", padx=(10, 10))
        nome_fornecedor_entry = CustomEntry(master=frame)
        nome_fornecedor_entry.grid(row=8, column=1, sticky="ew", padx=(0, 10), pady=2)
        widgets_para_limpar.append(nome_fornecedor_entry)

        valor_label = ctk.CTkLabel(master=frame, text="VALOR:")
        valor_entry = CustomEntry(master=frame)
        widgets_para_limpar.append(valor_entry)

        ano_atual = datetime.now().strftime("%Y")

        competencia_label = ctk.CTkLabel(master=frame, text="COMPETÊNCIA:")
        competencia_combobox = CustomComboBox(master=frame, values=[f"JAN/{ano_atual}", f"FEV/{ano_atual}", f"MAR/{ano_atual}", 
                                                                f"ABR/{ano_atual}", f"MAI/{ano_atual}", f"JUN/{ano_atual}", 
                                                                f"JUL/{ano_atual}", f"AGO/{ano_atual}", f"SET/{ano_atual}",
                                                                f"OUT/{ano_atual}", f"NOV/{ano_atual}", f"DEZ/{ano_atual}"])
        widgets_para_limpar.append(competencia_combobox)

        porcentagem_label = ctk.CTkLabel(master=frame, text="% DO ADIANTAMENTO \nDO PARCEIRO:")
        porcentagem_entry = CustomEntry(master=frame)
        widgets_para_limpar.append(porcentagem_entry)

        ctk.CTkLabel(master=frame, text="TIPO DE PAGAMENTO:").grid(row=12, column=0, sticky="w", padx=(10, 10))
        tipo_pagamento_combobox = CustomComboBox(master=frame, values=[
            "PIX", "VEXPENSES"
        ], command=lambda choice: adiciona_campo_pix())
        tipo_pagamento_combobox.grid(row=12, column=1, sticky="ew", padx=(0, 10), pady=2)
        tipo_pagamento_combobox.set("")

        tipo_chave_pix_label = ctk.CTkLabel(master=frame, text="TIPO DA CHAVE PIX:")
        tipo_chave_pix_combobox = CustomComboBox(master=frame, values=["CHAVE ALEATÓRIA", "CNPJ", "COPIA E COLA", "CPF", "E-MAIL", "QR CODE", "TELEFONE"],
            command=lambda choice: esconde_campos_pagamento_qrcode())
        tipo_chave_pix_combobox.set("")
        widgets_para_limpar.append(tipo_chave_pix_combobox)

        chave_pix_label = ctk.CTkLabel(master=frame, text="CHAVE PIX:")
        chave_pix_entry = CustomEntry(master=frame)
        widgets_para_limpar.append(chave_pix_entry)

        nome_benef_pix_label = ctk.CTkLabel(master=frame, text="NOME DO BENEF. DO PIX:")
        nome_benef_pix_entry = CustomEntry(master=frame, placeholder_text="Opcional")
        widgets_para_limpar.append(nome_benef_pix_entry)

        # Botão GERAR
        gerar_button = ctk.CTkButton(master=frame, text="GERAR", command=gerar_solicitacao)
        gerar_button.grid(row=16, column=0, sticky="ew", padx=(10, 10), pady=10)

        root.bind("<Return>", on_return_press)

        limpar_button = ctk.CTkButton(master=frame, text="LIMPAR", width=150, command=limpar_dados)
        limpar_button.grid(row=16, column=1, sticky="ew", padx=(0, 10), pady=10)

        switch_autocopia_var = tk.BooleanVar(value=True)
        switch_autocopia = ctk.CTkSwitch(master=frame, text="Auto-Cópia",
                                        variable=switch_autocopia_var, onvalue=True, offvalue=False)
        switch_autocopia.grid(row=17, column=0, sticky="n", padx=(0, 10), pady=10)

        switch_gerar_excel_var = tk.BooleanVar(value=True)
        switch_gerar_excel = ctk.CTkSwitch(master=frame, text="Gerar Excel",
                                        variable=switch_gerar_excel_var, onvalue=True, offvalue=False)
        switch_gerar_excel.grid(row=17, column=1, sticky="n", padx=(0, 10), pady=10)

        # Caixa de texto para a solicitação
        texto_solicitacao = ctk.CTkTextbox(master=frame)
        texto_solicitacao.grid(row=18, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")
        widgets_para_limpar.append(texto_solicitacao)

    if "E-MAIL" in abas_permitidas:
        # -------------------------------
        # Aba "E-MAIL"
        # -------------------------------
        frame_tab2 = ctk.CTkScrollableFrame(master=tabview.tab("E-MAIL"))
        frame_tab2.pack(fill="both", expand=True, padx=2, pady=2)

        # Configurando a coluna do frame para expandir
        frame_tab2.grid_rowconfigure(14, weight=1)  # Expande a linha
        frame_tab2.grid_columnconfigure(0, weight=1)  # Expande a coluna 0
        frame_tab2.grid_columnconfigure(1, weight=1)  # Expande a coluna 1

        # Campos de entrada
        ctk.CTkLabel(master=frame_tab2, text="USUÁRIO:").grid(row=0, column=0, sticky="w", padx=(10, 10), pady=(10, 0))
        nome_usuario_entry_tab2 = CustomEntry(master=frame_tab2)
        nome_usuario_entry_tab2.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(10, 2))
        nome_usuario_entry_tab2.insert(0, nome_completo_usuario)
        nome_usuario_entry_tab2.configure(state='disabled')

        ctk.CTkLabel(master=frame_tab2, text="TIPO DE SERVIÇO:").grid(row=1, column=0, sticky="w", padx=(10, 10))
        tipo_servico_combobox_tab2 = CustomComboBox(master=frame_tab2, values=[
            "COMPRAS EM GERAL - COM OS",
            "COMPRAS EM GERAL - SEM OS",
            "LOCAÇÃO",
        ], command=lambda choice: add_campos_tab2())
        tipo_servico_combobox_tab2.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=2)
        tipo_servico_combobox_tab2.set("")

        prefixo_label_tab2 = ctk.CTkLabel(master=frame_tab2, text="PREFIXO:")
        prefixo_entry_tab2 = CustomEntry(master=frame_tab2)
        widgets_para_limpar_tab2.append(prefixo_entry_tab2)

        agencia_label_tab2 = ctk.CTkLabel(master=frame_tab2, text="AGÊNCIA:")
        agencia_entry_tab2 = CustomEntry(master=frame_tab2)
        widgets_para_limpar_tab2.append(agencia_entry_tab2)

        os_label_tab2 = ctk.CTkLabel(master=frame_tab2, text="OS:")
        os_entry_tab2 = CustomEntry(master=frame_tab2)
        widgets_para_limpar_tab2.append(os_entry_tab2)

        endereco_agencia_label_tab2 = ctk.CTkLabel(master=frame_tab2, text="ENDEREÇO DE ENTREGA:")
        endereco_entry_tab2 = CustomEntry(master=frame_tab2)
        widgets_para_limpar_tab2.append(endereco_entry_tab2)

        ctk.CTkLabel(master=frame_tab2, text="NOME FORNEC./BENEF.:").grid(row=8, column=0, sticky="w", padx=(10, 10))
        nome_fornecedor_entry_tab2 = CustomEntry(master=frame_tab2)
        nome_fornecedor_entry_tab2.grid(row=8, column=1, sticky="ew", padx=(0, 10), pady=2)
        widgets_para_limpar_tab2.append(nome_fornecedor_entry_tab2)

        ctk.CTkLabel(master=frame_tab2, text="VALOR:").grid(row=9, column=0, sticky="w", padx=(10, 10))
        valor_entry_tab2 = CustomEntry(master=frame_tab2)
        valor_entry_tab2.grid(row=9, column=1, sticky="ew", padx=(0, 10), pady=2)
        widgets_para_limpar_tab2.append(valor_entry_tab2)

        ctk.CTkLabel(master=frame_tab2, text="TIPO DE PAGAMENTO:").grid(row=10, column=0, sticky="w", padx=(10, 10))
        tipo_pagamento_combobox_tab2 = CustomComboBox(master=frame_tab2, values=[
            "FATURAMENTO", "PIX", "VEXPENSES"
        ], command=lambda choice: adiciona_campo_pix())
        tipo_pagamento_combobox_tab2.grid(row=10, column=1, sticky="ew", padx=(0, 10), pady=2)
        tipo_pagamento_combobox_tab2.set("")
        widgets_para_limpar_tab2.append(tipo_pagamento_combobox_tab2)

        num_orcamento_label_tab2 = ctk.CTkLabel(master=frame_tab2, text="Nº ORÇAM./PEDIDO (SE APLICÁVEL):").grid(row=11, column=0, sticky="w", padx=(10, 10))
        num_orcamento_entry_tab2 = CustomEntry(master=frame_tab2, placeholder_text="Opcional")
        num_orcamento_entry_tab2.grid(row=11, column=1, sticky="ew", padx=(0, 10), pady=2)
        widgets_para_limpar_tab2.append(num_orcamento_entry_tab2)

        gerar_button_tab2 = ctk.CTkButton(master=frame_tab2, text="GERAR", command=gerar_texto_email)
        gerar_button_tab2.grid(row=12, column=0, sticky="ew", padx=(10, 10), pady=10)

        limpar_button_tab2 = ctk.CTkButton(master=frame_tab2, text="LIMPAR", width=150, command=limpar_dados)
        limpar_button_tab2.grid(row=12, column=1, sticky="ew", padx=(0, 10), pady=10)

        root.bind("<Return>", on_return_press)

        switch_autocopia_frame_tab2_var = tk.BooleanVar(value=True)
        switch_autocopia_frame_tab2 = ctk.CTkSwitch(master=frame_tab2, text="Auto-Cópia",
                                        variable=switch_autocopia_frame_tab2_var, onvalue=True, offvalue=False)
        switch_autocopia_frame_tab2.grid(row=13, column=0, columnspan=2, sticky="n", padx=10, pady=10)

        # Caixa de texto para a solicitação
        texto_email = ctk.CTkTextbox(master=frame_tab2)
        texto_email.grid(row=14, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")
        widgets_para_limpar_tab2.append(texto_email)

    if "AQUISIÇÃO" in abas_permitidas:
        # -------------------------------
        # Aba "AQUISIÇÃO"
        # -------------------------------
        frame_tab3 = ctk.CTkScrollableFrame(master=tabview.tab("AQUISIÇÃO"))
        frame_tab3.pack(fill="both", expand=True, padx=2, pady=2)

        # Configurando a coluna do frame para expandir
        frame_tab3.grid_rowconfigure(20, weight=1)  # Expande a linha
        frame_tab3.grid_rowconfigure(3, weight=1)  # Expande a linha
        frame_tab3.grid_columnconfigure(0, weight=1)  # Expande a coluna 0
        frame_tab3.grid_columnconfigure(1, weight=1)  # Expande a coluna 1

        ctk.CTkLabel(master=frame_tab3, text="USUÁRIO:").grid(row=0, column=0, sticky="w", padx=(10, 10), pady=(10, 0))
        nome_usuario_entry_tab3 = CustomEntry(master=frame_tab3)
        nome_usuario_entry_tab3.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=(10, 2))
        nome_usuario_entry_tab3.insert(0, nome_completo_usuario)
        nome_usuario_entry_tab3.configure(state='disabled')

        ctk.CTkLabel(master=frame_tab3, text="TIPO:").grid(row=1, column=0, sticky="w", padx=(10, 10))
        tipo_aquisicao_combobox_tab3 = CustomComboBox(master=frame_tab3, values=[
            "COMPRA",
            "LOCAÇÃO",
        ], command=lambda choice: add_campos_tab3())
        tipo_aquisicao_combobox_tab3.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=2)
        tipo_aquisicao_combobox_tab3.set("")

        ctk.CTkLabel(master=frame_tab3, text="CONTRATO:").grid(row=2, column=0, sticky="w", padx=(10, 10))
        contrato_combobox_tab3 = CustomComboBox(master=frame_tab3, values=[
            "ESCRITÓRIO", "C. O. BELO HORIZONTE - MG - 2054", "C. O. MANAUS - AM - 7649", "C. O. NITERÓI - RJ - 1380", 
            "C. O. RECIFE - PE - 5254", "C. O. RIO DE JANEIRO - RJ - 0494", "C. O. RIO GRANDE DO SUL - RS - 5525", 
            "C. O. RONDÔNIA - RD - S/N", "C. O. SALVADOR - BA - 2877", "C. O. SANTA CATARINA - SC - 5023", 
            "C. O. VOLTA REDONDA - RJ - 0215", "ATA BB CURITIBA - 0232", "C. E. MANAUS - 1593", "CAIXA BAHIA - 4922.2024",
            "CAIXA CURITIBA - 534.2025", "CAIXA MANAUS - 4569.2024", "INFRA CURITIBA - 1120"
        ], command=lambda choice: add_campos_tab3())
        contrato_combobox_tab3.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=2)
        contrato_combobox_tab3.set("")

        # Criando os campos de entrada
        descricao_locacao_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="DESCRIÇÃO:")
        descricao_locacao_entry_tab3 = CustomEntry(master=frame_tab3)

        # -------------------------------
        # Frame para os itens
        # -------------------------------
        frame_caixa_itens = ctk.CTkFrame(master=frame_tab3, border_width=1)

        frame_caixa_itens.grid_columnconfigure(0, weight=1)
        frame_caixa_itens.grid_columnconfigure(1, weight=1)
        
        # Inicializando o frame antes de manipulá-lo
        frame_lista_itens = ctk.CTkFrame(master=frame_caixa_itens)

        # Variável para controlar se um item está sendo editado
        editando_item = None  # Inicializa como None (nenhum item está sendo editado)

        # Criando os campos de entrada
        descricao_compra_label_tab3 = ctk.CTkLabel(master=frame_caixa_itens, text="DESCRIÇÃO DO ITEM:")
        descricao_compra_entry_tab3 = CustomEntry(master=frame_caixa_itens)
        descricao_compra_label_tab3.grid(row=3, column=0, sticky="w", padx=(10, 10))
        descricao_compra_entry_tab3.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=2)

        quantidade_label_tab3 = ctk.CTkLabel(master=frame_caixa_itens, text="QUANTIDADE:")
        quantidade_entry_tab3 = CustomEntry(master=frame_caixa_itens)
        quantidade_label_tab3.grid(row=4, column=0, sticky="w", padx=(10, 10))
        quantidade_entry_tab3.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)

        altura_label_tab3 = ctk.CTkLabel(master=frame_caixa_itens, text=f"ALTURA:", anchor="w", justify="left")
        altura_entry_tab3 = CustomEntry(master=frame_caixa_itens, placeholder_text="Opcional")
        altura_label_tab3.grid(row=5, column=0, sticky="w", padx=(10, 10))
        altura_entry_tab3.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)

        largura_label_tab3 = ctk.CTkLabel(master=frame_caixa_itens, text=f"LARGURA:", anchor="w", justify="left")
        largura_entry_tab3 = CustomEntry(master=frame_caixa_itens, placeholder_text="Opcional")
        largura_label_tab3.grid(row=6, column=0, sticky="w", padx=(10, 10))
        largura_entry_tab3.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)

        comprimento_label_tab3 = ctk.CTkLabel(master=frame_caixa_itens, text=f"COMPRIMENTO:                ", anchor="w", justify="left")
        comprimento_entry_tab3 = CustomEntry(master=frame_caixa_itens, placeholder_text="Opcional")
        comprimento_label_tab3.grid(row=7, column=0, sticky="w", padx=(10, 10))
        comprimento_entry_tab3.grid(row=7, column=1, sticky="ew", padx=(0, 10), pady=2)

        espessura_label_tab3 = ctk.CTkLabel(master=frame_caixa_itens, text="ESPESSURA:")
        espessura_entry_tab3 = CustomEntry(master=frame_caixa_itens, placeholder_text="Opcional")
        espessura_label_tab3.grid(row=8, column=0, sticky="w", padx=(10, 10))
        espessura_entry_tab3.grid(row=8, column=1, sticky="ew", padx=(0, 10), pady=2)

        link_label_tab3 = ctk.CTkLabel(master=frame_caixa_itens, text="LINK:")
        link_entry_tab3 = CustomEntry(master=frame_caixa_itens, placeholder_text="Opcional")
        link_label_tab3.grid(row=9, column=0, sticky="w", padx=(10, 10))
        link_entry_tab3.grid(row=9, column=1, sticky="ew", padx=(0, 10), pady=2) 

        # Botão para adicionar serviço
        btn_adicionar_servico = ctk.CTkButton(master=frame_caixa_itens, text="Adicionar item", command=adicionar_item_tab3)
        # -------------------------------
        # Fim do frame para os itens
        # -------------------------------

        data_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="DATA DA LOCAÇÃO:")
        data_entry_tab3 = CTkDatePicker(master=frame_tab3)
        data_entry_tab3.set_date_format("%d/%m/%Y")
        data_entry_tab3.set_allow_manual_input(False)
        widgets_para_limpar_tab3.append(data_entry_tab3)

        #row = 5
        prazo_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="PRAZO:")
        prazo_entry_tab3 = CTkDatePicker(master=frame_tab3)
        prazo_entry_tab3.set_date_format("%d/%m/%Y")
        prazo_entry_tab3.set_allow_manual_input(False)
        widgets_para_limpar_tab3.append(prazo_entry_tab3)

        servico_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="SERVIÇO:")
        servico_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(servico_entry_tab3)

        #row = 6
        periodo_locacao_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="PERÍODO DE LOCAÇÃO:")
        periodo_locacao_combobox_tab3 = CustomComboBox(master=frame_tab3, values=[
            "DIÁRIA", "SEMANAL", "QUINZENAL", "MENSAL"
        ])
        periodo_locacao_combobox_tab3.set("")
        widgets_para_limpar_tab3.append(periodo_locacao_combobox_tab3)

        #row = 7
        quantidade_locacao_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="QUANTIDADE DE PERÍODOS:")
        quantidade_locacao_entry_tab3 = CustomEntry(master=frame_tab3, placeholder_text="Apenas números")
        widgets_para_limpar_tab3.append(quantidade_locacao_label_tab3)

        #row = 8

        #row = 9

        #row = 10

        #row = 11
        prefixo_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="PREFIXO:")
        prefixo_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(prefixo_entry_tab3)

        #row = 12
        agencia_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="AGÊNCIA:")
        agencia_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(agencia_entry_tab3)

        #row = 13
        os_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="OS:")
        os_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(os_entry_tab3)

        opcao_entrega_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="OPÇÃO DE ENTREGA:")
        opcao_entrega_combobox_tab3 = CustomComboBox(master=frame_tab3, values=[
            "ENTREGA",
            "RETIRADA",
        ], command=lambda choice: add_campos_tab3())
        opcao_entrega_combobox_tab3.set("")
        widgets_para_limpar_tab3.append(opcao_entrega_combobox_tab3)

        #row = 14
        endereco_agencia_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="ENDEREÇO DE ENTREGA:")
        endereco_agencia_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(endereco_agencia_entry_tab3)

        local_retirada_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="LOCAL DE RETIRADA:")
        local_retirada_entry_tab3 = CustomEntry(master=frame_tab3, placeholder_text="Opcional")
        widgets_para_limpar_tab3.append(local_retirada_entry_tab3)

        #row = 15
        nome_responsavel_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="NOME DO RESPONSÁVEL:")
        nome_responsavel_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(nome_responsavel_entry_tab3)

        #row = 16
        contato_responsavel_agencia_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="CONTATO DO RESPONSÁVEL:")
        contato_responsavel_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(contato_responsavel_entry_tab3)

        observacoes_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="OBSERVAÇÕES:")
        observacoes_entry_tab3 = CustomEntry(master=frame_tab3, placeholder_text="Opcional")
        widgets_para_limpar_tab3.append(observacoes_entry_tab3)
        
        #row = 17
        gerar_button_tab3 = ctk.CTkButton(master=frame_tab3, text="GERAR", command=gerar_texto_aquisicao)
        gerar_button_tab3.grid(row=21, column=0, sticky="ew", padx=(10, 10), pady=10)

        root.bind("<Return>", on_return_press)

        limpar_button_tab3 = ctk.CTkButton(master=frame_tab3, text="LIMPAR", width=150, command=limpar_dados)
        limpar_button_tab3.grid(row=21, column=1, sticky="ew", padx=(0, 10), pady=10)

        #row = 18
        switch_autocopia_frame_tab3_var = tk.BooleanVar(value=True)
        switch_autocopia_frame_tab3 = ctk.CTkSwitch(master=frame_tab3, text="Auto-Cópia",
                                        variable=switch_autocopia_frame_tab3_var, onvalue=True, offvalue=False)
        switch_autocopia_frame_tab3.grid(row=22, column=0, columnspan=2, sticky="n", padx=10, pady=10)

        #row = 19
        texto_aquisicao = ctk.CTkTextbox(master=frame_tab3)
        texto_aquisicao.grid(row=23, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")
        widgets_para_limpar_tab3.append(texto_aquisicao)

    root.mainloop()
