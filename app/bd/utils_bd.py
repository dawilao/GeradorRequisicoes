"""
Módulo para gerenciar operações de banco de dados relacionadas a usuários e pagamentos.
"""

import sqlite3
from typing import Optional, Tuple

class DatabaseManager:
    """Gerenciador de operações do banco de dados."""
    
    def __init__(self):
        self.db_paths = [
            r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\login.db',
            r'app\bd\login.db'
        ]
    
    def _get_connection(self, outros_paths: list = None) -> sqlite3.Connection:
        """
        Estabelece conexão com o banco de dados.
        
        Args:
            outros_paths (list, opcional): Lista de caminhos alternativos para tentar a conexão.

        Returns:
            sqlite3.Connection: Conexão com o banco de dados.
            
        Raises:
            sqlite3.Error: Se não conseguir conectar a nenhum dos caminhos.
        """
        paths_para_iterar = outros_paths if outros_paths is not None else self.db_paths

        for db_path in paths_para_iterar:
            try:
                return sqlite3.connect(db_path)
            except sqlite3.Error:
                continue
        
        raise sqlite3.Error("Não foi possível conectar ao banco de dados em nenhum dos caminhos.")
    
    def validar_credenciais(self, usuario: str, senha: str) -> Optional[Tuple[str, str]]:
        """
        Valida as credenciais do usuário no banco de dados.
        
        Args:
            usuario (str): Nome de usuário.
            senha (str): Senha do usuário.
            
        Returns:
            Optional[Tuple[str, str]]: Tupla com (nome_completo, abas) se válido, None caso contrário.
            
        Raises:
            sqlite3.Error: Se houver erro na operação do banco de dados.
        """
        conn = self._get_connection()

        try:
            cursor = conn.cursor()
            query = (
                "SELECT senha, nome_completo, abas "
                "FROM dados_login "
                "WHERE LOWER(nome_usuario) = ?"
            )
            cursor.execute(query, (usuario.lower(),))
            resultado = cursor.fetchone()
            
            if resultado and resultado[0] == senha:
                return (resultado[1], resultado[2])
            
            return None
            
        finally:
            conn.close()
    
    def verificar_senha_atual(self, usuario: str) -> Optional[str]:
        """
        Verifica e retorna a senha atual do usuário.
        
        Args:
            usuario (str): Nome de usuário.
            
        Returns:
            Optional[str]: Senha atual se o usuário existir, None caso contrário.
            
        Raises:
            sqlite3.Error: Se houver erro na operação do banco de dados.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT senha FROM dados_login WHERE LOWER(nome_usuario) = ?",
                (usuario.lower(),)
            )
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
            
        finally:
            conn.close()
    
    def alterar_senha(self, usuario: str, nova_senha: str) -> bool:
        """
        Altera a senha do usuário no banco de dados.
        
        Args:
            usuario (str): Nome de usuário.
            nova_senha (str): Nova senha.
            
        Returns:
            bool: True se a alteração foi bem-sucedida, False caso contrário.
            
        Raises:
            sqlite3.Error: Se houver erro na operação do banco de dados.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE dados_login SET senha = ? WHERE LOWER(nome_usuario) = ?",
                (nova_senha, usuario.lower())
            )
            conn.commit()
            return cursor.rowcount > 0
            
        finally:
            conn.close()


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

def acessa_bd_usuarios():
    """
    Retorna uma lista de todos os usuários cadastrados no banco de dados.

    Retornos:
        - Lista de usuários.
    """
    try:
        try:
            conn = sqlite3.connect(r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\login.db')
        except sqlite3.Error:
            conn = sqlite3.connect(
                r'app\bd\login.db'
            )

        cursor = conn.cursor()
        cursor.execute("SELECT nome_completo, varios_departamentos FROM dados_login")
        resultados = cursor.fetchall()
        conn.close()

        # Lista com todos os usuários
        todos_usuarios = sorted([row[0] for row in resultados])

        # Lista apenas com usuários que têm varios_departamentos = 'SIM'
        usuarios_varios_dept = sorted([
            row[0] for row in resultados 
            if row[1] and row[1].upper() == 'SIM'
        ])

        return todos_usuarios, usuarios_varios_dept

    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        # Valores padrão caso ocorra erro
        todos_usuarios = [
            'ADRIANA BARRETO', 'AMANDA SAMPAIO', 'CARLOS ALBERTO',
            'DANIEL ROMUALDO', 'DAWISON NASCIMENTO', 'FELIPE COSTA',
            'FELIPE MOTA', 'GABRIEL BARBOSA', 'GUILHERME ANDRADE',
            'HENRIQUE CARDOSO', 'IGOR ALBERT', 'IURE OLIVEIRA',
            'JOÃO GABRIEL', 'LUCAS MACIEL', 'LUCAS HEBERT',
            'MATEUS SILVA', 'TÁCIO BARBOSA', 'TAIANE MARQUES',
            'VINICIUS CRUZ', 'LUCAS CALAIS', 'KALI ABDALLA',
            'DAVI BORGES', 'LUCAS BORGES', 'MARILIZA MACHADO',
            'ROSANA SILVA', 'DAVI ABDALLA', 'SAYMA ABDALLA',
            'BRUNA BORGES', 'ROBERTO ADANS', 'MIGUEL MARQUES',
            'JADSON JUNIOR',
        ]
        usuarios_varios_dept = [
            'AMANDA SAMPAIO', 'DAWISON NASCIMENTO', 
            'TÁCIO BARBOSA', 'TAIANE MARQUES', 'ROSANA SILVA'
            'MIGUEL MARQUES',
        ]
        return todos_usuarios, usuarios_varios_dept
