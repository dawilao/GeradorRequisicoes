import sqlite3

CONTRATOS = {
    "C. O. SALVADOR - BA - 2877": (
        r"G:\Meu Drive\1 - C. O SALVADOR - CTR 2021.7421.2877\7 - REQUISIÇÕES\REQUISIÇÃO"
    ),
    "C. O. SANTA CATARINA - SC - 5023": (
        r"G:\Meu Drive\2 - C. O SANTA CATARINA - CTR 2021.7421.5023\06 - REQUISIÇÕES"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. RIO GRANDE DO SUL - RS - 5525": (
        r"G:\Meu Drive\3 - C. O RIO GRANDE DO SUL - CTR 2022.7421.5525\7 - REQUISIÇÕES"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. RIO DE JANEIRO - RJ - 0494": (
        r"G:\Meu Drive\4 - C. O RIO DE JANEIRO - CTR 2023.7421.0494\7 - REQUISIÇÕES"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. NITERÓI - RJ - 1380": (
        r"G:\Meu Drive\5 - C. O NITERÓI - CTR 2023.7421.1380\7 - REQUISIÇÕES"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. BELO HORIZONTE - BH - 2054": (
        r"G:\Meu Drive\6 - C. O BELO HORIZONTE - CTR 2024.7421.2054\6 - REQUISIÇÃO"
    ),
    "C. O. RECIFE - PE - 5254": (
        r"G:\Meu Drive\8 - C. O RECIFE - CTR 2023.7421.5254\7 - REQUISIÇÕES"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. MANAUS - AM - 7649": (
        r"G:\Meu Drive\7 - C. O MANAUS - CTR 2023.7421.7649\07 - REQUISIÇÕES"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. VOLTA REDONDA - RJ - 0215": (
        r"G:\Meu Drive\10 - C. O VOLTA REDONDA - CTR 2025.7421.0215\6 - REQUISIÇÃO"
        r"\ORDEM DE COMPRA"
    ),
    "C. O. RONDÔNIA - RD - 0710": (
        r"G:\Meu Drive\9 - C. O RONDÔNIA - CTR 2025.7421.0710\6 - REQUISIÇÃO"
        r"\ORDEM DE COMPRA"
    ),
    "ATA BB CURITIBA - 0232": (
        r"G:\Meu Drive\11 - ATA CURITIBA BB - CTR 2025.7421.0232\6 - REQUISIÇÃO"
    ),
    "C. E. MANAUS - 1593": (
        r"G:\Meu Drive\24 - C. E MANAUS - CTR 2025.7421.1593\6 - REQUISIÇÃO"
        r"\ORDEM DE COMPRA"
    ),
    "CAIXA BAHIA - 4922.2024": (
        r"G:\Meu Drive\13 - CAIXA ECONÔMICA FEDERAL\1 - C.E.F - BAHIA - ATA 4922.2024"
        r"\6 - REQUISIÇÃO"
    ),
    "CAIXA CURITIBA - 534.2025": (
        r"G:\Meu Drive\13 - CAIXA ECONÔMICA FEDERAL\3 - C.E.F - CURITIBA - ATA"
        r" 534.2025\6 - REQUISIÇÃO"
    ),
    "CAIXA MANAUS - 4569.2024": (
        r"G:\Meu Drive\13 - CAIXA ECONÔMICA FEDERAL\2 - C.E.F - MANAUS - ATA"
        r" 4569.2024\6 - REQUISIÇÃO"
    ),
    "INFRA CURITIBA - 1120": (
        r"G:\Meu Drive\12 - INFRA CURITIBA BB - CTR 2025.7421.1120\6 - REQUISIÇÃO"
    )
}

conn = sqlite3.connect(r'app\bd\contratos.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS contratos (
    nome TEXT PRIMARY KEY,
    caminho TEXT NOT NULL
)
''')

for nome, caminho in CONTRATOS.items():
    cursor.execute("INSERT OR REPLACE INTO contratos (nome, caminho) VALUES (?, ?)", (nome, caminho))

conn.commit()
conn.close()
