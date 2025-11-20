@echo off
cd /d "%~dp0"
if not exist backups mkdir backups
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set DATE_PART=%%d-%%b-%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIME_PART=%%a-%%b
set TIMESTAMP=%DATE_PART%_%TIME_PART%
docker exec -t clinica_db pg_dump -U clinic_admin clinica > backups\clinica_dump_%TIMESTAMP%.sql
echo Backup salvo em backups\clinica_dump_%TIMESTAMP%.sql
pause
