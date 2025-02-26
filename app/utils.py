import re

def arrumar_texto(texto):
    return ' '.join(texto.strip().split()) if texto else ''

def verificar_se_numero(texto):
    try:
        if not texto:
            return ""  # Valor padrão caso o campo esteja vazio
        # Se for um número, chama a função arrumar_numero
        resultado = arrumar_numero(texto)
        return resultado
    except ValueError:
        return ValueError

def arrumar_numero(texto):
    if not texto:
        return ""  # Valor padrão caso o campo esteja vazio

    texto = texto.replace(" ", "")  # Remove todos os espaços

    try:
        # Troca o ponto por um marcador temporário "X", troca a vírgula por ponto e depois troca "X" por vírgula
        numero = float(texto.replace(".", "").replace(",", "."))
        return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return ""  # Retorna um valor padrão caso a conversão falhe

def valida_porcentagem(valor):
    if not valor:
        return ""

    if not valor.isdigit():
        return ValueError

    # Converte para inteiro e verifica se está dentro do intervalo permitido
    numero = int(valor)
    if not (1 <= numero <= 100):
        return "RangeError"
    else:
        return numero
    
def valida_os(texto: str):
    """
    Valida e ajusta um número de OS de acordo com os critérios:
    - Remove espaços extras, vírgulas e substitui '-' e '.' por '/'
    - Deve conter apenas números e os caracteres '/', '\'
    - Não pode conter letras ou outros caracteres especiais
    
    Retorna a OS ajustada se válida, uma string vazia se a entrada for nula,
    ou "OS_invalida" caso contenha caracteres inválidos.
    """
    def arrumar_os(texto_recebido):
        texto_recebido = ''.join(texto_recebido.strip().split())  # Remove espaços extras
        texto_recebido = texto_recebido.replace(",", "").replace("-", "/").replace(".", "/").replace(" ", "")
        return texto_recebido

    if not texto:
        return ""

    texto = arrumar_os(texto)

    if re.fullmatch(r"[\d./\\]+", texto):
        return texto
    else:
        return "OS_invalida"