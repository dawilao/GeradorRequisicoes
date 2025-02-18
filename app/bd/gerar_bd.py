import sqlite3
import random
import os

# Lista de usuários
usuarios = [
    "adriana", "amanda", "carlos", "daniel", "dawison",
    "felipec", "felipem", "gabriel", "guilherme", "cardoso",
    "igor", "iure", "joaogabriel", "lucasassuncao", "lucashebert", "mateus",
    "tacio", "taiane", "vinicius"
]

nome_completo = [
    "ADRIANA BARRETO", "AMANDA SAMPAIO", "CARLOS ALBERTO", "DANIEL ROMUALDO", "DAWISON NASCIMENTO",
    "FELIPE COSTA", "FELIPE MOTA", "GABRIEL BARBOSA", "GUILHERME GOMES", "HENRIQUE CARDOSO",
    "IGOR SAMPAIO", "IURE OLIVEIRA", "JOÃO GABRIEL", "LUCAS ASSUNÇÃO", "LUCAS HEBERT", "MATEUS SILVA",
    "TÁCIO BARBOSA", "TAIANE MARQUES", "VINICIUS CRUZ"
]

# Função para gerar senhas aleatórias de 6 dígitos
def gerar_senha():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

# Caminho para o banco de dados
caminho_bd = r'C:\Users\Taiane Marques\Desktop\login.db'

# Verificar e criar o diretório, se necessário
diretorio = os.path.dirname(caminho_bd)
if not os.path.exists(diretorio):
    os.makedirs(diretorio)  # Cria o diretório, caso não exista

# Conectar ao banco de dados
conn = sqlite3.connect(caminho_bd)
cursor = conn.cursor()

# Criar a tabela 'dados_login' se não existir
cursor.execute("""
    CREATE TABLE IF NOT EXISTS dados_login (
        nome_usuario TEXT PRIMARY KEY,
        nome_completo TEXT NOT NULL,
        senha TEXT NOT NULL,
        abas TEXT NOT NULL
    )
""")

# Função para verificar se o usuário já está no banco
def usuario_existe(usuario):
    cursor.execute("SELECT 1 FROM dados_login WHERE nome_usuario = ?", (usuario,))
    return cursor.fetchone() is not None

# Adicionar usuários com senhas aleatórias e abas conforme a regra
for usuario in usuarios:
    if not usuario_existe(usuario):
        senha = gerar_senha()
        # Definir as abas do usuário
        if usuario in ["taiane", "dawison", "tacio", "adriana"]:
            abas = "PAGAMENTO,E-MAIL,AQUISIÇÃO"
        else:
            abas = "PAGAMENTO,AQUISIÇÃO"
        
        cursor.execute("INSERT INTO dados_login (nome_usuario, nome_completo, senha, abas) VALUES (?, ?, ?, ?)", 
                       (usuario, nome_completo[usuarios.index(usuario)], senha, abas))

# Commit das mudanças e fechamento da conexão
conn.commit()
conn.close()

# Caminho do arquivo gerado
caminho_bd
