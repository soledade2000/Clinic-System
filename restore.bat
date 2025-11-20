@echo off
cd /d "%~dp0"
if "%~1"=="" (
  echo Uso: restore.bat path\arquivo.sql
  pause
  exit /b 1
)
docker cp "%~1" clinica_db:/tmp/dump.sql
docker exec -t clinica_db psql -U clinic_admin -d clinica -f /tmp/dump.sql
echo Restauração concluída.
pause
