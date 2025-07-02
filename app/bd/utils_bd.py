"""
Módulo para gerenciar operações de banco de dados relacionadas a usuários e pagamentos.
"""

import sqlite3
import os
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
            conn = sqlite3.connect(
                r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\login.db'
            )
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

def conecta_banco_pagamentos_v2(nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
        contrato, motivo, valor, tipo_pagamento, tecnicos, competencia,
        porcentagem, tipo_aquisicao):
    """
    Versão com sistema de filas simples - salva como JSON e processa depois.
    
    Esta função resolve problemas de concorrência salvando cada requisição como um arquivo JSON
    individual em uma fila de processamento, evitando conflitos quando múltiplos usuários
    fazem requisições simultaneamente.
    
    Args:
        nome_usuario (str): Nome do usuário que está fazendo a requisição
        tipo_servico (str): Tipo de serviço solicitado
        nome_fornecedor (str): Nome do fornecedor
        prefixo (str): Prefixo da requisição
        agencia (str): Agência responsável
        os_num (str): Número da OS
        contrato (str): Contrato relacionado
        motivo (str): Motivo da requisição
        valor (float): Valor da requisição
        tipo_pagamento (str): Tipo de pagamento
        tecnicos (str): Técnicos envolvidos
        competencia (str): Competência
        porcentagem (str): Porcentagem
        tipo_aquisicao (str): Tipo de aquisição
        
    Returns:
        str: ID único da requisição ou status do fallback
    """
    from datetime import datetime
    import json
    import uuid
    import os
    
    # Preparar dados da requisição
    dados_requisicao = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().isoformat(),
        'nome_usuario': nome_usuario,
        'tipo_servico': tipo_servico,
        'nome_fornecedor': nome_fornecedor,
        'prefixo': prefixo,
        'agencia': agencia,
        'os_num': os_num,
        'contrato': contrato,
        'motivo': motivo,
        'valor': valor,
        'tipo_pagamento': tipo_pagamento,
        'tecnicos': tecnicos,
        'competencia': competencia,
        'porcentagem': porcentagem,
        'tipo_aquisicao': tipo_aquisicao,
        'data_criacao': datetime.now().strftime('%d/%m/%Y'),
        'hora_criacao': datetime.now().strftime('%H:%M:%S'),
        'processado': False
    }
    
    # Definir caminhos da fila de requisições
    caminhos_fila = [
        r'app\bd\fila_requisicoes',
        r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\fila_requisicoes'
    ]
    
    # Criar diretório da fila se não existir
    diretorio_fila = None
    for caminho in caminhos_fila:
        try:
            os.makedirs(caminho, exist_ok=True)
            diretorio_fila = caminho
            break
        except:
            continue
    
    if not diretorio_fila:
        # Fallback para método original se não conseguir criar fila
        print("⚠️  Não foi possível criar fila. Usando método original...")
        conecta_banco_pagamentos(nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
            contrato, motivo, valor, tipo_pagamento, tecnicos, competencia,
            porcentagem, tipo_aquisicao)
        return "fallback"
    
    # Salvar como arquivo JSON na fila
    timestamp_arquivo = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Remove últimos 3 dígitos dos microssegundos
    nome_arquivo = f"req_{timestamp_arquivo}_{dados_requisicao['id'][:8]}.json"
    caminho_arquivo = os.path.join(diretorio_fila, nome_arquivo)
    
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_requisicao, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Requisição salva na fila: {dados_requisicao['id'][:8]}")
        print(f"   Arquivo: {nome_arquivo}")
        print(f"   Status: Aguardando processamento")
        
        return dados_requisicao['id']
        
    except Exception as e:
        print(f"❌ Erro ao salvar na fila: {e}")
        print("🔄 Tentando método original como fallback...")
        
        try:
            conecta_banco_pagamentos(nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
                contrato, motivo, valor, tipo_pagamento, tecnicos, competencia,
                porcentagem, tipo_aquisicao)
            print("✅ Salvo pelo método original")
            return "fallback_success"
        except Exception as erro_fallback:
            print(f"❌ Falha em ambos os métodos: {e} / {erro_fallback}")
            raise

def verificar_status_fila():
    """
    Verifica quantas requisições estão pendentes na fila de processamento.
    
    Esta função examina os arquivos JSON na fila e conta quantos estão pendentes
    de processamento e quantos já foram processados.
    
    Returns:
        dict: Dicionário com informações do status da fila:
            - pendentes: número de requisições não processadas
            - processados: número de requisições já processadas
            - total: total de arquivos na fila
            - diretorio: caminho do diretório da fila
    """
    import glob
    import json
    
    # Caminhos possíveis para a fila de requisições
    caminhos_fila = [
        r'app\bd\fila_requisicoes',
        r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\fila_requisicoes'
    ]
    
    # Procurar por diretório existente da fila
    for diretorio_fila in caminhos_fila:
        if os.path.exists(diretorio_fila):
            padrao_arquivos = os.path.join(diretorio_fila, "req_*.json")
            arquivos = glob.glob(padrao_arquivos)
            
            pendentes = 0
            processados = 0
            
            # Contar arquivos por status
            for arquivo in arquivos:
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                    
                    if dados.get('processado', False):
                        processados += 1
                    else:
                        pendentes += 1
                except:
                    continue
            
            return {
                'pendentes': pendentes,
                'processados': processados,
                'total': len(arquivos),
                'diretorio': diretorio_fila
            }
    
    return {'erro': 'Diretório da fila não encontrado'}

def mostrar_info_fila():
    """
    Função para mostrar informações da fila na interface principal.
    
    Retorna uma string formatada com o status atual da fila de requisições,
    incluindo indicadores visuais baseados na quantidade de requisições pendentes.
    
    Returns:
        str: Mensagem de status formatada com emoji indicativo
    """
    status = verificar_status_fila()
    
    if 'erro' in status:
        return "❌ Erro ao verificar fila"
    
    pendentes = status['pendentes']
    total = status['total']
    
    if pendentes == 0:
        return "✅ Fila vazia - todos os registros processados"
    elif pendentes <= 15:
        return f"🟡 {pendentes} requisições pendentes"
    else:
        return f"🔴 {pendentes} requisições pendentes - ATENÇÃO!"
