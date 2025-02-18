import sqlite3

def verificar_usuarios():
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect(r'app\bd\login.db')  # Caminho para o banco de dados
        cursor = conn.cursor()

        # Consulta para pegar todos os usuários
        cursor.execute("SELECT usuario, senha FROM usuarios")
        usuarios = cursor.fetchall()

        # Exibe os usuários no terminal
        print("Usuários no banco de dados:")
        for usuario, senha in usuarios:
            print(f"Usuário: {usuario}, Senha: {senha}")

        # Fechar a conexão com o banco de dados
        conn.close()

    except sqlite3.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")

# Chama a função para listar os usuários
verificar_usuarios()
