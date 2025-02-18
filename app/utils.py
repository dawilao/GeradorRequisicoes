
def arrumar_texto(texto):
    return ' '.join(texto.strip().split()) if texto else ''

def arrumar_os(texto):
    if texto:
        texto = ''.join(texto.strip().split())  # Remove espaços extras sem adicionar espaço entre palavras
        texto = texto.replace(",", "").replace("-", "").replace(".", "")  # Aplica as substituições corretamente
        return texto
    return ''

def verificar_se_numero(texto):
    try:
        if not texto:
            return ""  # Valor padrão caso o campo esteja vazio
        # Tenta converter o valor em número
        float(texto.replace(",", "."))
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
        numero = float(texto.replace(",", "."))
        return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return ""  # Retorna um valor padrão caso a conversão falhe
