@echo off
REM ATM System - Quick Start Script for Windows

echo.
echo 🏧 ATM Face Recognition System - Quick Start
echo ==============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python version: %PYTHON_VERSION%

REM Create virtual environment
echo.
echo 📦 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Check if trainer exists
echo.
if not exist "trainer\trainer.yml" (
    echo ⚠️  Trained model not found!
    echo Do you want to train the model now? (requires dataset/) [y/n]
    set /p response="Enter choice: "
    if /i "!response!"=="y" (
        echo 🔄 Training model...
        python train_model.py
    ) else (
        echo ❌ Cannot proceed without trained model. Run: python train_model.py
        pause
        exit /b 1
    )
)

REM Create .streamlit directory if it doesn't exist
if not exist ".streamlit" mkdir .streamlit

REM Run the app
echo.
echo 🚀 Starting Streamlit app...
echo 📲 Open your browser to: http://localhost:8501
echo.
streamlit run app.py
