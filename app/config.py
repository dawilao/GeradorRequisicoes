"""
Configurações centralizadas do programa.
"""

# Informações da versão
VERSION = "3.1.0"
APP_NAME = "Gerador de Requisições"
AUTHOR = "Dawison Nascimento"
DESCRIPTION = "Sistema para geração de requisições"

# Metadados
BUILD_DATE = "2024"
COPYRIGHT = f"© {BUILD_DATE} {AUTHOR}"

# Configurações gerais
DEBUG = False
LOG_LEVEL = "INFO"

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