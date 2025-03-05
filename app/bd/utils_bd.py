import sqlite3

def conecta_banco_pagamentos(nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
        contrato, motivo, valor, tipo_pagamento, tecnicos, saida_destino, competencia,
        porcentagem, tipo_aquisicao):
    def inserir_dados(nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
        contrato, motivo, valor, tipo_pagamento, tecnicos, saida_destino, competencia,
        porcentagem, tipo_aquisicao):
        # Obtendo a data e hora atuais
        from datetime import datetime
        data_criacao = datetime.now().strftime('%d/%m/%Y')
        hora_criacao = datetime.now().strftime('%H:%M:%S')
        
        cursor.execute('''
        INSERT INTO registros (
            nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
            contrato, motivo, valor, tipo_pagamento, tecnicos, saida_destino, competencia,
            porcentagem, tipo_aquisicao, data_criacao, hora_criacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
            contrato, motivo, valor, tipo_pagamento, tecnicos, saida_destino, competencia,
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
        contrato, motivo, valor, tipo_pagamento, tecnicos, saida_destino, competencia,
        porcentagem, tipo_aquisicao)

    fechar_conexao()

# Registrar a função para ser chamada ao sair do programa
# atexit.register(fechar_conexao)