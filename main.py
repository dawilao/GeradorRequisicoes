__author__ = "Dawison Nascimento"
__status__ = "Stable"
__license__ = "MIT license"
__copyright__ = "Copyright (c) 2025 Dawison Nascimento and other contributors"
__maintainer__ = "Dawison Nascimento"
__email__ = "daw_afk@tutamail.com"
__url__ = "https://github.com/dawilao/GeradorSolicitacaoCompras"

from app.version_checker import check_for_updates
from app.ui_tela_login import janela_login

def main():
    # Verificar atualizações antes de iniciar o aplicativo
    if not check_for_updates():
        # Se a função retornar False, significa que uma atualização é necessária
        # A função já mostra o diálogo e encerra o aplicativo
        return

    janela_login()

if __name__ == "__main__":
    main()