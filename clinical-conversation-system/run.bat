@echo off
echo ========================================
echo Clinical Conversation System - Starting
echo ========================================
echo.

:: Set Python path to current directory (Critical for AI modules)
set PYTHONPATH=%CD%

:: Check if virtual environment exists
if not exist venv\Scripts\activate (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

:: [NEW] Check for Fine-Tuned AI Weights (Proves local training)
if not exist "ai_models\clinical_bart_v1" (
    echo [WARNING] Fine-tuned model folder not found!
    echo The system will use the base model. If you haven't
    echo trained your model yet, please run:
    echo python ai_training/train_summarizer.py
    echo.
)

:: Display system info
echo [INFO] Python version:
python --version
echo.

:: Check if all project dependencies are in the venv
echo [INFO] Checking AI and Web dependencies...
python -c "import fastapi, uvicorn, transformers, loguru, rouge_score" 2>nul
if errorlevel 1 (
    echo [ERROR] Missing libraries in venv!
    echo Run: pip install fastapi uvicorn transformers loguru rouge-score
    pause
    exit /b 1
)
echo [SUCCESS] All dependencies are ready.
echo.

:: Suppress TensorFlow/Transformers noise
set HF_HUB_DISABLE_SYMLINKS_WARNING=1

echo ========================================
echo Starting FastAPI Server...
echo ========================================
echo Server URL: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.

:: Start the server using the module flag for better path handling
.\venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

pause