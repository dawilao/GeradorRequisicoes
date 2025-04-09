import re

def arrumar_texto(texto):
    return ' '.join(texto.strip().split()) if texto else ''

def verificar_se_numero(texto):
    if not texto:
        return ""  # Valor padrão caso o campo esteja vazio

    texto = texto.upper().replace("R$", "").replace(" ", "")  # Remove "R$", espaços

    try:
        # Substitui ponto (separador de milhar) por nada e vírgula por ponto (separador decimal)
        numero = float(texto.replace(".", "").replace(",", "."))
        # Retorna número formatado no padrão brasileiro
        return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return ValueError  # Retorna um valor padrão caso a conversão falhe

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

def validar_item_pagamento(texto):
    texto_corrigido = re.sub(r"\s*-\s*", " - ", texto)
    partes = texto_corrigido.split(" - ")

    if len(partes) != 4:
        return None, None, None, "Formato inválido. Use: PREFIXO - AGÊNCIA - OS - VALOR"

    prefixo_raw, agencia, os_str, valor_str = [p.strip() for p in partes]

    # --- PREFIXO ---
    if "/" in prefixo_raw:
        try:
            parte1, parte2 = prefixo_raw.split("/")
            parte1 = parte1.zfill(4)
            parte2 = parte2.zfill(2)
            prefixo_formatado = f"{parte1}/{parte2}"
        except:
            return None, None, None, "Prefixo inválido. Use o padrão XXXX/XX."
    else:
        parte1 = prefixo_raw.zfill(4)
        prefixo_formatado = f"{parte1}/00"

    # --- AGÊNCIA ---
    if not agencia:
        return None, None, None, "Agência não pode estar vazia."

    # --- OS ---
    if not os_str.isdigit() or len(os_str) <= 4:
        return None, None, None, "OS inválida. Deve conter mais de 4 dígitos numéricos."

    # --- VALOR ---
    valor_limpo = valor_str.upper().replace("R$", "").strip()
    valor_numerico = re.sub(r"[^\d,\.]", "", valor_limpo)

    valor_formatado = verificar_se_numero(valor_numerico)

    if not valor_formatado or isinstance(valor_formatado, Exception):
        return None, None, None, "Valor inválido."

    valor_com_rs = f"R$ {valor_formatado}"
    valor_puro = valor_formatado  # Já está formatado sem o R$

    # --- Descrição base (sem o valor) ---
    descricao_base = f"{prefixo_formatado} - {agencia} - {os_str}"

    # --- Descrição final com o valor ---
    descricao_final = f"{descricao_base} - {valor_com_rs}"

    return descricao_final, valor_puro, descricao_base, None
