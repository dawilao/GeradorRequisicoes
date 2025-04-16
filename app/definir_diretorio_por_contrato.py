"""
Módulo para gerenciar a criação de diretórios baseados em contratos
e interações com o Windows Explorer.

Este módulo contém funções para salvar arquivos em diretórios mapeados por contrato,
abrir o Explorer em um diretório específico e verificar se o Explorer 
já está aberto nesse caminho. 

Funções principais:
- salvar_arquivo_em_diretorio: Retorna o caminho do diretório onde o arquivo deve ser salvo, 
  criando as pastas de ano e mês se necessário.
- explorer_esta_aberto_no_caminho: Verifica se alguma janela do Explorer está aberta 
  no caminho desejado.
- abrir_explorer_se_necessario: Abre o Explorer no caminho desejado se ele ainda não estiver aberto.
"""

import os
import subprocess
from datetime import datetime

from tkinter import Tk, filedialog

import win32com.client

# Dicionário com os diretórios base dos contratos
CONTRATOS = {
    "C. O. SALVADOR - BA - 2877": (
        r"G:\Meu Drive\1 - C. O SALVADOR - CTR 2021.7421.2877\7 - REQUISIÇÕES\REQUISIÇÃO"
    ),
    "C. O. SANTA CATARINA - SC - 5023": (
        r"G:\Meu Drive\2 - C. O SANTA CATARINA - CTR 2021.7421.5023\06 - REQUISIÇÕES"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. RIO GRANDE DO SUL - RS - 5525": (
        r"G:\Meu Drive\3 - C. O RIO GRANDE DO SUL - CTR 2022.7421.5525\7 - REQUISIÇÕES"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. RIO DE JANEIRO - RJ - 0494": (
        r"G:\Meu Drive\4 - C. O RIO DE JANEIRO - CTR 2023.7421.0494\7 - REQUISIÇÕES"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. NITERÓI - RJ - 1380": (
        r"G:\Meu Drive\5 - C. O NITERÓI - CTR 2023.7421.1380\7 - REQUISIÇÕES"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. BELO HORIZONTE - BH - 2054": (
        r"G:\Meu Drive\6 - C. O BELO HORIZONTE - CTR 2024.7421.2054\6 - REQUISIÇÃO"
    ),
    "C. O. RECIFE - PE - 5254": (
        r"G:\Meu Drive\8 - C. O RECIFE - CTR 2023.7421.5254\7 - REQUISIÇÕES"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. MANAUS - AM - 7649": (
        r"G:\Meu Drive\7 - C. O MANAUS - CTR 2023.7421.7649\07 - REQUISIÇÕES"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. VOLTA REDONDA - RJ - 0215": (
        r"G:\Meu Drive\10 - C. O VOLTA REDONDA - CTR 2025.7421.0215\6 - REQUISIÇÃO"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. RONDÔNIA - RD - 0710": (
        r"G:\Meu Drive\9 - C. O RONDÔNIA - CTR 2025.7421.0710\6 - REQUISIÇÃO"
        r"\ORDEM DE COMPRA"
    ),
    "ATA BB CURITIBA - 0232": (
        r"G:\Meu Drive\11 - ATA CURITIBA BB - CTR 2025.7421.0232\6 - REQUISIÇÃO"
    ),
    "C. E. MANAUS - 1593": (
        r"G:\Meu Drive\24 - C. E MANAUS - CTR 2025.7421.1593\6 - REQUISIÇÃO"
        r"\ORDEM DE COMPRA"
    ),
    "CAIXA BAHIA - 4922.2024": (
        r"G:\Meu Drive\13 - CAIXA ECONÔMICA FEDERAL\1 - C.E.F - BAHIA - ATA 4922.2024"
        r"\6 - REQUISIÇÃO"
    ),
    "CAIXA CURITIBA - 534.2025": (
        r"G:\Meu Drive\13 - CAIXA ECONÔMICA FEDERAL\3 - C.E.F - CURITIBA - ATA"
        r" 534.2025\6 - REQUISIÇÃO"
    ),
    "CAIXA MANAUS - 4569.2024": (
        r"G:\Meu Drive\13 - CAIXA ECONÔMICA FEDERAL\2 - C.E.F - MANAUS - ATA"
        r" 4569.2024\6 - REQUISIÇÃO"
    ),
    "INFRA CURITIBA - 1120": (
        r"G:\Meu Drive\12 - INFRA CURITIBA BB - CTR 2025.7421.1120\6 - REQUISIÇÃO"
    )
}

# Lista com os meses no formato desejado
MESES = [
    "01 - JANEIRO", "02 - FEVEREIRO", "03 - MARÇO", "04 - ABRIL",
    "05 - MAIO", "06 - JUNHO", "07 - JULHO", "08 - AGOSTO",
    "09 - SETEMBRO", "10 - OUTUBRO", "11 - NOVEMBRO", "12 - DEZEMBRO"
]

def salvar_arquivo_em_diretorio(contrato: str) -> str:
    """
    Retorna o caminho do diretório onde o arquivo deve ser salvo.
    Cria as pastas de ano e mês caso não existam.
    Se o contrato não estiver mapeado, pergunta ao usuário o local.

    Parâmetros:
        contrato (str): Nome do contrato.

    Retorna:
        str: Caminho completo do diretório onde o arquivo será salvo.
    """
    agora = datetime.now()
    ano = str(agora.year)
    mes_nome = MESES[agora.month - 1]

    if contrato in CONTRATOS:
        base_path = CONTRATOS[contrato]
        caminho_destino = os.path.join(base_path, ano, mes_nome)
        os.makedirs(caminho_destino, exist_ok=True)
        return caminho_destino

    print(f"Contrato '{contrato}' não está mapeado.")
    print("Por favor, selecione a pasta onde deseja salvar o arquivo.")

    root = Tk()
    root.withdraw() # Evita que a janela principal do Tkinter apareça
    caminho_custom = filedialog.askdirectory(title="Selecione o diretório para salvar o arquivo")

    if caminho_custom:
        return caminho_custom

    raise ValueError("Nenhum diretório foi selecionado.")

def explorer_esta_aberto_no_caminho(caminho_desejado: str) -> bool:
    """
    Verifica se alguma janela do Explorer está aberta no caminho desejado.

    Parâmetros:
        caminho_desejado (str): O caminho desejado a ser verificado.

    Retorna:
        bool: True se o Explorer estiver aberto no caminho desejado, False caso contrário.
    """
    caminho_desejado = os.path.normpath(caminho_desejado).lower()
    shell = win32com.client.Dispatch("Shell.Application")
    for window in shell.Windows():
        try:
            if window.Name == "Explorador de Arquivos":
                path = os.path.normpath(window.Document.Folder.Self.Path).lower()
                if caminho_desejado == path:
                    return True
        except AttributeError as e_verifica_janela:
            print(f"Erro ao acessar atributo da janela: {e_verifica_janela}")
            continue
        except Exception as e:
            # Captura outras exceções inesperadas de forma mais geral
            print(f"Erro inesperado ao verificar janela: {e}")
            continue
    return False

def abrir_explorer_se_necessario(caminho_desejado: str):
    """
    Abre o Explorer no caminho desejado se ele ainda não estiver aberto.

    Parâmetros:
        caminho_desejado (str): O caminho a ser aberto no Explorer.
    """
    try:
        if not explorer_esta_aberto_no_caminho(caminho_desejado):
            subprocess.Popen(['explorer', caminho_desejado])
    except subprocess.SubprocessError as e_abrir_explorer:
        print(
            f"Erro ao tentar abrir o Explorer no caminho {caminho_desejado}: {e_abrir_explorer}"
        )
    except OSError as e_os:
        print(
            f"Erro ao tentar abrir o Explorer no caminho {caminho_desejado}: {e_os}"
        )
