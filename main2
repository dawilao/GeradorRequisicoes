

import locale

locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')

# Definir o caminho absoluto para o diretório de logs
log_dir = os.path.join(os.getcwd(), "logs")

# Criar diretório "logs" se não existir
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "app.log"), encoding='utf-8'),  # Agora será salvo dentro da pasta logs
        logging.StreamHandler()
    ]
)



# Conectar ao banco de dados (se não existir, ele será criado)
conn = sqlite3.connect(r'C:\Users\Taiane Marques\Desktop\meu_banco.db')
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
    data_criacao TEXT, 
    hora_criacao TEXT
)
''')

def fechar_conexao():
    conn.close()

# Registrar a função para ser chamada ao sair do programa
atexit.register(fechar_conexao)

# Função para inserir dados na tabela
def inserir_dados(nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
                  contrato, motivo, valor, tipo_pagamento, tecnicos, saida_destino, 
                  competencia, porcentagem):
    # Obtendo a data e hora atuais
    data_criacao = datetime.now().strftime('%d/%m/%Y')
    hora_criacao = datetime.now().strftime('%H:%M:%S')
    
    cursor.execute('''
    INSERT INTO registros (
        nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
        contrato, motivo, valor, tipo_pagamento, tecnicos, saida_destino, 
        competencia, porcentagem, data_criacao, hora_criacao
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
          contrato, motivo, valor, tipo_pagamento, tecnicos, saida_destino, 
          competencia, porcentagem, data_criacao, hora_criacao))
    
    conn.commit()

