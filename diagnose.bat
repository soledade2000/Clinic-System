@echo off
cd /d "%~dp0"
echo === docker info ===
docker info
echo.
echo === docker compose version ===
docker compose version 2>nul || docker-compose --version
echo.
echo === containers ===
docker ps -a
echo.
echo === logs clinica_backend ===
docker logs --tail 200 clinica_backend
echo.
echo === logs clinica_db ===
docker logs --tail 200 clinica_db
pause
