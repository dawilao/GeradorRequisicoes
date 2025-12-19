import requests
import json
import sys
from packaging import version
import webbrowser
import os

def get_version():
    """Recupera a versão atual do aplicativo do arquivo config.py."""
    try:
        from .config import VERSION
        return VERSION
    except Exception as e:
        # Versão fallback caso não consiga importar
        return "3.1.0"

def check_for_updates():
    """Verifica se há uma versão mais recente disponível."""
    current_version = get_version()  # Obtém a versão atual
    try:
        # URL para um arquivo JSON que contém informações da versão mais recente
        # Pode ser um arquivo no GitHub ou em qualquer servidor web
        version_url = "https://raw.githubusercontent.com/dawilao/GeradorRequisicoes/main/version.json"
        
        response = requests.get(version_url, timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            latest_version = version_info["version"]
            download_url = version_info["download_url"]
            
            # Adicionando logs de depuração
            print(f"Versão atual: {current_version}")
            print(f"Versão online: {latest_version}")
            
            # Compara versões explicitamente para garantir
            current_v = version.parse(current_version)
            latest_v = version.parse(latest_version)
            needs_update = latest_v > current_v
            
            print(f"Necessita atualização: {needs_update}")
            
            if needs_update:
                show_update_dialog(latest_version, download_url, current_version)
                return False  # Versão desatualizada
            return True  # Versão atualizada
        else:
            # Se não conseguir verificar, permite o uso (mais amigável)
            print(f"Não foi possível verificar atualizações. Status: {response.status_code}")
            return True
    except Exception as e:
        print(f"Erro ao verificar atualizações: {e}")
        # Em caso de erro, permite o uso
        return True

def show_update_dialog(latest_version, download_url, current_version):
    """Mostra diálogo de atualização e opções para o usuário."""
    try:
        # Tenta importar e usar a interface gráfica
        from .tela_update import TelaUpdate
        dialog = TelaUpdate(current_version, latest_version, download_url)
        dialog.show()
    except ImportError:
        # Fallback para versão de console se não conseguir importar a interface gráfica
        print("\n" + "="*50)
        print(f"ATUALIZAÇÃO OBRIGATÓRIA DISPONÍVEL!")
        print(f"Sua versão: {current_version}")
        print(f"Nova versão: {latest_version}")
        print("\nVocê precisa atualizar para continuar usando o PDFMaster.")
        print("="*50)
        
        while True:
            choice = input("\nDeseja: [1] Baixar a nova versão agora, [2] Sair? ").strip()
            if choice == "1":
                print("Abrindo página de download...")
                webbrowser.open(download_url)
                sys.exit(0)
            elif choice == "2":
                print("Saindo do aplicativo. Por favor, atualize para usar novamente.")
                sys.exit(0)
