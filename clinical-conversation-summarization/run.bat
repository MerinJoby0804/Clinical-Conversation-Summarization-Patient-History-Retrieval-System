@echo off
echo ========================================
echo Clinical Conversation System - Starting
echo ========================================
echo.

:: Set Python path to current directory
set PYTHONPATH=%CD%

:: 1. AUTO-SETUP: Create venv if it doesn't exist
if not exist venv\Scripts\activate (
    echo [INFO] Virtual environment not found. Creating it now...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Python not found. Please install Python and add to PATH.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

:: 2. AUTO-INSTALL: Install requirements if they are missing
echo [INFO] Checking dependencies...
python -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo [INFO] Installing required packages from requirements.txt...
    pip install -r requirements.txt
)
echo [SUCCESS] Dependencies OK
echo.

:: 3. AUTO-CONFIG: Create .env from .example and generate secret key
if not exist .env (
    if exist .env.example (
        echo [WARNING] .env file not found! Creating from .env.example...
        copy .env.example .env
        echo [INFO] Generating a fresh SECRET_KEY for security...
        python -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')" >> .env
    ) else (
        echo [ERROR] Neither .env nor .env.example found!
    )
)

:: Set environment variables for AI models
set TRANSFORMERS_CACHE=%CD%\cache\huggingface
set HF_HOME=%CD%\cache\huggingface

:: Start the server
echo ========================================
echo Starting FastAPI Server...
echo ========================================
echo Server URL: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo (Note: First run will download AI models like all-MiniLM-L6-v2)
echo Press CTRL+C to stop the server
echo ========================================

python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

pause
