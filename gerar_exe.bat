@echo off
pyinstaller --name "Gerador de Requisições" --version-file "S:\Projetos\GeradorTextoCompras\version_info.txt" --noconsole --paths=. "S:\Projetos\GeradorTextoCompras\main.py"
pause
