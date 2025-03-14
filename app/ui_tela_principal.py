import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from .utils import arrumar_texto, verificar_se_numero, valida_porcentagem, valida_os
from .gerador_excel import gerar_excel
from .CTkDatePicker import *
from .CTkFloatingNotifications import *
import pyperclip
import re
from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')

# Criar uma classe personalizada para o ComboBox
class CustomComboBox(ctk.CTkComboBox):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            border_width=1,
            corner_radius=1,
            state="readonly",
            **kwargs  
        )

# Criar uma classe personalizada para Entry
class CustomEntry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            border_width=1,
            corner_radius=1,
            **kwargs
        )

def gerar_solicitacao():
    # Coletar dados dos campos
    nome_usuario = arrumar_texto(nome_usuario_entry.get().upper())
    tipo_servico = arrumar_texto(tipo_servico_combobox.get().upper())
    nome_fornecedor = arrumar_texto(nome_fornecedor_entry.get().upper())
    prefixo = arrumar_texto(prefixo_entry.get())
    agencia = arrumar_texto(agencia_entry.get().upper())
    os_num = valida_os(os_entry.get())
    contrato = arrumar_texto(contrato_combobox.get().upper())
    motivo = arrumar_texto(motivo_entry.get().upper())
    valor_tab1 = verificar_se_numero(valor_entry.get())
    tipo_pagamento = arrumar_texto(tipo_pagamento_combobox.get().upper())
    tecnicos = arrumar_texto(tecnicos_entry.get().upper())
    saida_destino = arrumar_texto(saida_destino_entry.get().upper())
    competencia = arrumar_texto(competencia_combobox.get().upper())
    porcentagem = valida_porcentagem(porcentagem_entry.get().upper())
    tipo_aquisicao = arrumar_texto(tipo_aquisicao_combobox.get().upper())

    if tipo_pagamento == "PIX":
        tipo_chave_pix = arrumar_texto(tipo_chave_pix_combobox.get())
        chave_pix = arrumar_texto(chave_pix_entry.get())
        nome_benef_pix = arrumar_texto(nome_benef_pix_entry.get().upper())

    # Facilitar a identificação do erro pelo nome de usuário
    # logging.info(f"Aplicação iniciada. User: {nome_usuario}")

    # Dicionário que mapeia contratos para departamentos
    contrato_departamentos = {
        "ESCRITÓRIO": "ESCRITÓRIO",
        "C. O. SALVADOR - BA - 2877": "CONTRATO BA",
        "C. O. SANTA CATARINA - SC - 5023": "CONTRATO SC",
        "C. O. RIO GRANDE DO SUL - RS - 5525": "CONTRATO RS",
        "C. O. RIO DE JANEIRO - RJ - 0494": "CONTRATO RJ",
        "C. O. NITERÓI - RJ - 1380": "CONTRATO NT",
        "C. O. BELO HORIZONTE - MG - 2054": "CONTRATO MG",
        "C. O. RECIFE - PE - 5254": "CONTRATO PE",
        "C. O. VOLTA REDONDA - RJ - 0215": "CONTRATO VOLTA REDONDA",
        "C. O. RONDÔNIA - RD - S/N": "CONTRATO RONDÔNIA",
        "C. O. MANAUS - AM - 7649": "CONTRATO AM"
    } 
    
    departamento = contrato_departamentos.get(contrato, "")

    dict_sigla_contrato = {
        "ESCRITÓRIO": "ESCRITÓRIO",
        "": "ESCRITÓRIO",
        "C. O. SALVADOR - BA - 2877": "SSA",
        "C. O. SANTA CATARINA - SC - 5023": "SC",
        "C. O. RIO GRANDE DO SUL - RS - 5525": "RS",
        "C. O. RIO DE JANEIRO - RJ - 0494": "RJ",
        "C. O. NITERÓI - RJ - 1380": "NIT",
        "C. O. BELO HORIZONTE - BH - 2054": "BH",
        "C. O. RECIFE - PE - 5254": "PE",
        "C. O. MANAUS - AM - 7649": "AM",
        "C. O. VOLTA REDONDA - RJ - 0215": "VR",
        "C. O. RONDÔNIA - RD - 0710": "RO",
        "ATA BB CURITIBA - 0232": "ATA PR",
        "C. E. MANAUS - S/N": "BB AM",
        "CAIXA BAHIA - 4922.2024": "CAIXA BA",
        "CAIXA CURITIBA - 534.2025": "CAIXA PR",
        "CAIXA MANAUS - 4569.2024": "CAIXA AM",
        "INFRA CURITIBA - S/N": "INFRA PR"
    }

    sigla_contrato = dict_sigla_contrato.get(contrato, "Sigla não encontrada")

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
    elif tipo_servico == "ADIANTAMENTO PARCEIRO":
        campos_obrigatorios.extend([
            (prefixo, "PREFIXO"),
            (agencia, "AGÊNCIA"),
            (os_num, "OS"),
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
    elif tipo_servico == "ENVIO DE MATERIAL":
        campos_obrigatorios.remove((contrato, "CONTRATO"))
    elif tipo_servico in {"ESTACIONAMENTO", "HOSPEDAGEM"}:
        campos_obrigatorios.extend([
            (tecnicos, "TÉCNICOS"),
            (prefixo, "PREFIXO"),
            (agencia, "AGÊNCIA"),
            (os_num, "OS")
        ])        
    elif tipo_servico == "REEMBOLSO COM OS" or tipo_servico == "SOLICITAÇÃO COM OS":
        campos_obrigatorios.extend([
            (motivo, "MOTIVO"),
            (prefixo, "PREFIXO"),
            (agencia, "AGÊNCIA"),
            (os_num, "OS")
        ])
    elif tipo_servico == "REEMBOLSO SEM OS" or tipo_servico == "SOLICITAÇÃO SEM OS":
        campos_obrigatorios.append((motivo, "MOTIVO"))
    elif tipo_servico == "REEMBOLSO UBER":
        campos_obrigatorios.extend([
            (saida_destino, "SAÍDA X DESTINO"),
            (motivo, "MOTIVO")
        ])
    elif tipo_servico in {"CARRETO", "ORÇAMENTO APROVADO", "PREST. SERVIÇO/MÃO DE OBRA", "TRANSPORTADORA"}:
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
            if item not in {(prefixo, "PREFIXO"), (agencia, "AGÊNCIA"), (os_num, "OS")}
        ]

    # Verificar campos vazios
    campos_vazios = [nome for valor, nome in campos_obrigatorios if not valor]

    notification_manager = NotificationManager(root)  # passando a instância da janela principal
    if os_num == "OS_invalida":
        notification_manager.show_notification("Campo OS\nPor favor, insira uma OS válida!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return
    
    if valor_tab1 == ValueError:
        notification_manager.show_notification("Campo VALOR\nPor favor, insira um número válido!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return
    
    if porcentagem == ValueError:
        notification_manager.show_notification("Campo PORCENTAGEM\nPor favor, insira um número válido!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return
    elif porcentagem == "RangeError":
        notification_manager.show_notification("Campo PORCENTAGEM\nPor favor, insira um número entre 1 e 100.", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return

    if campos_vazios:
        notification_manager.show_notification("Preencha os campos em branco!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return

    # Definindo o nome do arquivo
    data_atual = datetime.now().strftime("%d.%m.%Y")
    
    if os_num == "":
        nome_arquivo = f"{valor_tab1} - {data_atual} - ORDEM DE COMPRA {nome_fornecedor} - {tipo_servico} - {sigla_contrato}.xlsx"
    else:
        nome_arquivo = f"{valor_tab1} - {data_atual} - ORDEM DE COMPRA {nome_fornecedor} - {os_num} - {agencia} - {prefixo} - {tipo_servico} - {sigla_contrato}.xlsx"    
    
    nome_arquivo = re.sub(r'[<>:"/\\|?*\x00]', ".", nome_arquivo)

    # Gerar texto da solicitação
    if tipo_servico == "ADIANTAMENTO PARCEIRO":
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
        texto += f"SERVIÇO: {tipo_servico} - {tipo_aquisicao}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif tipo_servico == "REEMBOLSO COM OS" or tipo_servico == "SOLICITAÇÃO COM OS":
        texto = (
            f"Solicito o pagamento para {nome_fornecedor}, referente à obra: "
            f"{prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
        )   
        texto += f"SERVIÇO: {tipo_servico}\n\n"
        texto += f"MOTIVO: {motivo}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif tipo_servico == "REEMBOLSO SEM OS":
        texto = f"Solicito o pagamento ao {nome_fornecedor}, para {contrato}.\n\n"
        texto += f"SERVIÇO: {tipo_servico}\n\n"
        texto += f"MOTIVO: {motivo}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
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
        texto = (
            f"Solicito reembolso referente ao deslocamento de {nome_fornecedor}, com {saida_destino}, "
            f"referente à obra: {prefixo} - {agencia} - {os_num}, para {contrato}.\n\n"
            if prefixo
            else f"Solicito reembolso referente ao deslocamento de {nome_fornecedor}, com {saida_destino}, "
            f"para {contrato}.\n\n"
        )
        texto += f"SERVIÇO: {tipo_servico}\n\n"
        texto += f"MOTIVO: {motivo}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif tipo_servico == "HOSPEDAGEM":
        texto = (
            f"Solicito o pagamento ao fornecedor {nome_fornecedor} pela hospedagem dos "
            f"técnicos {tecnicos} referente à obra: {prefixo} - {agencia} - {os_num}, "
            f"para {contrato}.\n\n"
        )
        texto += f"SERVIÇO: {tipo_servico}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif tipo_servico == "SOLICITAÇÃO SEM OS":
        texto = f"Solicito o pagamento ao fornecedor {nome_fornecedor}, para {contrato}.\n\n"
        texto += f"SERVIÇO: {tipo_servico}\n\n"
        texto += f"MOTIVO: {motivo}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif tipo_servico == "ENVIO DE MATERIAL":
        texto = f"Solicito o pagamento ao fornecedor {nome_fornecedor}.\n\n"
        texto += f"SERVIÇO: {tipo_servico}\n\n"
        texto += f"VALOR: R$ {valor_tab1}\n\n"
    elif contrato == "ESCRITÓRIO":
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
            f"Assunto: {nome_arquivo}\n\n"
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
        contrato, motivo, valor_tab1, tipo_pagamento, tecnicos, saida_destino, competencia,
        porcentagem, tipo_aquisicao)

    # Copiar automaticamente o texto gerado caso o switch esteja ativo
    if switch_autocopia_var.get():
        pyperclip.copy(texto)

    if switch_gerar_excel_var.get():
        gerar_excel(root, nome_arquivo, nome_fornecedor, os_num, prefixo, agencia, contrato, nome_usuario, tipo_pagamento, departamento, usuarios_varios_departamentos, usuarios_gerais)

def limpar_dados():
    aba_ativa  = tabview.get()
    
    # Limpar widgets da aba ativa
    if aba_ativa == "PAGAMENTO":
        # Limpar os widgets da Tab 1
        for widget in widgets_para_limpar:
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, tk.END)  # Limpa o campo de entrada
            elif isinstance(widget, ctk.CTkTextbox):
                widget.delete("0.0", tk.END)  # Limpa o campo de texto
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set("")  # Reseta o ComboBox
    elif aba_ativa == "E-MAIL":
        # Limpar os widgets da Tab 2
        for widget in widgets_para_limpar_tab2:
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, tk.END)  # Limpa o campo de entrada
            elif isinstance(widget, ctk.CTkTextbox):
                widget.delete("0.0", tk.END)  # Limpa o campo de texto
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set("")  # Reseta o ComboBox
    elif aba_ativa == "AQUISIÇÃO":
        # Limpar os widgets da Tab 3
        for widget in widgets_para_limpar_tab3:
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, tk.END)  # Limpa o campo de entrada
            elif isinstance(widget, ctk.CTkTextbox):
                widget.delete("0.0", tk.END)  # Limpa o campo de texto
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set("")  # Reseta o ComboBox

def gerar_texto_email():
    # Coletar dados dos campos
    nome_usuario_tab2 = arrumar_texto(nome_usuario_entry_tab2.get().upper())
    tipo_servico_tab2 = arrumar_texto(tipo_servico_combobox_tab2.get().upper())
    nome_fornecedor_tab2 = arrumar_texto(nome_fornecedor_entry_tab2.get().upper())
    prefixo_tab2 = arrumar_texto(prefixo_entry_tab2.get())
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

    notification_manager = NotificationManager(root) # passando a instância da janela principal
    if valor_tab2 == ValueError:
        notification_manager.show_notification(f"Por favor, insira um número válido!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
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

def gerar_texto_aquisicao():
    # Coletar dados dos campos
    nome_usuario_tab3 = arrumar_texto(nome_usuario_entry_tab3.get().upper())
    tipo_aquisicao_tab3 = arrumar_texto(tipo_aquisicao_combobox_tab3.get().upper())
    contrato_tab3 = arrumar_texto(contrato_combobox_tab3.get().upper())
    descricao_tab3 = arrumar_texto(descricao_entry_tab3.get().upper())
    prazo_tab3 = arrumar_texto(prazo_entry_tab3.get_date().upper())
    data_tab3 = arrumar_texto(data_entry_tab3.get_date().upper())
    altura_tab3 = arrumar_texto(altura_entry_tab3.get().upper())
    largura_tab3 = arrumar_texto(largura_entry_tab3.get().upper())
    comprimento_tab3 = arrumar_texto(comprimento_entry_tab3.get().upper())
    servico_tab3 = arrumar_texto(servico_entry_tab3.get().upper())
    espessura_tab3 = arrumar_texto(espessura_entry_tab3.get().upper())
    periodo_locacao_tab3 = arrumar_texto(periodo_locacao_combobox_tab3.get().upper())
    quantidade_tab3 = arrumar_texto(quantidade_entry_tab3.get().upper())
    link_tab3 = arrumar_texto(link_entry_tab3.get())
    prefixo_tab3 = arrumar_texto(prefixo_entry_tab3.get())
    agencia_tab3 = arrumar_texto(agencia_entry_tab3.get().upper())
    os_num_tab3 = valida_os(os_entry_tab3.get())
    opcao_entrega_tab3 = arrumar_texto(opcao_entrega_combobox_tab3.get().upper())
    endereco_agencia_tab3 = arrumar_texto(endereco_agencia_entry_tab3.get().upper())
    nome_responsavel_tab3 = arrumar_texto(nome_responsavel_entry_tab3.get().upper())
    contato_responsavel_tab3 = arrumar_texto(contato_responsavel_entry_tab3.get().upper())

    # Verificar se algum campo obrigatório está vazio
    campos_obrigatorios = [
        (nome_usuario_tab3, "USUÁRIO"),
        (tipo_aquisicao_tab3, "TIPO DE SERVIÇO"),
        (contrato_tab3, "CONTRATO"),
        (descricao_tab3, "DESCRIÇÃO")
    ]

    if tipo_aquisicao_tab3 == "COMPRA":
        # Adiciona os campos comuns para os dois tipos
        campos_obrigatorios.extend([
            (prazo_tab3, "PRAZO"),
            (quantidade_tab3, "QUANTIDADE"),
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
            (servico_tab3, "SERVIÇO"),
            (periodo_locacao_tab3, "PERÍODO DE LOCAÇÃO"),
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
            if item not in {(prefixo_tab3, "PREFIXO"), (agencia_tab3, "AGÊNCIA"), (os_num_tab3, "OS")}
        ]

    # Verificar campos vazios
    campos_vazios = [nome for valor, nome in campos_obrigatorios if not valor]

    notification_manager = NotificationManager(root)  # passando a instância da janela principal
    if campos_vazios:
        notification_manager.show_notification("Preencha os campos obrigatórios em branco!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return

    if os_num_tab3 == "OS_invalida":
        notification_manager.show_notification("Campo OS\nPor favor, insira uma OS válida!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
        return

    if tipo_aquisicao_tab3 == "COMPRA":
            texto = f"*SOLICITAÇÃO DE AQUISIÇÃO - {tipo_aquisicao_tab3}*\n\n"
            texto += f"▪ *Contrato:* {contrato_tab3}\n"
            texto += f"▪ *Descrição da aquisição:* {descricao_tab3}\n"
            texto += f"▪ *Prazo para aquisição:* {prazo_tab3}\n"
            texto += f"▪ *Altura:* {altura_tab3}\n" if altura_tab3 else ""
            texto += f"▪ *Largura:* {largura_tab3}\n" if largura_tab3 else ""
            texto += f"▪ *Comprimento:* {comprimento_tab3}\n" if comprimento_tab3 else ""
            texto += f"▪ *Espessura:* {espessura_tab3}\n" if espessura_tab3 else ""
            texto += f"▪ *Quantidade:* {quantidade_tab3}\n"
            texto += f"▪ *Link:* {link_tab3}\n" if link_tab3 else ""
            texto += f"▪ *Prefixo, Agência e OS:* {prefixo_tab3} - {agencia_tab3} - {os_num_tab3}\n" if os_num_tab3 else f""
            texto += f"▪ *Entrega ou Retirada:* ENTREGA\n▪ *Endereço da Agência:* {endereco_agencia_tab3}\n" if opcao_entrega_tab3 == "ENTREGA" else "▪ *Entrega ou Retirada:* RETIRADA\n"            
            texto += f"▪ *Nome do responsável:* {nome_responsavel_tab3}\n"
            texto += f"▪ *Contato do responsável:* {contato_responsavel_tab3}\n"
    else:        
            texto = f"*SOLICITAÇÃO DE AQUISIÇÃO - {tipo_aquisicao_tab3}*\n\n"
            texto += f"▪ *Contrato:* {contrato_tab3}\n"
            texto += f"▪ *Descrição da locação:* {descricao_tab3}\n"
            texto += f"▪ *Data da locação:* {data_tab3}\n"
            texto += f"▪ *Serviço:* {servico_tab3}\n"
            texto += f"▪ *Período da locação:* {periodo_locacao_tab3}\n"
            texto += f"▪ *Prefixo, Agência e OS:* {prefixo_tab3} - {agencia_tab3} - {os_num_tab3}\n" if os_num_tab3 else f""
            texto += f"▪ *Entrega ou Retirada:* ENTREGA\n▪ *Endereço da Agência:* {endereco_agencia_tab3}\n" if opcao_entrega_tab3 == "ENTREGA" else "▪ *Entrega ou Retirada:* RETIRADA\n"            
            texto += f"▪ *Nome do responsável:* {nome_responsavel_tab3}\n"
            texto += f"▪ *Contato do responsável:* {contato_responsavel_tab3}\n"            

    # Exibir texto na caixa de texto
    texto_aquisicao.delete(1.0, tk.END)
    texto_aquisicao.insert(tk.END, texto)

    # Copiar automaticamente o texto gerado caso o switch esteja ativo
    if switch_autocopia_frame_tab3_var.get():
        pyperclip.copy(texto)
    
def add_campos():
    tipo_servico = tipo_servico_combobox.get()

    prefixo_label.configure(text="PREFIXO:")
    agencia_label.configure(text="AGÊNCIA:")
    os_label.configure(text="OS ou Nº DO CONTRATO (CAIXA):")

    contrato_combobox.configure(values=[
        "ESCRITÓRIO", "C. O. BELO HORIZONTE - MG - 2054", "C. O. MANAUS - AM - 7649",  "C. O. NITERÓI - RJ - 1380", 
        "C. O. RECIFE - PE - 5254", "C. O. RIO DE JANEIRO - RJ - 0494", "C. O. RIO GRANDE DO SUL - RS - 5525", 
        "C. O. RONDÔNIA - RD - S/N", "C. O. SALVADOR - BA - 2877", "C. O. SANTA CATARINA - SC - 5023", 
        "C. O. VOLTA REDONDA - RJ - 0215", "ATA BB CURITIBA - 0232", "C. E. MANAUS - S/N", "CAIXA BAHIA - 4922.2024",
        "CAIXA CURITIBA - 534.2025", "CAIXA MANAUS - 4569.2024", "INFRA CURITIBA - S/N"
    ])
    contrato_combobox.set("")

    tipo_pagamento_combobox.set("")
    tipo_chave_pix_label.grid_forget()
    tipo_chave_pix_combobox.grid_forget()
    chave_pix_label.grid_forget()
    chave_pix_entry.grid_forget()
    nome_benef_pix_label.grid_forget()
    nome_benef_pix_entry.grid_forget()

    # Oculta todos os campos por padrão
    for widget in [
        competencia_label, competencia_combobox,
        porcentagem_label, porcentagem_entry,
        motivo_label, motivo_entry,
        saida_destino_label, saida_destino_entry,
        tecnicos_label, tecnicos_entry
    ]:
        widget.grid_forget()

    # Limpa os campos de entrada por padrão
    competencia_combobox.set("")
    porcentagem_entry.delete(0, tk.END)
    motivo_entry.delete(0, tk.END)
    saida_destino_entry.delete(0, tk.END)
    tecnicos_entry.delete(0, tk.END)

    if tipo_servico == "ADIANTAMENTO PARCEIRO":
        competencia_label.grid(row=9, column=0, sticky="w", padx=(10, 10))
        competencia_combobox.grid(row=9, column=1, sticky="ew", padx=(0, 10), pady=2)
        porcentagem_label.grid(row=10, column=0, sticky="w", padx=(10, 10))
        porcentagem_entry.grid(row=10, column=1, sticky="ew", padx=(0, 10), pady=2)

    elif tipo_servico in {"REEMBOLSO SEM OS", "SOLICITAÇÃO SEM OS", "REEMBOLSO COM OS", "SOLICITAÇÃO COM OS"}:
        motivo_label.grid(row=2, column=0, sticky="w", padx=(10, 10))
        motivo_entry.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=2)

    elif tipo_servico == "REEMBOLSO UBER":
        saida_destino_label.grid(row=2, column=0, sticky="w", padx=(10, 10))
        saida_destino_entry.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=2)
        motivo_label.grid(row=4, column=0, sticky="w", padx=(10, 10))
        motivo_entry.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)

    elif tipo_servico in {"ABASTECIMENTO", "ESTACIONAMENTO", "HOSPEDAGEM"}:
        tecnicos_label.grid(row=2, column=0, sticky="w", padx=(10, 10))
        tecnicos_entry.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=2)  

    # Mostrar ou esconder PREFIXO, OS e AGÊNCIA
    esconde_pref_age_os = {
        "REEMBOLSO SEM OS",
        "SOLICITAÇÃO SEM OS",
        "ABASTECIMENTO",
        "ENVIO DE MATERIAL",
        "AQUISIÇÃO SEM OS",
    }

    if tipo_servico in esconde_pref_age_os:
        contrato_combobox.configure(values=[
            "ESCRITÓRIO", "C. O. BELO HORIZONTE - MG - 2054", "C. O. MANAUS - AM - 7649",  "C. O. NITERÓI - RJ - 1380",
            "C. O. RECIFE - PE - 5254", "C. O. RIO DE JANEIRO - RJ - 0494", "C. O. RIO GRANDE DO SUL - RS - 5525",
            "C. O. RONDÔNIA - RD - S/N", "C. O. SALVADOR - BA - 2877", "C. O. SANTA CATARINA - SC - 5023",
            "C. O. VOLTA REDONDA - RJ - 0215", "ATA BB CURITIBA - 0232", "C. E. MANAUS - S/N", "CAIXA BAHIA - 4922.2024",
            "CAIXA CURITIBA - 534.2025", "CAIXA MANAUS - 4569.2024", "INFRA CURITIBA - S/N"
        ])
        prefixo_label.grid_forget()
        prefixo_entry.grid_forget()
        os_label.grid_forget()
        os_entry.grid_forget()
        agencia_label.grid_forget()
        agencia_entry.grid_forget()
    elif tipo_servico == "REEMBOLSO UBER":
        prefixo_label.grid(row=5, column=0, sticky="w", padx=(10, 10))
        prefixo_label.configure(text="PREFIXO (SE APLICÁVEL):")
        prefixo_entry.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)

        agencia_label.grid(row=6, column=0, sticky="w", padx=(10, 10))
        agencia_label.configure(text="AGÊNCIA (SE APLICÁVEL):")
        agencia_entry.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)

        os_label.grid(row=7, column=0, sticky="w", padx=(10, 10))
        os_label.configure(text="OS ou Nº DO CONTRATO (CAIXA)\n(SE APLICÁVEL):")
        os_entry.grid(row=7, column=1, sticky="ew", padx=(0, 10), pady=2)
    else:
        prefixo_label.grid(row=5, column=0, sticky="w", padx=(10, 10))
        prefixo_entry.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)
        agencia_label.grid(row=6, column=0, sticky="w", padx=(10, 10))
        agencia_entry.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)
        os_label.grid(row=7, column=0, sticky="w", padx=(10, 10))
        os_entry.grid(row=7, column=1, sticky="ew", padx=(0, 10), pady=2)

    tipo_pagamento_combobox.set("") # limpar a seleção antes de configurar os valores
    if tipo_servico in {"ADIANTAMENTO PARCEIRO", "ABASTECIMENTO"}:
        opcoes_pagamento = ["PIX"]
    elif tipo_servico in {"ORÇAMENTO APROVADO", "AQUISIÇÃO SEM OS", "AQUISIÇÃO COM OS"}:
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

def add_campos_tab2():
    tipo_servico_tab2 = tipo_servico_combobox_tab2.get()
 
    if tipo_servico_tab2 in {"COMPRAS EM GERAL - COM OS", "LOCAÇÃO"}:
        prefixo_label_tab2.grid(row=4, column=0, sticky="w", padx=(10, 10))
        prefixo_entry_tab2.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)
        os_label_tab2.grid(row=5, column=0, sticky="w", padx=(10, 10))
        os_entry_tab2.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)
        agencia_label_tab2.grid(row=6, column=0, sticky="w", padx=(10, 10))
        agencia_entry_tab2.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)
    else:
        prefixo_label_tab2.grid_forget()
        prefixo_entry_tab2.grid_forget()
        os_label_tab2.grid_forget()
        os_entry_tab2.grid_forget()
        agencia_label_tab2.grid_forget()
        agencia_entry_tab2.grid_forget()

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

def add_campos_tab3():
    tipo_aquisicao_tab3 = tipo_aquisicao_combobox_tab3.get()
    contrato_tab3 = contrato_combobox_tab3.get()
 
    if tipo_aquisicao_tab3 == "COMPRA":
        data_label_tab3.grid_forget()
        data_entry_tab3.grid_forget()
        prazo_label_tab3.grid(row=4, column=0, sticky="w", padx=(10, 10))
        prazo_entry_tab3.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)
        servico_label_tab3.grid_forget()
        servico_entry_tab3.grid_forget()
        altura_label_tab3.grid(row=5, column=0, sticky="w", padx=(10, 10))
        altura_entry_tab3.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)
        largura_label_tab3.grid(row=6, column=0, sticky="w", padx=(10, 10))
        largura_entry_tab3.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)
        comprimento_label_tab3.grid(row=7, column=0, sticky="w", padx=(10, 10))
        comprimento_entry_tab3.grid(row=7, column=1, sticky="ew", padx=(0, 10), pady=2)
        periodo_locacao_label_tab3.grid_forget()
        periodo_locacao_combobox_tab3.grid_forget()
        espessura_label_tab3.grid(row=8, column=0, sticky="w", padx=(10, 10))
        espessura_entry_tab3.grid(row=8, column=1, sticky="ew", padx=(0, 10), pady=2)
        quantidade_label_tab3.grid(row=9, column=0, sticky="w", padx=(10, 10))
        quantidade_entry_tab3.grid(row=9, column=1, sticky="ew", padx=(0, 10), pady=2)
        link_label_tab3.grid(row=10, column=0, sticky="w", padx=(10, 10))
        link_entry_tab3.grid(row=10, column=1, sticky="ew", padx=(0, 10), pady=2)
        prefixo_label_tab3.grid(row=11, column=0, sticky="w", padx=(10, 10))
        prefixo_entry_tab3.grid(row=11, column=1, sticky="ew", padx=(0, 10), pady=2)
        os_label_tab3.grid(row=12, column=0, sticky="w", padx=(10, 10))
        os_entry_tab3.grid(row=12, column=1, sticky="ew", padx=(0, 10), pady=2)
        agencia_label_tab3.grid(row=13, column=0, sticky="w", padx=(10, 10))
        agencia_entry_tab3.grid(row=13, column=1, sticky="ew", padx=(0, 10), pady=2)
        opcao_entrega_label_tab3.grid(row=14, column=0, sticky="w", padx=(10, 10))
        opcao_entrega_combobox_tab3.grid(row=14, column=1, sticky="ew", padx=(0, 10), pady=2)
        nome_responsavel_label_tab3.grid(row=16, column=0, sticky="w", padx=(10, 10))
        nome_responsavel_entry_tab3.grid(row=16, column=1, sticky="ew", padx=(0, 10), pady=2)
        contato_responsavel_agencia_label_tab3.grid(row=17, column=0, sticky="w", padx=(10, 10))
        contato_responsavel_entry_tab3.grid(row=17, column=1, sticky="ew", padx=(0, 10), pady=2)
    elif tipo_aquisicao_tab3 == "LOCAÇÃO":
        prazo_label_tab3.grid_forget()
        prazo_entry_tab3.grid_forget()
        data_label_tab3.grid(row=4, column=0, sticky="w", padx=(10, 10))
        data_entry_tab3.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=2)
        altura_label_tab3.grid_forget()
        altura_entry_tab3.grid_forget()
        largura_label_tab3.grid_forget()
        largura_entry_tab3.grid_forget()
        comprimento_label_tab3.grid_forget()
        comprimento_entry_tab3.grid_forget()
        servico_label_tab3.grid(row=5, column=0, sticky="w", padx=(10, 10))
        servico_entry_tab3.grid(row=5, column=1, sticky="ew", padx=(0, 10), pady=2)
        espessura_label_tab3.grid_forget()
        espessura_entry_tab3.grid_forget()
        periodo_locacao_label_tab3.grid(row=6, column=0, sticky="w", padx=(10, 10))
        periodo_locacao_combobox_tab3.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)        
        quantidade_label_tab3.grid_forget()
        quantidade_entry_tab3.grid_forget()
        link_label_tab3.grid_forget()
        link_entry_tab3.grid_forget()
        prefixo_label_tab3.grid(row=9, column=0, sticky="w", padx=(10, 10))
        prefixo_entry_tab3.grid(row=9, column=1, sticky="ew", padx=(0, 10), pady=2)
        os_label_tab3.grid(row=10, column=0, sticky="w", padx=(10, 10))
        os_entry_tab3.grid(row=10, column=1, sticky="ew", padx=(0, 10), pady=2)
        agencia_label_tab3.grid(row=11, column=0, sticky="w", padx=(10, 10))
        agencia_entry_tab3.grid(row=11, column=1, sticky="ew", padx=(0, 10), pady=2)
        opcao_entrega_label_tab3.grid(row=12, column=0, sticky="w", padx=(10, 10))
        opcao_entrega_combobox_tab3.grid(row=12, column=1, sticky="ew", padx=(0, 10), pady=2)
        nome_responsavel_label_tab3.grid(row=16, column=0, sticky="w", padx=(10, 10))
        nome_responsavel_entry_tab3.grid(row=16, column=1, sticky="ew", padx=(0, 10), pady=2)
        contato_responsavel_agencia_label_tab3.grid(row=17, column=0, sticky="w", padx=(10, 10))
        contato_responsavel_entry_tab3.grid(row=17, column=1, sticky="ew", padx=(0, 10), pady=2)
    
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

    if opcao_entrega_combobox_tab3.get() == "ENTREGA":
        endereco_agencia_label_tab3.grid(row=15, column=0, sticky="w", padx=(10, 10))
        endereco_agencia_entry_tab3.grid(row=15, column=1, sticky="ew", padx=(0, 10), pady=2)
    else:
        endereco_agencia_label_tab3.grid_forget()
        endereco_agencia_entry_tab3.grid_forget()

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

def janela_principal():
    from .ui_tela_login import nome_completo_usuario, abas_permitidas

    # Variáveis globais principais
    global root, tabview, frame, widgets_para_limpar, widgets_para_limpar_tab2, widgets_para_limpar_tab3
    global usuarios_varios_departamentos, usuarios_gerais

    # Widgets da aba PAGAMENTO
    global nome_usuario_entry, tipo_servico_combobox, nome_fornecedor_entry, prefixo_entry, agencia_entry
    global os_entry, contrato_combobox, motivo_entry, valor_entry, tipo_pagamento_combobox, tecnicos_entry
    global saida_destino_entry, competencia_combobox, porcentagem_entry, tipo_aquisicao_combobox, tipo_chave_pix_combobox
    global chave_pix_entry, texto_solicitacao, switch_autocopia_var, switch_gerar_excel_var
    global tipo_chave_pix_label, chave_pix_label, competencia_label, porcentagem_label, motivo_label
    global saida_destino_label, tecnicos_label, prefixo_label, os_label, agencia_label, contrato_label
    global nome_benef_pix_label, nome_benef_pix_entry
    global tipo_aquisicao_label, gerar_button

    # Widgets da aba E-MAIL
    global nome_usuario_entry_tab2, tipo_servico_combobox_tab2, prefixo_entry_tab2, agencia_entry_tab2
    global os_entry_tab2, endereco_entry_tab2, nome_fornecedor_entry_tab2, valor_entry_tab2, num_orcamento_label_tab2
    global tipo_pagamento_combobox_tab2, num_orcamento_entry_tab2, texto_email, switch_autocopia_frame_tab2_var
    global prefixo_label_tab2, os_label_tab2, agencia_label_tab2, endereco_agencia_label_tab2, gerar_button_tab2

    # Widgets da aba AQUISIÇÃO
    global nome_usuario_entry_tab3, tipo_aquisicao_combobox_tab3, contrato_combobox_tab3, descricao_entry_tab3
    global prazo_entry_tab3, data_entry_tab3, servico_entry_tab3, espessura_entry_tab3
    global periodo_locacao_combobox_tab3, quantidade_entry_tab3, link_entry_tab3, prefixo_entry_tab3
    global agencia_entry_tab3, os_entry_tab3, opcao_entrega_combobox_tab3, endereco_agencia_entry_tab3
    global nome_responsavel_entry_tab3, contato_responsavel_entry_tab3, texto_aquisicao, switch_autocopia_frame_tab3_var
    global data_label_tab3, prazo_label_tab3, servico_label_tab3, periodo_locacao_label_tab3
    global espessura_label_tab3, quantidade_label_tab3, link_label_tab3, prefixo_label_tab3, os_label_tab3
    global agencia_label_tab3, opcao_entrega_label_tab3, nome_responsavel_label_tab3, contato_responsavel_agencia_label_tab3
    global altura_label_tab3, altura_entry_tab3, largura_label_tab3, largura_entry_tab3, comprimento_label_tab3, comprimento_entry_tab3
    global endereco_agencia_label_tab3, gerar_button_tab3

    # Configuração da interface gráfica
    root = ctk.CTk()
    root.title("Modelo Solicitação de Pagamento")
    root.geometry("520x600")
    ctk.set_default_color_theme("green")

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

    if "PAGAMENTO" in abas_permitidas:
        # -------------------------------
        # Aba "PAGAMENTO"
        # -------------------------------
        frame = ctk.CTkScrollableFrame(master=tabview.tab("PAGAMENTO"))
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Configurando a coluna do frame para expandir
        frame.grid_rowconfigure(18, weight=1)  # Expande a linha
        frame.grid_columnconfigure(0, weight=1)  # Expande a coluna 0
        frame.grid_columnconfigure(1, weight=1)  # Expande a coluna 1

        # Lista para armazenar os widgets que precisam ser limpos
        widgets_para_limpar = []
        widgets_para_limpar_tab2 = []
        widgets_para_limpar_tab3 = []

        usuarios_gerais = ["AMANDA SAMPAIO",
            "CARLOS ALBERTO",
            "DANIEL ROMUALDO",
            "DAWISON NASCIMENTO",
            "FELIPE COSTA",
            "FELIPE MOTA",
            "GABRIEL BARBOSA",
            "GUILHERME GOMES",
            "HENRIQUE CARDOSO",
            "IGOR SAMPAIO",
            "IURE OLIVEIRA",
            "JOÃO GABRIEL",
            "LUCAS ASSUNÇÃO",
            "LUCAS HEBERT",
            "MATEUS SILVA",
            "TÁCIO BARBOSA",
            "TAIANE MARQUES",
            "VINICIUS CRUZ"
        ]

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
            "ADIANTAMENTO PARCEIRO",  
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
            "SOLICITAÇÃO COM OS",  
            "SOLICITAÇÃO SEM OS",  
            "TRANSPORTADORA"
        ], command=lambda choice: add_campos())
        tipo_servico_combobox.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=2)
        tipo_servico_combobox.set("")

        contrato_label = ctk.CTkLabel(master=frame, text="CONTRATO:")#.grid(row=6, column=0, sticky="w", padx=(10, 10))
        '''Label e Combobox de Contrato apenas aparecem após a seleção do tipo_serviço.
        Iniciado combobox sem valor, já que, ao selecionar determinado tipo_serviço, o Contrato mostra valores específicos
        '''
        contrato_combobox = CustomComboBox(master=frame, values=[])
        #contrato_combobox.grid(row=6, column=1, sticky="ew", padx=(0, 10), pady=2)
        #contrato_combobox.set("")

        # Campo para MOTIVO
        motivo_label = ctk.CTkLabel(master=frame, text="MOTIVO:")
        motivo_entry = CustomEntry(master=frame)
        widgets_para_limpar.append(motivo_entry)

        tipo_aquisicao_label = ctk.CTkLabel(master=frame, text="TIPO DE AQUISIÇÃO:")
        tipo_aquisicao_combobox = CustomComboBox(master=frame)
        tipo_aquisicao_combobox.set("")
        widgets_para_limpar.append(tipo_aquisicao_combobox)
        # Associa a função ao evento de exclusão manual (quando o campo perde o foco ou quando uma tecla é liberada)
        tipo_aquisicao_combobox.bind("<FocusOut>", restaurar_valores_tipo_aquisicao)  # Quando o campo perde o foco
        tipo_aquisicao_combobox.bind("<KeyRelease>", restaurar_valores_tipo_aquisicao)  # Quando o usuário digita algo

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

        ctk.CTkLabel(master=frame, text="VALOR:").grid(row=11, column=0, sticky="w", padx=(10, 10))
        valor_entry = CustomEntry(master=frame)
        valor_entry.grid(row=11, column=1, sticky="ew", padx=(0, 10), pady=2)
        widgets_para_limpar.append(valor_entry)

        ano_atual = datetime.now().strftime("%Y")
        # Campos para ADIANTAMENTO PARCEIRO
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

        nome_benef_pix_label = ctk.CTkLabel(master=frame, text="NOME DO BENEF. DO PIX\n(SE APLICÁVEL):")
        nome_benef_pix_entry = CustomEntry(master=frame)
        widgets_para_limpar.append(nome_benef_pix_entry)

        # Campo para SAÍDA X DESTINO (UBER)
        saida_destino_label = ctk.CTkLabel(master=frame, text="SAÍDA X DESTINO:")
        saida_destino_entry = CustomEntry(master=frame)
        widgets_para_limpar.append(saida_destino_entry)

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

        os_label_tab2 = ctk.CTkLabel(master=frame_tab2, text="OS:")
        os_entry_tab2 = CustomEntry(master=frame_tab2)
        widgets_para_limpar_tab2.append(os_entry_tab2)

        agencia_label_tab2 = ctk.CTkLabel(master=frame_tab2, text="AGÊNCIA:")
        agencia_entry_tab2 = CustomEntry(master=frame_tab2)
        widgets_para_limpar_tab2.append(agencia_entry_tab2)

        endereco_agencia_label_tab2 = ctk.CTkLabel(master=frame_tab2, text="ENDEREÇO DA AGÊNCIA:")
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
        num_orcamento_entry_tab2 = CustomEntry(master=frame_tab2)
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
            "ESCRITÓRIO", "C. O. BELO HORIZONTE - MG - 2054", "C. O. MANAUS - AM - 7649",  "C. O. NITERÓI - RJ - 1380", 
            "C. O. RECIFE - PE - 5254", "C. O. RIO DE JANEIRO - RJ - 0494", "C. O. RIO GRANDE DO SUL - RS - 5525", 
            "C. O. RONDÔNIA - RD - S/N", "C. O. SALVADOR - BA - 2877", "C. O. SANTA CATARINA - SC - 5023", 
            "C. O. VOLTA REDONDA - RJ - 0215", "ATA BB CURITIBA - 0232", "C. E. MANAUS - S/N", "CAIXA BAHIA - 4922.2024",
            "CAIXA CURITIBA - 534.2025", "CAIXA MANAUS - 4569.2024", "INFRA CURITIBA - S/N"
        ], command=lambda choice: add_campos_tab3())
        contrato_combobox_tab3.grid(row=2, column=1, sticky="ew", padx=(0, 10), pady=2)
        contrato_combobox_tab3.set("")

        ctk.CTkLabel(master=frame_tab3, text="DESCRIÇÃO:").grid(row=3, column=0, sticky="w", padx=(10, 10))
        descricao_entry_tab3 = CustomEntry(master=frame_tab3)
        descricao_entry_tab3.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=2)
        widgets_para_limpar_tab3.append(descricao_entry_tab3)

        #row = 4
        prazo_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="PRAZO:")
        prazo_entry_tab3 = CTkDatePicker(master=frame_tab3)
        prazo_entry_tab3.set_date_format("%d/%m/%Y")
        prazo_entry_tab3.set_allow_manual_input(False)

        data_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="DATA DA LOCAÇÃO:")
        data_entry_tab3 = CTkDatePicker(master=frame_tab3)
        data_entry_tab3.set_date_format("%d/%m/%Y")
        data_entry_tab3.set_allow_manual_input(False)

        #row = 5
        altura_label_tab3 = ctk.CTkLabel(master=frame_tab3, text=f"ALTURA (SE APLICÁVEL):", anchor="w", justify="left")
        altura_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(altura_entry_tab3)

        servico_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="SERVIÇO:")
        servico_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(servico_entry_tab3)

        #row = 6
        largura_label_tab3 = ctk.CTkLabel(master=frame_tab3, text=f"LARGURA (SE APLICÁVEL):", anchor="w", justify="left")
        largura_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(largura_entry_tab3)

        periodo_locacao_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="PERÍODO DE LOCAÇÃO:")
        periodo_locacao_combobox_tab3 = CustomComboBox(master=frame_tab3, values=[
            "DIÁRIA", "SEMANAL", "QUINZENAL", "MENSAL"
        ])
        periodo_locacao_combobox_tab3.set("")
        widgets_para_limpar_tab3.append(periodo_locacao_combobox_tab3)

        #row = 7
        comprimento_label_tab3 = ctk.CTkLabel(master=frame_tab3, text=f"COMPRIMENTO (SE APLICÁVEL):", anchor="w", justify="left")
        comprimento_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(comprimento_entry_tab3)

        #row = 8
        espessura_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="ESPESSURA (SE APLICÁVEL):")
        espessura_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(espessura_entry_tab3)

        #row = 9
        quantidade_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="QUANTIDADE:")
        quantidade_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(quantidade_entry_tab3)

        #row = 10
        link_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="LINK (SE APLICÁVEL):")
        link_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(link_entry_tab3)

        #row = 11
        prefixo_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="PREFIXO:")
        prefixo_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(prefixo_entry_tab3)

        #row = 12
        os_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="OS:")
        os_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(os_entry_tab3)

        #row = 13
        agencia_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="AGÊNCIA:")
        agencia_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(agencia_entry_tab3)

        endereco_agencia_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="ENDEREÇO DE ENTREGA:")
        endereco_agencia_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(endereco_agencia_entry_tab3)

        #row = 14
        opcao_entrega_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="OPÇÃO DE ENTREGA:")
        opcao_entrega_combobox_tab3 = CustomComboBox(master=frame_tab3, values=[
            "ENTREGA",
            "RETIRADA",
        ], command=lambda choice: add_campos_tab3())
        opcao_entrega_combobox_tab3.set("")
        widgets_para_limpar_tab3.append(opcao_entrega_combobox_tab3)

        #row = 15
        nome_responsavel_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="NOME DO RESPONSÁVEL:")
        nome_responsavel_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(nome_responsavel_entry_tab3)

        #row = 16
        contato_responsavel_agencia_label_tab3 = ctk.CTkLabel(master=frame_tab3, text="CONTATO DO RESPONSÁVEL:")
        contato_responsavel_entry_tab3 = CustomEntry(master=frame_tab3)
        widgets_para_limpar_tab3.append(contato_responsavel_entry_tab3)
        
        #row = 17
        gerar_button_tab3 = ctk.CTkButton(master=frame_tab3, text="GERAR", command=gerar_texto_aquisicao)
        gerar_button_tab3.grid(row=18, column=0, sticky="ew", padx=(10, 10), pady=10)

        root.bind("<Return>", on_return_press)

        limpar_button_tab3 = ctk.CTkButton(master=frame_tab3, text="LIMPAR", width=150, command=limpar_dados)
        limpar_button_tab3.grid(row=18, column=1, sticky="ew", padx=(0, 10), pady=10)

        #row = 18
        switch_autocopia_frame_tab3_var = tk.BooleanVar(value=True)
        switch_autocopia_frame_tab3 = ctk.CTkSwitch(master=frame_tab3, text="Auto-Cópia",
                                        variable=switch_autocopia_frame_tab3_var, onvalue=True, offvalue=False)
        switch_autocopia_frame_tab3.grid(row=19, column=0, columnspan=2, sticky="n", padx=10, pady=10)

        #row = 19
        texto_aquisicao = ctk.CTkTextbox(master=frame_tab3)
        texto_aquisicao.grid(row=20, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")
        widgets_para_limpar_tab3.append(texto_aquisicao)

    root.mainloop()