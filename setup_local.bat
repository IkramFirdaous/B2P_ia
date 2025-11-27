@echo off
echo ========================================
echo    B2P.AI - Installation Locale
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo Telechargez Python depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Node.js n'est pas installe ou n'est pas dans le PATH
    echo Telechargez Node.js depuis: https://nodejs.org/
    pause
    exit /b 1
)

echo [1/6] Configuration du Backend...
echo.

cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creation de l'environnement virtuel Python...
    python -m venv venv
)

REM Activate virtual environment
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installation des dependances Python...
pip install -q --upgrade pip
pip install -q -r requirements.txt

REM Download spaCy model
echo.
echo [2/6] Telechargement du modele NLP francais (peut prendre 2-3 minutes)...
python -m spacy download fr_core_news_lg

REM Create database and sample data
echo.
echo [3/6] Creation de la base de donnees avec donnees d'exemple...
python create_sample_data.py
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de la creation de la base de donnees
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Backend configure avec succes!
echo ========================================
echo.

cd ..

echo [4/6] Configuration du Frontend...
echo.

cd frontend

REM Install Node dependencies
echo Installation des dependances Node.js...
call npm install

if %errorlevel% neq 0 (
    echo [ERREUR] Echec de l'installation des dependances frontend
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Frontend configure avec succes!
echo ========================================
echo.

cd ..

echo.
echo ========================================
echo      INSTALLATION TERMINEE!
echo ========================================
echo.
echo Comptes de test crees:
echo   - alice@example.com / password123 (Manager)
echo   - bob@example.com / password123 (Employe)
echo   - claire@example.com / password123 (Employe)
echo.
echo Prochaines etapes:
echo.
echo [5/6] Demarrer le BACKEND (dans ce terminal):
echo   cd backend
echo   venv\Scripts\activate
echo   uvicorn app.main:app --reload
echo.
echo [6/6] Demarrer le FRONTEND (dans un NOUVEAU terminal):
echo   cd frontend
echo   npm start
echo.
echo Puis ouvrir: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Consultez DEMARRAGE_LOCAL.md pour plus de details
echo.
pause
