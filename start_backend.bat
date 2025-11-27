@echo off
echo ========================================
echo    Demarrage du Backend B2P.AI
echo ========================================
echo.

cd backend

if not exist "venv\Scripts\activate.bat" (
    echo [ERREUR] Environnement virtuel non trouve!
    echo Executez d'abord: setup_local.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Backend demarre sur: http://localhost:8000
echo Documentation API: http://localhost:8000/docs
echo.
echo Appuyez sur Ctrl+C pour arreter
echo.

uvicorn app.main:app --reload
