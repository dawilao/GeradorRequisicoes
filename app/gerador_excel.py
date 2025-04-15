from openpyxl import load_workbook
from openpyxl.styles import Alignment
import os, shutil, time
from tkinter import filedialog, messagebox
from datetime import datetime
from openpyxl.worksheet.datavalidation import DataValidation
from app.CTkFloatingNotifications import NotificationManager, NotifyType
from app.definir_diretorio_por_contrato import salvar_arquivo_em_diretorio
from app.definir_diretorio_por_contrato import *


def gerar_excel(
        root, nome_arquivo, tipo_servico, nome_fornecedor, os_num, prefixo, agencia,
        contrato, nome_usuario, tipo_pagamento, departamento, valor, tecnicos,
        usuarios_varios_departamentos, usuarios_gerais, motivo, descricao_itens
    ):
    """
    Gera um arquivo Excel de requisição a partir de um modelo padrão, preenchendo-o com dados fornecidos e aplicando validações dinâmicas.

    Esta função copia um modelo de ordem de compra, preenche automaticamente campos como fornecedor, contrato, usuário, tipo de pagamento, entre outros, e insere descrições específicas conforme o tipo de serviço. Dependendo do perfil do usuário, aplica diferentes validações de departamento. O arquivo é salvo com verificação de duplicidade no nome, e aberto automaticamente após a geração.

    Parâmetros:
    -----------
    root : Tk
        Janela principal da interface gráfica para exibição de mensagens ao usuário.
    nome_arquivo : str
        Nome desejado para o arquivo Excel gerado.
    tipo_servico : str
        Tipo de serviço solicitado (ex: "RELATÓRIO EXTRA", "ADIANTAMENTO/PAGAMENTO PARCEIRO").
    nome_fornecedor : str
        Nome do fornecedor a ser incluído na planilha.
    os_num : str or int
        Número da Ordem de Serviço (pode ser omitido).
    prefixo : str
        Prefixo da OS, utilizado junto com a agência.
    agencia : str
        Agência vinculada à OS.
    contrato : str
        Nome do contrato ou "ESCRITÓRIO" se não aplicável.
    nome_usuario : str
        Usuário responsável pela requisição.
    tipo_pagamento : str
        Tipo de pagamento selecionado.
    departamento : str
        Departamento vinculado à requisição.
    valor : str
        Valor do serviço solicitado.
    usuarios_varios_departamentos : list[str]
        Lista de usuários com permissão para escolher entre múltiplos departamentos.
    usuarios_gerais : list[str]
        Lista de usuários com departamento fixo.
    motivo : str
        Motivo da requisição.
    descricao_itens : str
        Descrição detalhada dos itens/serviços, separados por quebra de linha.

    Retorno:
    --------
    None

    Efeitos colaterais:
    -------------------
    - Exibe mensagens de sucesso, erro ou alerta.
    - Salva e abre automaticamente o arquivo Excel gerado.
    - Aplica validações de dados em campos específicos da planilha.
    - Gera versões incrementais do arquivo se já existir no diretório.

    Exceções tratadas:
    ------------------
    - Arquivo modelo ausente.
    - Falha ao selecionar diretório de destino.
    - Erros na manipulação da planilha ou no processo de geração.
    """
    notification_manager = NotificationManager(root)

    try:
        caminho_modelo = r"G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\dist\MODELO NOVO 2024 - ORDEM DE COMPRA.xlsx"

        if not os.path.exists(caminho_modelo):
            notification_manager.show_notification(f"Arquivo modelo não encontrado!", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            return

        try:
            caminho_destino = salvar_arquivo_em_diretorio(contrato)

            base_nome, extensao = os.path.splitext(nome_arquivo)
            nome_arquivo_destino = os.path.join(caminho_destino, nome_arquivo)

            contador = 1
            while os.path.exists(nome_arquivo_destino):
                novo_nome = f"{base_nome}_Cópia {contador}{extensao}"
                nome_arquivo_destino = os.path.join(caminho_destino, novo_nome)
                contador += 1

            shutil.copy(caminho_modelo, nome_arquivo_destino)

        except Exception as e:
            notification_manager.show_notification(
                f"Falha ao definir diretório: {e}", NotifyType.WARNING, bg_color="#404040", text_color="#FFFFFF"
            )
            return

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

        linha_inicial = 19
        limite_caracteres = 45
        altura_por_linha = 15  # Altura padrão por linha
        sheet_principal.column_dimensions["E"].width = 15
        if tipo_servico in {"ABASTECIMENTO", "ESTACIONAMENTO", "HOSPEDAGEM"}:
            sheet_principal[f"C{linha_inicial}"].alignment = Alignment(
                wrap_text=True, horizontal='center', vertical='center'
            )

            sheet_principal[f"B{linha_inicial}"] = "1"
            sheet_principal[f"C{linha_inicial}"] = f"{tipo_servico}: {tecnicos}"

            if len(f"{tipo_servico}: {tecnicos}") > limite_caracteres:
                '''Dobra a altura da linha quando a quantidade de caracteres ultrapassa o especificado em limite_caracteres''' 
                qtd_linhas = (len(f"{tipo_servico}: {tecnicos}") // limite_caracteres) + 1
                sheet_principal.row_dimensions[linha_inicial].height = qtd_linhas * altura_por_linha
            
            sheet_principal[f"F{linha_inicial}"] = 1
            sheet_principal[f"G{linha_inicial}"] = valor
        elif tipo_servico == "RELATÓRIO EXTRA":
            descricao_lista = descricao_itens.split("\n")

            for i, descricao in enumerate(descricao_lista):
                sheet_principal[f"C{linha_inicial + i}"].alignment = Alignment(
                    wrap_text=False, horizontal='center', vertical='center'
                )
                sheet_principal[f"B{linha_inicial + i}"] = f"{i + 1}"
                sheet_principal[f"C{linha_inicial + i}"] = descricao
                sheet_principal[f"F{linha_inicial + i}"] = 1
                sheet_principal[f"G{linha_inicial + i}"] = "80,00"

                if len(descricao) > limite_caracteres:
                    qtd_linhas = (len(descricao) // limite_caracteres) + 1
                    sheet_principal.row_dimensions[linha_inicial + i].height = qtd_linhas * altura_por_linha 
        elif tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
            descricao_lista = descricao_itens.split("\n")

            for i, descricao in enumerate(descricao_lista):
                sheet_principal[f"C{linha_inicial + i}"].alignment = Alignment(
                    wrap_text=False, horizontal='center', vertical='center'
                )
                sheet_principal[f"B{linha_inicial + i}"] = f"{i + 1}"
                sheet_principal[f"C{linha_inicial + i}"] = descricao
                sheet_principal[f"F{linha_inicial + i}"] = 1

                if len(descricao) > limite_caracteres:
                    qtd_linhas = (len(descricao) // limite_caracteres) + 1
                    sheet_principal.row_dimensions[linha_inicial + i].height = qtd_linhas * altura_por_linha                    

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
            abrir_explorer_se_necessario(caminho_destino)
            time.sleep(1.2)
            os.startfile(nome_arquivo_destino)
        except FileNotFoundError:
            notification_manager.show_notification(f"Arquivo não encontrado após a geração.", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")
            print(FileNotFoundError)
    except Exception as e:
        notification_manager.show_notification(f"Erro ao gerar o arquivo Excel: {e}", NotifyType.ERROR, bg_color="#404040", text_color="#FFFFFF")