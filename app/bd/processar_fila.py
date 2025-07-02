"""
Processador manual da fila de requisições com controle de acesso.

Este módulo permite que apenas usuários autorizados processem as requisições
armazenadas na fila de arquivos JSON, consolidando-as no banco de dados principal.
Isso resolve problemas de concorrência ao permitir processamento controlado e manual.

NOVAS FUNCIONALIDADES:
- verificar_autorizacao() agora aceita o nome do usuário logado no programa
- Se nome_usuario_logado for fornecido, usa ele diretamente
- Caso contrário, mantém o comportamento original (usuário do sistema operacional)
- Nova função verificar_usuario_autorizado() para verificações silenciosas

EXEMPLO DE USO:
    # Verificar com usuário logado no programa
    if verificar_autorizacao("TAIANE MARQUES"):
        processar_fila_completa("TAIANE MARQUES")
    
    # Verificação silenciosa para interfaces
    if verificar_usuario_autorizado("DAWISON NASCIMENTO"):
        print("Usuário autorizado")
"""

import os
import json
import glob
import sqlite3
from datetime import datetime
from typing import List, Dict

try:
    from ..salva_erros import salvar_erro
except ImportError:
    try:
        from app.salva_erros import salvar_erro
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from salva_erros import salvar_erro

# Lista de usuários autorizados a processar a fila de requisições
USUARIOS_AUTORIZADOS = [
    'TAIANE MARQUES',
    'DAWISON NASCIMENTO',
    'TÁCIO BARBOSA',
]

def verificar_autorizacao(nome_usuario_logado: str = None) -> bool:
    """
    Verifica se o usuário atual está autorizado a processar a fila.
    
    Compara o nome de usuário logado no programa com a lista de usuários
    autorizados. Se nome_usuario_logado não for fornecido, usa o usuário
    do sistema operacional como fallback.
    
    Args:
        nome_usuario_logado (str, optional): Nome do usuário logado no programa
    
    Returns:
        bool: True se o usuário está autorizado, False caso contrário
    """
    if nome_usuario_logado:
        # Usar o nome do usuário logado no programa
        usuario_verificacao = nome_usuario_logado.upper().strip()
        print(f"🔍 Verificando autorização para usuário logado: {usuario_verificacao}")
        
        # Verificar se o usuário logado está na lista de autorizados
        if usuario_verificacao in [u.upper() for u in USUARIOS_AUTORIZADOS]:
            print(f"✅ Usuário autorizado: {usuario_verificacao}")
            return True
        
        print(f"❌ Usuário não autorizado: {usuario_verificacao}")
        print(f"📋 Usuários autorizados: {', '.join(USUARIOS_AUTORIZADOS)}")
        return False
    
    else:
        # Fallback: usar o usuário do sistema operacional (comportamento original)
        usuario_sistema = os.environ.get('USERNAME', '').upper()
        print(f"🔍 Verificando autorização para usuário do sistema: {usuario_sistema}")
        
        # Mapeamento de usuários do sistema para nomes completos
        mapeamento_usuarios = {
            'TAIANE MARQUES': ['TAIANE', 'TAIANEMAR', 'TAIANE.MARQUES', 'TAIANE MARQUES'],
            'DAWISON NASCIMENTO': ['DAWISON', 'DAWISON.NASCIMENTO', 'DAWISON NASCIMENTO'],
            'TÁCIO BARBOSA': ['TACIO', 'TACIO.BARBOSA', 'TACIO BARBOSA', 'TÁCIO BARBOSA'],
        }
        
        # Verificar se o usuário atual corresponde a algum usuário autorizado
        for nome_completo, usuarios_sistema in mapeamento_usuarios.items():
            if usuario_sistema in [u.upper() for u in usuarios_sistema]:
                print(f"✅ Usuário autorizado: {nome_completo} ({usuario_sistema})")
                return True
        
        print(f"❌ Usuário não autorizado: {usuario_sistema}")
        print(f"📋 Usuários autorizados: {', '.join(USUARIOS_AUTORIZADOS)}")
        return False

def obter_arquivos_pendentes() -> List[str]:
    """
    Obtém lista de arquivos JSON pendentes na fila de processamento.
    
    Procura por arquivos de requisição que ainda não foram processados
    nos diretórios da fila de requisições.
    
    Returns:
        List[str]: Lista de caminhos dos arquivos pendentes, ordenados por timestamp
    """
    caminhos_fila = [
        r'app\bd\fila_requisicoes',
        # r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\fila_requisicoes'
    ]
    
    # Procurar diretório existente da fila
    for diretorio_fila in caminhos_fila:
        if os.path.exists(diretorio_fila):
            padrao_arquivos = os.path.join(diretorio_fila, "req_*.json")
            arquivos = glob.glob(padrao_arquivos)
            
            # Filtrar apenas arquivos não processados
            pendentes = []
            for arquivo in arquivos:
                try:
                    with open(arquivo, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                    
                    if not dados.get('processado', False):
                        pendentes.append(arquivo)
                except Exception:
                    continue
            
            # Ordenar por timestamp (mais antigos primeiro)
            pendentes.sort()
            return pendentes
    
    return []

def processar_requisicao_individual(dados: Dict) -> bool:
    """
    Processa uma requisição individual no banco de dados principal.
    
    Tenta conectar ao banco de dados e inserir os dados da requisição,
    adicionando timestamps de processamento.
    
    Args:
        dados (Dict): Dicionário com os dados da requisição
        
    Returns:
        bool: True se o processamento foi bem-sucedido, False caso contrário
    """
    # Caminhos possíveis para o banco de dados (priorizar o banco principal do Drive)
    caminhos_bd = [
        r'app\bd\dados.db'  # Banco local
        # r'G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\dados.db',  # Banco principal
    ]
    
    nome_usuario = dados.get('nome_usuario', '').upper().strip()

    # Tentar conectar ao banco de dados
    conn = None
    for caminho_bd in caminhos_bd:
        try:
            conn = sqlite3.connect(caminho_bd, timeout=30.0)
            break
        except sqlite3.Error:
            continue
    
    if not conn:
        raise sqlite3.Error("Não foi possível conectar ao banco de dados")
        salvar_erro(nome_usuario, "Erro ao conectar ao banco de dados")
    
    try:
        cursor = conn.cursor()
        
        # Verificar se as colunas de processamento existem
        cursor.execute("PRAGMA table_info(registros)")
        colunas_existentes = [col[1] for col in cursor.fetchall()]
        
        # Adicionar colunas se não existirem (principalmente para o banco do Drive)
        if "data_processamento" not in colunas_existentes:
            cursor.execute("ALTER TABLE registros ADD COLUMN data_processamento TEXT")
            print("Coluna 'data_processamento' adicionada ao banco")

        if "hora_processamento" not in colunas_existentes:
            cursor.execute("ALTER TABLE registros ADD COLUMN hora_processamento TEXT")
            print("Coluna 'hora_processamento' adicionada ao banco")

        # Criar tabela se não existir (para compatibilidade)
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
            hora_criacao TEXT,
            data_processamento TEXT,
            hora_processamento TEXT
        )
        ''')
        
        # Adicionar timestamps de processamento
        agora = datetime.now()
        dados_completos = {
            'nome_usuario': dados.get('nome_usuario', ''),
            'tipo_servico': dados.get('tipo_servico', ''),
            'nome_fornecedor': dados.get('nome_fornecedor', ''),
            'prefixo': dados.get('prefixo', ''),
            'agencia': dados.get('agencia', ''),
            'os_num': dados.get('os_num', ''),
            'contrato': dados.get('contrato', ''),
            'motivo': dados.get('motivo', ''),
            'valor': dados.get('valor', 0),
            'tipo_pagamento': dados.get('tipo_pagamento', ''),
            'tecnicos': dados.get('tecnicos', ''),
            'competencia': dados.get('competencia', ''),
            'porcentagem': dados.get('porcentagem', ''),
            'tipo_aquisicao': dados.get('tipo_aquisicao', ''),
            'data_criacao': dados.get('data_criacao', ''),
            'hora_criacao': dados.get('hora_criacao', ''),
            'lido': 0,  # Registros processados da fila começam como NÃO LIDOS
            'data_processamento': agora.strftime('%d/%m/%Y'),
            'hora_processamento': agora.strftime('%H:%M:%S')
        }
        
        # Inserir dados no banco
        cursor.execute('''
        INSERT INTO registros (
            nome_usuario, tipo_servico, nome_fornecedor, prefixo, agencia, os_num, 
            contrato, motivo, valor, tipo_pagamento, tecnicos, competencia,
            porcentagem, tipo_aquisicao, data_criacao, hora_criacao, lido,
            data_processamento, hora_processamento
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(dados_completos.values()))
        
        conn.commit()
        return True
        
    finally:
        conn.close()

def marcar_como_processado(caminho_arquivo: str):
    """
    Remove o arquivo JSON após processamento bem-sucedido.
    
    Como o arquivo já foi processado e inserido no banco de dados principal,
    não há necessidade de mantê-lo na fila. Esta abordagem evita acúmulo
    de arquivos processados e torna o sistema mais limpo.
    
    Args:
        caminho_arquivo (str): Caminho para o arquivo JSON a ser removido
    """
    try:
        # Criar backup opcional antes de remover (opcional)
        # backup_dir = os.path.join(os.path.dirname(caminho_arquivo), 'processados')
        # if not os.path.exists(backup_dir):
        #     os.makedirs(backup_dir)
        # shutil.move(caminho_arquivo, backup_dir)
        
        # Remover o arquivo da fila
        os.remove(caminho_arquivo)
        print(f"✅ Arquivo processado removido: {os.path.basename(caminho_arquivo)}")
            
    except Exception as e:
        print(f"⚠️  Erro ao remover arquivo processado: {e}")
        # Nota: Esta função pode ser chamada em contextos onde nome_usuario global não está definido
        # Por isso comentamos a linha de log de erro para evitar problemas
        # salvar_erro(nome_usuario, f"Erro ao remover arquivo processado: {e}")

def processar_fila_completa(nome_usuario_logado: str = None):
    """
    Processa toda a fila de requisições pendentes.
    
    Função principal que verifica autorização, obtém arquivos pendentes,
    solicita confirmação do usuário e processa todas as requisições.
    
    Args:
        nome_usuario_logado (str, optional): Nome do usuário logado no programa
    """
    print("=== PROCESSADOR DE FILA DE REQUISIÇÕES ===")
    
    # Verificar se o usuário está autorizado
    if not verificar_autorizacao(nome_usuario_logado):
        input("Pressione Enter para sair...")
        return
    
    # Obter arquivos pendentes na fila
    arquivos_pendentes = obter_arquivos_pendentes()
    
    if not arquivos_pendentes:
        print("✅ Nenhuma requisição pendente na fila!")
        input("Pressione Enter para sair...")
        return
    
    print(f"Encontradas {len(arquivos_pendentes)} requisições pendentes")
    
    # Solicitar confirmação do usuário
    resposta = input(f"Deseja processar todas as {len(arquivos_pendentes)} requisições? (s/n): ")
    if resposta.lower() not in ['s', 'sim', 'y', 'yes']:
        print("❌ Processamento cancelado pelo usuário")
        input("Pressione Enter para sair...")
        return
    
    print("\n🔄 Iniciando processamento...")
    
    processadas = 0
    erros = 0
    
    # Processar cada arquivo da fila
    for i, caminho_arquivo in enumerate(arquivos_pendentes, 1):
        try:
            # Carregar dados do arquivo JSON
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                requisicao = json.load(f)
            
            id_requisicao = requisicao.get('id', 'unknown')[:8]
            usuario = requisicao.get('nome_usuario', 'N/A')
            
            print(f"[{i}/{len(arquivos_pendentes)}] Processando {id_requisicao} ({usuario})...", end=' ')
            
            # Processar requisição no banco de dados
            if processar_requisicao_individual(requisicao):
                marcar_como_processado(caminho_arquivo)
                processadas += 1
                print("✅")
            else:
                erros += 1
                print("❌")
                
        except Exception as e:
            erros += 1
            print(f"❌ Erro: {e}")
    
    # Mostrar resumo do processamento
    print(f"\n📊 RESUMO DO PROCESSAMENTO:")
    print(f"   ✅ Processadas com sucesso: {processadas}")
    print(f"   ❌ Erros: {erros}")
    print(f"   📋 Total: {len(arquivos_pendentes)}")
    
    if erros == 0:
        print("🎉 Todos os registros foram processados com sucesso!")
    else:
        print("⚠️  Alguns registros apresentaram erros. Verifique os logs.")
    
    input("Pressione Enter para sair...")

def mostrar_status_fila():
    """
    Mostra o status atual da fila sem processar as requisições.
    
    Exibe informações sobre requisições pendentes, incluindo detalhes
    das últimas requisições na fila.
    """
    print("=== STATUS DA FILA DE REQUISIÇÕES ===")
    
    arquivos_pendentes = obter_arquivos_pendentes()
    
    if not arquivos_pendentes:
        print("✅ Nenhuma requisição pendente na fila!")
        return
    
    print(f"📋 Requisições pendentes: {len(arquivos_pendentes)}")
    print("\n📄 Últimas 10 requisições:")
    
    # Mostrar detalhes das últimas 10 requisições
    for i, caminho_arquivo in enumerate(arquivos_pendentes[-10:], 1):
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            timestamp = dados.get('timestamp', 'N/A')[:19].replace('T', ' ')
            usuario = dados.get('nome_usuario', 'N/A')
            id_requisicao = dados.get('id', 'unknown')[:8]
            
            print(f"   {i:2d}. {timestamp} | {id_requisicao} | {usuario}")
            
        except Exception:
            print(f"   {i:2d}. Erro ao ler arquivo")

def obter_info_fila_para_interface():
    """
    Obtém informações da fila formatadas para uso na interface gráfica.
    
    Como esta função é usada em uma aba com controle de acesso restrito,
    não é necessário verificar autorização aqui.
    
    Returns:
        dict: Dicionário com informações da fila para exibição na UI
    """
    arquivos_pendentes = obter_arquivos_pendentes()
    total_pendentes = len(arquivos_pendentes)
    
    # Determinar status e cor baseados na quantidade
    if total_pendentes == 0:
        status = "Fila vazia"
        cor = "verde"
        icone = "✅"
    elif total_pendentes <= 15:
        status = f"{total_pendentes} pendentes"
        cor = "amarelo"
        icone = "🟡"
    else:
        status = f"{total_pendentes} pendentes - ATENÇÃO!"
        cor = "vermelho"
        icone = "🔴"
    
    return {
        'total_pendentes': total_pendentes,
        'status': status,
        'cor': cor,
        'icone': icone
    }

def verificar_usuario_autorizado(nome_usuario: str) -> bool:
    """
    Função auxiliar para verificar se um usuário específico está autorizado
    a processar a fila de requisições.
    
    Esta função é útil para interfaces que precisam verificar autorização
    sem mostrar mensagens de console.
    
    Args:
        nome_usuario (str): Nome do usuário a ser verificado
        
    Returns:
        bool: True se o usuário está autorizado, False caso contrário
    """
    if not nome_usuario:
        return False
        
    usuario_verificacao = nome_usuario.upper().strip()
    return usuario_verificacao in [u.upper() for u in USUARIOS_AUTORIZADOS]

if __name__ == "__main__":
    import sys
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        mostrar_status_fila()
    else:
        processar_fila_completa()
