@echo off
echo ========================================
echo    Demarrage du Frontend B2P.AI
echo ========================================
echo.

cd frontend

if not exist "node_modules" (
    echo [ERREUR] Dependances non installees!
    echo Executez d'abord: setup_local.bat
    pause
    exit /b 1
)

echo Frontend demarre sur: http://localhost:3000
echo.
echo Appuyez sur Ctrl+C pour arreter
echo.

call npm start
