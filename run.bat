@echo off
REM Startup script for the Agentic AI Enterprise application

echo ================================================
echo  Agentic AI Enterprise - Startup Script
echo ================================================
echo.

REM Activate virtual environment
if exist "venv\" (
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirement.txt
)

echo.
echo ================================================
echo Starting Services...
echo ================================================
echo.

REM Start the Flask API server in a new window
echo Starting Flask API server on http://localhost:5000
start "Flask API" cmd /k "python api.py"

REM Wait for Flask to start
timeout /t 3 /nobreak

REM Start the Streamlit app in a new window
echo Starting Streamlit app on http://localhost:8501
start "Streamlit App" cmd /k "streamlit run app.py"

echo.
echo ================================================
echo Both services started!
echo - Flask API: http://localhost:5000
echo - Streamlit App: http://localhost:8501
echo - Auth Page: floating-auth-page/index.html
echo ================================================
echo.
echo You can now:
echo 1. Open http://localhost:8501 in your browser
echo 2. Use the built-in Streamlit auth, OR
echo 3. Open floating-auth-page/index.html for HTML auth
echo.
pause
