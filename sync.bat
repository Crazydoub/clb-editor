@echo off
cd /d %~dp0

echo ==========================
echo   RESET + RESYNC GITHUB
echo ==========================

:: === CONFIG ===
set REPO_URL=https://github.com/Crazydoub/clb-editor.git
set BRANCH=main

echo.
echo [1] Verification repo git...
if not exist .git (
    echo Initialisation du repo...
    git init
)

echo.
echo [2] Fix safe directory...
git config --global --add safe.directory "%cd%"

echo.
echo [3] Reset remote origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo.
echo [4] Forcer branche main...
git branch -M %BRANCH%

echo.
echo [5] Ajout fichiers...
git add .

echo.
echo [6] Commit...
git commit -m "Resync %date% %time%" 2>nul

echo.
echo [7] Push GitHub...
git push -u origin %BRANCH% --force

echo.
echo ==========================
echo   RESYNC TERMINE ✔
echo ==========================
pause