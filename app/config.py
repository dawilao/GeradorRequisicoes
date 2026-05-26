"""
Configurações centralizadas do programa.
"""

# Informações da versão
VERSION = "3.2.1"
APP_NAME = "Gerador de Requisições"
AUTHOR = "Dawison Nascimento"
DESCRIPTION = "Sistema para geração de requisições"

# Metadados
BUILD_DATE = "2024"
COPYRIGHT = f"© {BUILD_DATE} {AUTHOR}"

# Configurações gerais
DEBUG = False
LOG_LEVEL = "INFO"

# Caminhos dos bancos de dados (fallback: local → corporativo)
DB_LOGIN_PATHS = [
    r'app\bd\login.db',
    r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\login.db',
]

DB_DADOS_PATHS = [
    r'app\bd\dados.db',
    r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\dados.db',
]

DB_CONTRATOS_PATHS = [
    r'app\bd\contratos.db',
    r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\contratos.db',
]

# Caminhos do ícone da aplicação
ICON_PATHS = [
    r'app\assets\GerReq_icon.ico',
    r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\assets\GerReq_icon.ico',
]

# Informações completas da versão
def get_version_info():
    """Retorna informações completas da versão."""
    return {
        "version": VERSION,
        "app_name": APP_NAME,
        "author": AUTHOR,
        "description": DESCRIPTION,
        "build_date": BUILD_DATE,
        "copyright": COPYRIGHT
    }

def get_version_string():
    """Retorna uma string formatada com a versão."""
    return f"{APP_NAME} v{VERSION}"