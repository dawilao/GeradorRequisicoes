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

def valida_prefixo(prefixo_raw):
    if not prefixo_raw:
        return ""
    else:
        if "/" in prefixo_raw:
            try:
                parte1, parte2 = prefixo_raw.split("/")
                parte1 = parte1.zfill(4)
                parte2 = parte2.zfill(2)
                prefixo_formatado = f"{parte1}/{parte2}"
                if not re.fullmatch(r"\d{4}/\d{2}", prefixo_formatado):
                    return "Prefixo inválido"
            except:
                return "Prefixo inválido"
        elif prefixo_raw.isdigit():
            parte1 = prefixo_raw.zfill(4)
            prefixo_formatado = f"{parte1}/00"
        else:
            return "Prefixo inválido"
        
        return prefixo_formatado

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

def validar_item_pagamento(texto, tipo_servico, possui_os):
    """
    Valida e formata o texto de entrada para o tipo de serviço "ADIANTAMENTO/PAGAMENTO PARCEIRO".
    - Se possui_os == "SIM", o padrão esperado é "PREFIXO - AGENCIA - OS - PORCENTAGEM".
    - Se possui_os == "NÃO", o padrão esperado é "MOTIVO - PORCENTAGEM".
    """
    texto_corrigido = re.sub(r"\s*-\s*", " - ", texto)
    partes = texto_corrigido.split(" - ")

    if tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
        if possui_os == "SIM": # Padrão "PREFIXO - AGENCIA - OS - PORCENTAGEM"
            if len(partes) != 4:
                return None, None, "Formato inválido. Use: PREFIXO - AGÊNCIA - OS - % DO ADIANTAMENTO"

            prefixo_raw, agencia, os_str, percentual_raw = [p.strip() for p in partes]

            # --- VALIDAÇÃO DO PERCENTUAL ---
            # Remove o símbolo % se houver
            percentual_limpo = percentual_raw.replace("%", "").strip()

            # Verifica se é numérico puro
            if not percentual_limpo.isdigit():
                return None, None, "Percentual inválido. Deve conter apenas números, com ou sem '%'."

            percentual_valor = int(percentual_limpo)

            if percentual_valor < 1 or percentual_valor > 100:
                return None, None, "Percentual inválido. Deve estar entre 1 e 100."

            # Reaplica o símbolo de % para exibir formatado
            percentual = f"{percentual_valor}%"

            valor_formatado = None
            valor_com_rs = None
        else:  # Padrão "MOTIVO - PORCENTAGEM"
            if len(partes) != 2:
                return None, None, "Formato inválido. Use: MOTIVO - % DO ADIANTAMENTO"

            motivo, percentual_raw = [p.strip() for p in partes]

            # --- VALIDAÇÃO DO PERCENTUAL ---
            percentual_limpo = percentual_raw.replace("%", "").strip()
            if not percentual_limpo.isdigit():
                return None, None, "Percentual inválido. Deve conter apenas números, com ou sem '%'."

            percentual_valor = int(percentual_limpo)
            if percentual_valor < 1 or percentual_valor > 100:
                return None, None, "Percentual inválido. Deve estar entre 1 e 100."

            percentual = f"{percentual_valor}%"

            # --- MOTIVO ---
            if not motivo:
                return None, None, "Motivo não pode estar vazio."

            # --- Descrição final ---
            descricao_final = f"{motivo} - ADIANTAMENTO DE {percentual}"

            return descricao_final, None, None

    else:  # PADRÃO PARA PAGAMENTO EXTRA
        if len(partes) != 4:
            return None, None, "Formato inválido. Use: PREFIXO - AGÊNCIA - OS - VALOR"

        prefixo_raw, agencia, os_str, valor_str = [p.strip() for p in partes]

        if not valor_str:
            return None, None, "Valor não pode estar vazio."

        valor_limpo = valor_str.upper().replace("R$", "").strip()
        valor_numerico = re.sub(r"[^\d,\.]", "", valor_limpo)
        valor_formatado = verificar_se_numero(valor_numerico)

        if not valor_formatado or isinstance(valor_formatado, Exception):
            return None, None, "Valor inválido."

        valor_com_rs = f"R$ {valor_formatado}"

    # --- PREFIXO ---
    if "/" in prefixo_raw:
        try:
            parte1, parte2 = prefixo_raw.split("/")
            parte1 = parte1.zfill(4)
            parte2 = parte2.zfill(2)
            prefixo_formatado = f"{parte1}/{parte2}"
            if not re.fullmatch(r"\d{4}/\d{2}", prefixo_formatado):
                return None, None, "Prefixo inválido. Use o padrão XXXX/XX."
        except:
            return None, None, "Prefixo inválido. Use o padrão XXXX/XX."
    elif prefixo_raw.isdigit():
        parte1 = prefixo_raw.zfill(4)
        prefixo_formatado = f"{parte1}/00"
    else:
        return None, None, "Prefixo inválido. Use o padrão XXXX/XX."

    # --- AGÊNCIA ---
    if not agencia:
        return None, None, "Agência não pode estar vazia."

    # --- OS ---
    os_str = valida_os(os_str)
    if os_str == "OS_invalida":
        return None, None, "OS inválida. Não deve conter textos."

    if len(os_str) <= 4:
        return None, None, "OS inválida. Deve conter mais de 4 dígitos numéricos."

    # --- Descrição base e final ---
    descricao_base = f"{prefixo_formatado} - {agencia} - {os_str}"

    if tipo_servico == "ADIANTAMENTO/PAGAMENTO PARCEIRO":
        descricao_final = f"{descricao_base} - ADIANTAMENTO DE {percentual}"
    else:
        descricao_final = f"{descricao_base} - {valor_com_rs}"

    return descricao_final, descricao_base, None