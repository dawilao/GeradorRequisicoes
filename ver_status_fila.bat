@echo off
REM Script para verificar o status da fila de requisições
REM Este arquivo mostra informações sobre requisições pendentes
REM sem processá-las, permitindo monitoramento da fila

title Status da Fila - Gerador de Requisicoes
cd /d "%~dp0"

echo.
echo ==========================================
echo   STATUS DA FILA DE REQUISICOES
echo ==========================================
echo.
echo Este programa mostra informacoes sobre
echo requisicoes pendentes na fila.
echo.

python app\bd\processar_fila.py --status

echo.
pause
