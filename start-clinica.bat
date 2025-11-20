@echo off
cd /d "%~dp0"
echo Iniciando Clinica (docker)...
rem tenta `docker compose` (prefere novo CLI). Se falhar, tenta docker-compose.
docker compose up -d --build 2>nul || docker-compose up -d --build
IF %ERRORLEVEL% NEQ 0 (
  echo Erro ao iniciar containers.
  echo Verifique se o Docker Desktop esta instalado e rodando.
  pause
  exit /b 1
)
echo Containers iniciados.
docker ps
pause
