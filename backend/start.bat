@echo off
REM Script para iniciar o servidor FastAPI corretamente
echo Iniciando servidor Lumine API...
echo.
echo Certificando que estamos no diretorio correto...
cd /d "%~dp0"
echo Diretorio atual: %CD%
echo.
python run.py
pause

