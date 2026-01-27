@echo off
SETLOCAL EnableDelayedExpansion

echo ====================================================
echo   Clinical Conversation System - Setup ^& Launch
echo ====================================================
echo.

:: 1. Check for Python Installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python 3.10+ and check 'Add to PATH'.
    pause
    exit /b
)

:: 2. Create Virtual Environment if missing
if not exist "venv" (
    echo [1/5] Creating virtual environment...
    python -m venv venv
)

:: 3. Activate and Install Requirements
echo [2/5] Activating environment and installing dependencies...
call venv\Scripts\activate
:: Ensures OpenAI Whisper and other libraries from requirements.txt are installed
pip install -r requirements.txt

:: 4. Handle Environment Variables (.env)
if not exist ".env" (
    echo [3/5] .env file missing. Creating from .env.example...
    if exist ".env.example" (
        copy .env.example .env
        echo [INFO] Generating a fresh SECRET_KEY for security...
        :: Generates a unique 32-character hex key for JWT/Security
        python -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')" >> .env
        echo [SUCCESS] .env created with a unique secret key.
    ) else (
        echo [ERROR] .env.example not found. Please ensure it is in the project root.
        pause
        exit /b
    )
)

:: 5. Create Local Folders (Ignored in Git)
echo [4/5] Preparing local directories...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs
if not exist "cache\huggingface" mkdir cache\huggingface
if not exist "cache\transformers" mkdir cache\transformers

:: 6. Launch the Backend
echo [5/5] Starting the Clinical AI Backend...
echo.
echo Server URL: http://127.0.0.1:8000
echo API Docs:   http://127.0.0.1:8000/docs
echo.
echo (NOTE: The first run will download Whisper and BART models. Please wait...)
echo.

:: Runs the FastAPI application using Uvicorn
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

pause
