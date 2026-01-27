@echo off
echo ========================================
echo Clinical Conversation System - Starting
echo ========================================
echo.

:: Set Python path to current directory
set PYTHONPATH=%CD%

:: Check if virtual environment exists
if not exist venv\Scripts\activate (
    echo [ERROR] Virtual environment not found!
    echo Please run setup first: python -m venv venv
    pause
    exit /b 1
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

:: Check if activation was successful
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [SUCCESS] Virtual environment activated
echo.

:: Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found!
    echo Please create .env file from .env.example
    echo.
)

:: Display system info
echo [INFO] Python version:
python --version
echo.

:: Check if required packages are installed
echo [INFO] Checking dependencies...
python -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo [ERROR] Required packages not installed!
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies OK
echo.

:: Set environment variable to suppress warnings (optional)
set TRANSFORMERS_CACHE=%CD%\cache\huggingface
set HF_HOME=%CD%\cache\huggingface

:: Start the server
echo ========================================
echo Starting FastAPI Server...
echo ========================================
echo Server URL: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

:: If server stops, show message
echo.
echo ========================================
echo Server stopped
echo ========================================
pause