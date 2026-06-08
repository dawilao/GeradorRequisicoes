"""
Script de recuperação do banco de dados corrompido (dados.db).

Tenta recuperar os dados usando dois métodos:
  1. .recover  — mais completo, disponível no SQLite CLI >= 3.29.0
  2. .dump      — fallback, lê página a página o que ainda é legível

Uso:
    python recuperar_banco.py
    python recuperar_banco.py --origem "caminho\para\dados.db"
"""

import sqlite3
import subprocess
import shutil
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path


ORIGEM_PADRAO = r"G:\Meu Drive\17 - MODELOS\PROGRAMAS\Gerador de Requisições\app\bd\dados.db"


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def verificar_sqlite3_cli() -> str | None:
    """Retorna o caminho do executável sqlite3, ou None se não encontrado."""
    caminho = shutil.which("sqlite3")
    if caminho:
        return caminho
    # Tenta localizar em caminhos comuns do Windows
    candidatos = [
        r"C:\sqlite\sqlite3.exe",
        r"C:\Program Files\SQLite\sqlite3.exe",
        r"C:\tools\sqlite3.exe",
    ]
    for c in candidatos:
        if Path(c).exists():
            return c
    return None


def fazer_backup(origem: Path) -> Path:
    backup = origem.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    shutil.copy2(origem, backup)
    log(f"Backup criado: {backup}")
    return backup


def recuperar_via_cli(sqlite_exe: str, origem: Path, destino: Path, modo: str) -> bool:
    """
    Executa sqlite3 com .recover ou .dump escrevendo diretamente em arquivo
    (evita problemas de encoding no pipe do Windows).
    Retorna True se obteve sucesso (destino com dados).
    """
    sql_temp = origem.with_suffix(".recovery.sql")
    # Usa caminhos com barras normais para o sqlite3 CLI
    origem_cli = str(origem).replace("\\", "/")
    sql_temp_cli = str(sql_temp).replace("\\", "/")
    destino_cli = str(destino).replace("\\", "/")

    # Escreve o SQL direto em arquivo — evita UnicodeDecodeError no pipe
    script_dump = f'.output "{sql_temp_cli}"\n.{modo}\n.output stdout\n.quit\n'

    log(f"Executando sqlite3 .{modo} em {origem} ...")
    try:
        resultado = subprocess.run(
            [sqlite_exe, origem_cli],
            input=script_dump,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        log("Timeout — sqlite3 demorou mais de 2 minutos.")
        return False
    except FileNotFoundError:
        log(f"Executável não encontrado: {sqlite_exe}")
        return False

    if resultado.stderr:
        log(f"Avisos do sqlite3: {resultado.stderr[:500]}")

    if not sql_temp.exists() or sql_temp.stat().st_size == 0:
        log(f"O comando .{modo} não gerou conteúdo.")
        return False

    log(f"SQL gerado: {sql_temp} ({sql_temp.stat().st_size:,} bytes)")

    # Importa o SQL para o banco destino
    if destino.exists():
        destino.unlink()

    script_import = f'.read "{sql_temp_cli}"\n.quit\n'
    try:
        resultado_import = subprocess.run(
            [sqlite_exe, destino_cli],
            input=script_import,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        if resultado_import.stderr:
            log(f"Avisos na importação: {resultado_import.stderr[:500]}")
    except Exception as e:
        log(f"Erro na importação via CLI: {e}")
        log("Tentando importar via Python sqlite3 ...")
        try:
            sql_content = sql_temp.read_text(encoding="utf-8", errors="replace")
            conn = sqlite3.connect(str(destino))
            conn.executescript(sql_content)
            conn.commit()
            conn.close()
        except Exception as e2:
            log(f"Falha também via Python: {e2}")
            return False

    return destino.exists() and destino.stat().st_size > 0


def recuperar_via_python(origem: Path, destino: Path) -> bool:
    """
    Tenta copiar os dados linha a linha usando Python puro (sem CLI).
    Mais lento, mas não depende do sqlite3 externo.
    """
    log("Tentando recuperação via Python (row-by-row) ...")

    try:
        conn_orig = sqlite3.connect(str(origem))
        conn_orig.row_factory = sqlite3.Row
    except Exception as e:
        log(f"Não foi possível abrir o banco origem: {e}")
        return False

    if destino.exists():
        destino.unlink()
    conn_dest = sqlite3.connect(str(destino))

    total_recuperado = 0
    try:
        cur = conn_orig.cursor()

        # Lista as tabelas que ainda são legíveis
        try:
            cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
            tabelas = cur.fetchall()
        except Exception as e:
            log(f"Não foi possível ler o schema: {e}")
            conn_orig.close()
            conn_dest.close()
            return False

        log(f"Tabelas encontradas: {[t[0] for t in tabelas]}")

        for nome_tabela, sql_create in tabelas:
            if not sql_create:
                log(f"  [{nome_tabela}] Sem DDL, pulando.")
                continue

            try:
                conn_dest.execute(sql_create)
                conn_dest.commit()
            except Exception as e:
                log(f"  [{nome_tabela}] Erro ao criar tabela: {e}")
                continue

            try:
                cur.execute(f"SELECT * FROM [{nome_tabela}]")
                linhas = cur.fetchall()
            except Exception as e:
                log(f"  [{nome_tabela}] Erro ao ler linhas: {e}")
                continue

            if not linhas:
                log(f"  [{nome_tabela}] Vazia.")
                continue

            placeholders = ", ".join(["?"] * len(linhas[0]))
            inseridos = 0
            for linha in linhas:
                try:
                    conn_dest.execute(
                        f"INSERT OR IGNORE INTO [{nome_tabela}] VALUES ({placeholders})",
                        tuple(linha)
                    )
                    inseridos += 1
                except Exception:
                    pass  # linha corrompida, ignora

            conn_dest.commit()
            log(f"  [{nome_tabela}] {inseridos}/{len(linhas)} linhas recuperadas.")
            total_recuperado += inseridos

    finally:
        conn_orig.close()
        conn_dest.close()

    log(f"Total de linhas recuperadas: {total_recuperado}")
    return total_recuperado > 0


def validar_destino(destino: Path):
    """Abre o banco recuperado e imprime um resumo."""
    try:
        conn = sqlite3.connect(str(destino))
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = [r[0] for r in cur.fetchall()]
        log(f"\nResumo do banco recuperado ({destino.name}):")
        for t in tabelas:
            cur.execute(f"SELECT COUNT(*) FROM [{t}]")
            count = cur.fetchone()[0]
            log(f"  {t}: {count} registros")
        conn.close()
    except Exception as e:
        log(f"Erro ao validar destino: {e}")


def main():
    parser = argparse.ArgumentParser(description="Recuperação de banco SQLite corrompido")
    parser.add_argument("--origem", default=ORIGEM_PADRAO, help="Caminho do .db corrompido")
    args = parser.parse_args()

    origem = Path(args.origem)
    if not origem.exists():
        log(f"ERRO: Arquivo não encontrado: {origem}")
        sys.exit(1)

    log(f"Arquivo origem: {origem} ({origem.stat().st_size:,} bytes)")
    destino = origem.with_stem(origem.stem + "_recuperado")

    # Cria backup antes de qualquer operação
    fazer_backup(origem)

    sucesso = False
    sqlite_exe = verificar_sqlite3_cli()

    if sqlite_exe:
        log(f"sqlite3 CLI encontrado: {sqlite_exe}")

        # Tenta .recover primeiro (SQLite >= 3.29.0)
        log("\n=== Método 1: .recover ===")
        sucesso = recuperar_via_cli(sqlite_exe, origem, destino, "recover")

        if not sucesso:
            log("\n=== Método 2: .dump ===")
            sucesso = recuperar_via_cli(sqlite_exe, origem, destino, "dump")
    else:
        log("sqlite3 CLI não encontrado. Pulando métodos 1 e 2.")

    if not sucesso:
        log("\n=== Método 3: Python row-by-row ===")
        sucesso = recuperar_via_python(origem, destino)

    if sucesso:
        validar_destino(destino)
        log(f"\nRecuperação concluída! Banco salvo em:\n  {destino}")
        log("Para usar, renomeie o arquivo recuperado para 'dados.db' substituindo o original.")
    else:
        log("\nNão foi possível recuperar o banco de dados por nenhum método.")
        log("O banco pode estar muito danificado, ou tente instalar o sqlite3 CLI:")
        log("  https://www.sqlite.org/download.html  (baixe 'sqlite-tools-win-...')")
        log("  Extraia sqlite3.exe para C:\\sqlite\\ e adicione ao PATH.")


if __name__ == "__main__":
    main()
