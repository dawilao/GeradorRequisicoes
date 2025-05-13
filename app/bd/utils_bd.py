import sqlite3

def conecta_banco_pagamentos(nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
        contrato, motivo, valor, tipo_pagamento, tecnicos, competencia,
        porcentagem, tipo_aquisicao):
    def inserir_dados(nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
        contrato, motivo, valor, tipo_pagamento, tecnicos, competencia,
        porcentagem, tipo_aquisicao):
        # Obtendo a data e hora atuais
        from datetime import datetime
        data_criacao = datetime.now().strftime('%d/%m/%Y')
        hora_criacao = datetime.now().strftime('%H:%M:%S')
        
        cursor.execute('''
        INSERT INTO registros (
            nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
            contrato, motivo, valor, tipo_pagamento, tecnicos, competencia,
            porcentagem, tipo_aquisicao, data_criacao, hora_criacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
            contrato, motivo, valor, tipo_pagamento, tecnicos, competencia,
            porcentagem, tipo_aquisicao, data_criacao, hora_criacao))
        
        conn.commit()

    def fechar_conexao():
        conn.close()

    try:
        conn = sqlite3.connect(r'app\bd\dados.db')
    except Exception:
        conn = sqlite3.connect(r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\dados.db')
    
    cursor = conn.cursor()

    # Criar uma tabela no banco de dados
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_usuario TEXT,
        tipo_servico TEXT,
        nome_fornecedor TEXT,
        prefixo TEXT,
        agencia TEXT,
        os_num TEXT,
        contrato TEXT,
        motivo TEXT,
        valor REAL,
        tipo_pagamento TEXT,
        tecnicos TEXT,
        saida_destino TEXT,
        competencia TEXT,
        porcentagem TEXT,
        tipo_aquisicao TEXT,
        data_criacao TEXT, 
        hora_criacao TEXT
    )
    ''')

    inserir_dados(nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
        contrato, motivo, valor, tipo_pagamento, tecnicos, competencia,
        porcentagem, tipo_aquisicao)

    fechar_conexao()

def acessa_bd_contratos(contrato: str = None):
    """
    Se 'contrato' for fornecido, retorna (departamento, sigla) do contrato.
    Se 'contrato' for None, retorna a lista ordenada de todos os contratos.

    Parâmetros:
        contrato (str, opcional): Nome exato do contrato ou None.

    Retornos:
        - Tupla (departamento, sigla) se contrato for fornecido.
        - Lista de contratos ordenada se contrato for None.
    """
    try:
        try:
            conn = sqlite3.connect(r'app\bd\contratos.db')
        except sqlite3.Error:
            conn = sqlite3.connect(
                r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\contratos.db'
            )

        cursor = conn.cursor()

        if contrato is None:
            cursor.execute("SELECT nome FROM contratos")
            resultados = cursor.fetchall()
            conn.close()
            return sorted([row[0] for row in resultados])

        cursor.execute("SELECT departamento, sigla FROM contratos WHERE nome = ?", (contrato,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            return resultado  # (departamento, sigla)
        else:
            return ("", "Sigla não encontrada")

    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        if contrato is None:
            # Lista de fallback
            contratos = [
                "ESCRITÓRIO", "C. O. BELO HORIZONTE - BH - 2054", "C. O. MANAUS - AM - 7649", "C. O. NITERÓI - RJ - 1380",
                "C. O. RECIFE - PE - 5254", "C. O. RIO DE JANEIRO - RJ - 0494", "C. O. RIO GRANDE DO SUL - RS - 5525",
                "C. O. RONDÔNIA - RD - 0710", "C. O. SALVADOR - BA - 2877", "C. O. SANTA CATARINA - SC - 5023",
                "C. O. VOLTA REDONDA - RJ - 0215", "ATA BB CURITIBA - 0232", "C. E. MANAUS - 1593",
                "CAIXA BAHIA - 4922.2024", "CAIXA CURITIBA - 534.2025", "CAIXA MANAUS - 4569.2024", "INFRA CURITIBA - 1120"
            ]
            return sorted(contratos)
        else:
            return ("", "Sigla não encontrada")
