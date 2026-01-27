@echo off
echo ========================================
echo Fixing bcrypt compatibility issue
echo ========================================
echo.

:: Activate virtual environment
call venv\Scripts\activate

:: Uninstall problematic versions
echo [INFO] Removing old bcrypt versions...
pip uninstall -y bcrypt passlib

:: Install compatible versions
echo [INFO] Installing compatible versions...
pip install bcrypt==4.0.1
pip install passlib[bcrypt]==1.7.4

echo.
echo [SUCCESS] bcrypt fixed!
echo.
echo The warning should be gone when you restart the server.
echo.
pause