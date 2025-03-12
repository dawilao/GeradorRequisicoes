from openpyxl import load_workbook
import os, shutil
from tkinter import filedialog, messagebox
from datetime import datetime
from openpyxl.worksheet.datavalidation import DataValidation
from app.CTkFloatingNotifications import NotificationManager, NotifyType

def gerar_excel(root, nome_arquivo, nome_fornecedor, os_num, prefixo, agencia, contrato, nome_usuario, tipo_pagamento, departamento, usuarios_varios_departamentos, usuarios_gerais):
    try:
        # Caminho do arquivo modelo
        caminho_modelo = r"G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\dist\MODELO NOVO 2024 - ORDEM DE COMPRA.xlsx"

        # Verificar se o arquivo modelo existe
        if not os.path.exists(caminho_modelo):
            notification_manager = NotificationManager(root)  # passando a instância da janela principal
            notification_manager.show_notification(f"Arquivo modelo não encontrado!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return

        # Criar uma cópia do arquivo modelo
        caminho_destino = filedialog.askdirectory()

        if not caminho_destino:  # Se o usuário cancelar a seleção
            notification_manager = NotificationManager(root)  # passando a instância da janela principal
            notification_manager.show_notification(f"Nenhum diretório selecionado!", NotifyType.WARNING, bg_color="#404040", text_color="#FFFFFF")
            return
        
        # Criar o nome do arquivo de destino
        nome_arquivo_destino = os.path.join(caminho_destino, nome_arquivo)

        shutil.copy(caminho_modelo, nome_arquivo_destino)

        # Abrir o arquivo Excel copiado
        workbook = load_workbook(nome_arquivo_destino)
        sheet_dados = workbook["DADOS"]  # Planilha onde os dados serão preenchidos
        sheet_principal = workbook["Planilha1"]  # Planilha onde será aplicada a validação

        # Preenchendo os dados
        data_atual = datetime.now().strftime("%d/%m/%Y")
        sheet_principal["D5"] = nome_fornecedor
        sheet_principal["D11"] = nome_usuario
        sheet_principal["D16"] = contrato if contrato else "ESCRITÓRIO"

        if tipo_pagamento == "FATURAMENTO":
            sheet_principal["D41"] = "FATURADO"
        else:
            sheet_principal["D41"] = tipo_pagamento

        sheet_principal["B47"] = f"Assinatura: {nome_usuario}"
        sheet_principal["B48"] = f"Data: {data_atual}"

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

        '''Restaurando a Validação de Dados'''
        workbook.active = sheet_principal
        dv = DataValidation(
            type="list", 
            formula1='"SEM CUSTO PARA ENTREGA,COM CUSTO PARA ENTREGA"', 
            showDropDown=False,
            allow_blank=True
        )
        sheet_principal.add_data_validation(dv)
        dv.add("D42")  # Aplicando a validação na célula D11

        # Salvar e fechar o arquivo
        workbook.save(nome_arquivo_destino)
        workbook.close()

        notification_manager = NotificationManager(root)  # passando a instância da janela principal
        notification_manager.show_notification(f"Sucesso!\nArquivo salvo no local selecionado.", NotifyType.SUCCESS, bg_color="#404040", text_color="#FFFFFF")
    except Exception as e:
        notification_manager = NotificationManager(root)  # passando a instância da janela principal
        notification_manager.show_notification(f"Erro ao gerar o arquivo Excel: {e}", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")        
        # logging.error("Erro ao gerar o arquivo Excel: ", exc_info=True)