from openpyxl import load_workbook
from openpyxl.styles import Alignment
import os, shutil, time
from tkinter import filedialog, messagebox
from datetime import datetime
from openpyxl.worksheet.datavalidation import DataValidation
from app.CTkFloatingNotifications import NotificationManager, NotifyType

def gerar_excel(root, nome_arquivo, tipo_servico, nome_fornecedor, os_num, prefixo, agencia, contrato, nome_usuario, tipo_pagamento, departamento, usuarios_varios_departamentos, usuarios_gerais, descricao_itens):
    """
    Gera um arquivo Excel de requisição baseado em um modelo pré-definido.

    Esta função copia um arquivo modelo de ordem de compra, preenche com os dados fornecidos (como fornecedor, usuário, tipo de pagamento, contrato, OS, etc.), aplica validações de dados conforme o perfil do usuário e salva o arquivo em um diretório escolhido. Se o nome do arquivo já existir no local, cria uma nova versão com sufixo incremental (_Cópia 1, _Cópia 2...).

    Parâmetros:
    -----------
    root : Tk
        Referência à janela principal da interface (para exibir notificações).
    nome_arquivo : str
        Nome inicial desejado para o arquivo gerado (ex: 'Ordem_Compra.xlsx').
    nome_fornecedor : str
        Nome do fornecedor a ser inserido na planilha.
    os_num : str or int
        Número da OS (Ordem de Serviço). Pode ser vazio ou nulo.
    prefixo : str
        Prefixo associado à OS, usado junto da agência.
    agencia : str
        Agência vinculada à OS.
    contrato : str
        Nome do contrato (ou "ESCRITÓRIO" se não informado).
    nome_usuario : str
        Nome do usuário responsável pela requisição.
    tipo_pagamento : str
        Tipo de pagamento ("FATURAMENTO", "SEM CUSTO PARA ENTREGA", etc.).
    departamento : str
        Departamento ao qual a requisição pertence.
    usuarios_varios_departamentos : list[str]
        Lista de usuários que têm acesso a múltiplos departamentos (com validação por lista).
    usuarios_gerais : list[str]
        Lista de usuários com departamento fixo (sem múltipla escolha).

    Retorno:
    --------
    None

    Efeitos colaterais:
    -------------------
    - Exibe notificações gráficas ao usuário (sucesso, erro, alertas).
    - Salva e abre o arquivo Excel gerado.
    - Aplica validações de dados em células específicas da planilha.
    - Cria automaticamente um novo nome se o arquivo já existir no destino.

    Exceções tratadas:
    ------------------
    - Arquivo modelo não encontrado.
    - Nenhum diretório selecionado.
    - Erros gerais na manipulação do Excel ou no processo de geração.
    """
    notification_manager = NotificationManager(root)

    try:
        caminho_modelo = r"G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\dist\MODELO NOVO 2024 - ORDEM DE COMPRA.xlsx"

        if not os.path.exists(caminho_modelo):
            notification_manager.show_notification(f"Arquivo modelo não encontrado!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return

        caminho_destino = filedialog.askdirectory()

        if not caminho_destino:
            notification_manager.show_notification(f"Nenhum diretório selecionado!", NotifyType.WARNING, bg_color="#404040", text_color="#FFFFFF")
            return
        
        base_nome, extensao = os.path.splitext(nome_arquivo)
        nome_arquivo_destino = os.path.join(caminho_destino, nome_arquivo)

        contador = 1
        while os.path.exists(nome_arquivo_destino):
            novo_nome = f"{base_nome}_Cópia {contador}{extensao}"
            nome_arquivo_destino = os.path.join(caminho_destino, novo_nome)
            contador += 1

        shutil.copy(caminho_modelo, nome_arquivo_destino)

        workbook = load_workbook(nome_arquivo_destino)
        sheet_principal = workbook["Planilha1"]

        data_atual = datetime.now().strftime("%d/%m/%Y")
        sheet_principal["D5"] = nome_fornecedor
        sheet_principal["D11"] = nome_usuario
        sheet_principal["D16"] = contrato if contrato else "ESCRITÓRIO"

        if tipo_pagamento == "FATURAMENTO":
            sheet_principal["D47"] = "FATURADO"
        else:
            sheet_principal["D47"] = tipo_pagamento

        sheet_principal["B53"] = f"Assinatura: {nome_usuario}"
        sheet_principal["B54"] = f"Data: {data_atual}"

        if os_num in (0, '', None):
            sheet_principal["D14"] = "-"
            sheet_principal["D15"] = "-"
        else:
            sheet_principal["D14"] = os_num
            sheet_principal["D15"] = f"{prefixo} - {agencia}"
        
        '''Usuários que podem selecionar departamentos'''
        # Verificação do nome do usuário
        if nome_usuario in usuarios_varios_departamentos:
            # Se o nome do usuário estiver na lista de 'usuarios_varios_departamentos', aplica a validação
            workbook.active = sheet_principal
            dv = DataValidation(
                type="list", 
                formula1='"SETOR DE COMPRAS,ESCRITÓRIO,CONTRATO BA,CONTRATO SC,CONTRATO RS,CONTRATO RJ,CONTRATO NT,CONTRATO MG,CONTRATO PE,CONTRATO VOLTA REDONDA,CONTRATO RONDÔNIA,CONTRATO AM"',
                showDropDown=False,
                allow_blank=True
            )
            sheet_principal.add_data_validation(dv)
            dv.add("D13")  # Aplicando a validação na célula D13
            
            if departamento == "ESCRITÓRIO":
                sheet_principal["D13"] = departamento
            else:
                sheet_principal["D13"] = "SETOR DE COMPRAS"
        elif nome_usuario in usuarios_gerais:
            # Se o nome do usuário estiver na lista de 'usuarios_gerais' (mas não em 'usuarios_varios_departamentos'), atribui o valor diretamente
            sheet_principal["D13"] = departamento

        if tipo_servico == "RELATÓRIO EXTRA":
            descricao_lista = descricao_itens.split("\n")
            sheet_principal.column_dimensions["E"].width = 15
            linha_inicial = 19

            for i, descricao in enumerate(descricao_lista):
                sheet_principal[f"B{linha_inicial + i}"] = f"{i + 1}"
                sheet_principal[f"C{linha_inicial + i}"] = descricao
                sheet_principal[f"C{linha_inicial + i}"].alignment = Alignment(wrap_text=False, horizontal='center', vertical='center')
                sheet_principal[f"F{linha_inicial + i}"] = 1
                sheet_principal[f"G{linha_inicial + i}"] = "80,00"

        # Restaurando a Validação de Dados
        workbook.active = sheet_principal
        dv = DataValidation(
            type="list", 
            formula1='"SEM CUSTO PARA ENTREGA,COM CUSTO PARA ENTREGA"',
            showDropDown=False,
            allow_blank=True
        )
        sheet_principal.add_data_validation(dv)
        dv.add("D48")

        workbook.save(nome_arquivo_destino)
        workbook.close()

        notification_manager.show_notification(f"Sucesso!\nArquivo salvo no local selecionado.\nAbrindo o arquivo...", NotifyType.SUCCESS, bg_color="#404040", text_color="#FFFFFF")

        try:
            time.sleep(1.2)
            os.startfile(nome_arquivo_destino)
        except FileNotFoundError:
            notification_manager.show_notification(f"Arquivo não encontrado após a geração.", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            print(FileNotFoundError)
    except Exception as e:
        notification_manager.show_notification(f"Erro ao gerar o arquivo Excel: {e}", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")