@echo off
REM Script para processar a fila de requisições
REM Este arquivo permite que usuários autorizados processem manualmente
REM as requisições armazenadas na fila de arquivos JSON

title Processador de Fila - Gerador de Requisicoes
cd /d "%~dp0"

echo.
echo ==========================================
echo   PROCESSADOR DE FILA DE REQUISICOES
echo ==========================================
echo.
echo Este programa processa requisicoes pendentes
echo armazenadas na fila de arquivos JSON.
echo.
echo Apenas usuarios autorizados podem executar
echo este processamento.
echo.

python app\bd\processar_fila.py

echo.
echo Processamento finalizado.
pause
