@echo off
cd /d "%~dp0"
docker compose down 2>nul || docker-compose down
pause
