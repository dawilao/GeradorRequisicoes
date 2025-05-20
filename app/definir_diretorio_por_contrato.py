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
import sqlite3

# Lista com os meses no formato desejado
MESES = [
    "01 - JANEIRO", "02 - FEVEREIRO", "03 - MARÇO", "04 - ABRIL",
    "05 - MAIO", "06 - JUNHO", "07 - JULHO", "08 - AGOSTO",
    "09 - SETEMBRO", "10 - OUTUBRO", "11 - NOVEMBRO", "12 - DEZEMBRO"
]

def obter_caminho_base_contrato(contrato: str) -> str:
    """
    Consulta o banco de dados SQLite para obter o caminho base de salvamento
    associado a um contrato específico.

    Esta função tenta se conectar ao banco de dados 'contratos.db' localizado
    preferencialmente na pasta local do projeto. Caso não consiga, tenta uma
    segunda localização no Google Drive (uso remoto). Em seguida, realiza a
    busca pelo nome do contrato e retorna o caminho correspondente, se encontrado.

    Parâmetros:
        contrato (str): Nome completo do contrato conforme armazenado no banco.

    Retorna:
        str: Caminho base associado ao contrato, se encontrado.
        None: Se o contrato não for encontrado ou ocorrer algum erro.
    """
    try:
        try:
            conn = sqlite3.connect(r'app\bd\contratos.db')
        except sqlite3.Error:
            conn = sqlite3.connect(
                r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\contratos.db'
            )

        cursor = conn.cursor()
        cursor.execute("SELECT caminho FROM contratos WHERE nome = ?", (contrato,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            return resultado[0]
        return None
    except Exception as e:
        print(f"Erro ao consultar caminho do contrato no banco: {e}")
        return None

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

    base_path = obter_caminho_base_contrato(contrato)
    if base_path:
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
