@echo off
cd /d %~dp0

echo Ajout des fichiers...
git add .

echo Commit...
git commit -m "Auto update"

echo Push vers GitHub...
git push

echo OK ✔
pause