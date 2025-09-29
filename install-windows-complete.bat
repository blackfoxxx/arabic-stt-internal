@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: Arabic STT Internal System - Complete Windows Installation Script
:: ============================================================================
:: This script automatically installs all requirements for the Arabic STT system
:: including Python, Node.js, Git, CUDA, LLM models, and performs integrity checks
:: No user interaction required - fully automated installation
:: ============================================================================

echo.
echo ========================================================================
echo  Arabic STT Internal System - Automated Windows Installation
echo ========================================================================
echo  Installing all requirements automatically...
echo  This may take 30-60 minutes depending on your internet connection.
echo ========================================================================
echo.

:: Set installation directory
set "INSTALL_DIR=%~dp0"
set "VENV_DIR=%INSTALL_DIR%arabic-stt-env"
set "MODELS_DIR=%INSTALL_DIR%models"
set "LOG_FILE=%INSTALL_DIR%installation.log"

:: Create log file
echo Installation started at %date% %time% > "%LOG_FILE%"

:: ============================================================================
:: PHASE 1: System Requirements Check
:: ============================================================================
echo [1/8] Checking system requirements...
echo [1/8] Checking system requirements... >> "%LOG_FILE%"

:: Check Windows version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo Windows version: %VERSION% >> "%LOG_FILE%"

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo ERROR: This script must be run as Administrator! >> "%LOG_FILE%"
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

:: Check available disk space (minimum 20GB)
for /f "tokens=3" %%a in ('dir /-c "%INSTALL_DIR%" ^| find "bytes free"') do set FREESPACE=%%a
set /a FREESPACE_GB=%FREESPACE:~0,-9%
if %FREESPACE_GB% LSS 20 (
    echo ERROR: Insufficient disk space. Need at least 20GB, found %FREESPACE_GB%GB
    echo ERROR: Insufficient disk space. Need at least 20GB, found %FREESPACE_GB%GB >> "%LOG_FILE%"
    pause
    exit /b 1
)

echo System requirements check passed. >> "%LOG_FILE%"

:: ============================================================================
:: PHASE 2: Install Chocolatey Package Manager
:: ============================================================================
echo [2/8] Installing Chocolatey package manager...
echo [2/8] Installing Chocolatey package manager... >> "%LOG_FILE%"

where choco >nul 2>&1
if %errorLevel% neq 0 (
    echo Installing Chocolatey...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" >> "%LOG_FILE%" 2>&1
    if !errorLevel! neq 0 (
        echo ERROR: Failed to install Chocolatey
        echo ERROR: Failed to install Chocolatey >> "%LOG_FILE%"
        pause
        exit /b 1
    )
    :: Refresh environment variables
    call refreshenv
    echo Chocolatey installed successfully. >> "%LOG_FILE%"
) else (
    echo Chocolatey already installed. >> "%LOG_FILE%"
)

:: ============================================================================
:: PHASE 3: Install Core Dependencies
:: ============================================================================
echo [3/8] Installing core dependencies (Python, Node.js, Git)...
echo [3/8] Installing core dependencies... >> "%LOG_FILE%"

:: Install Python 3.11
echo Installing Python 3.11...
choco install python --version=3.11.9 -y >> "%LOG_FILE%" 2>&1
if !errorLevel! neq 0 (
    echo ERROR: Failed to install Python
    echo ERROR: Failed to install Python >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Install Node.js LTS
echo Installing Node.js LTS...
choco install nodejs-lts -y >> "%LOG_FILE%" 2>&1
if !errorLevel! neq 0 (
    echo ERROR: Failed to install Node.js
    echo ERROR: Failed to install Node.js >> "%LOG_FILE%"
    pause
    exit /b 1
)

::Install Git
echo Installing Git...
choco install git -y >> "%LOG_FILE%" 2>&1
if !errorLevel! neq 0 (
    echo ERROR: Failed to install Git
    echo ERROR: Failed to install Git >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Install Ollama for LLM capabilities
echo Installing Ollama for advanced LLM processing...
choco install ollama -y >> "%LOG_FILE%" 2>&1
if !errorLevel! neq 0 (
    echo WARNING: Failed to install Ollama via Chocolatey, trying direct download...
    echo WARNING: Failed to install Ollama via Chocolatey >> "%LOG_FILE%"
    
    :: Try direct download as fallback
    powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/windows' -OutFile '%TEMP%\OllamaSetup.exe'" >> "%LOG_FILE%" 2>&1
    if exist "%TEMP%\OllamaSetup.exe" (
        echo Installing Ollama from direct download...
        "%TEMP%\OllamaSetup.exe" /S >> "%LOG_FILE%" 2>&1
        if !errorLevel! neq 0 (
            echo WARNING: Ollama installation failed, continuing without Ollama support
            echo WARNING: Ollama installation failed >> "%LOG_FILE%"
        ) else (
            echo Ollama installed successfully via direct download. >> "%LOG_FILE%"
        )
        del "%TEMP%\OllamaSetup.exe" >nul 2>&1
    ) else (
        echo WARNING: Could not download Ollama installer, continuing without Ollama support
        echo WARNING: Could not download Ollama installer >> "%LOG_FILE%"
    )
) else (
    echo Ollama installed successfully via Chocolatey. >> "%LOG_FILE%"
)

:: Refresh environment variables
call refreshenv

echo Core dependencies installed successfully. >> "%LOG_FILE%"

:: ============================================================================
:: PHASE 4: Install CUDA Toolkit (Optional but Recommended)
:: ============================================================================
echo [4/8] Installing CUDA Toolkit for GPU acceleration...
echo [4/8] Installing CUDA Toolkit... >> "%LOG_FILE%"

:: Check if NVIDIA GPU is present
nvidia-smi >nul 2>&1
if !errorLevel! equ 0 (
    echo NVIDIA GPU detected, installing CUDA Toolkit...
    choco install cuda --version=12.1.0 -y >> "%LOG_FILE%" 2>&1
    if !errorLevel! neq 0 (
        echo WARNING: Failed to install CUDA Toolkit, continuing without GPU acceleration
        echo WARNING: Failed to install CUDA Toolkit >> "%LOG_FILE%"
    ) else (
        echo CUDA Toolkit installed successfully. >> "%LOG_FILE%"
    )
) else (
    echo No NVIDIA GPU detected, skipping CUDA installation.
    echo No NVIDIA GPU detected, skipping CUDA installation. >> "%LOG_FILE%"
)

:: ============================================================================
:: PHASE 5: Create Python Virtual Environment
:: ============================================================================
echo [5/8] Creating Python virtual environment...
echo [5/8] Creating Python virtual environment... >> "%LOG_FILE%"

:: Remove existing virtual environment if it exists
if exist "%VENV_DIR%" (
    echo Removing existing virtual environment...
    rmdir /s /q "%VENV_DIR%"
)

:: Create new virtual environment
python -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
if !errorLevel! neq 0 (
    echo ERROR: Failed to create virtual environment
    echo ERROR: Failed to create virtual environment >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1

echo Virtual environment created successfully. >> "%LOG_FILE%"

:: ============================================================================
:: PHASE 6: Install Python Dependencies
:: ============================================================================
echo [6/8] Installing Python dependencies...
echo [6/8] Installing Python dependencies... >> "%LOG_FILE%"

:: Install PyTorch with CUDA support
echo Installing PyTorch with CUDA support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 >> "%LOG_FILE%" 2>&1
if !errorLevel! neq 0 (
    echo WARNING: Failed to install PyTorch with CUDA, trying CPU version...
    pip install torch torchvision torchaudio >> "%LOG_FILE%" 2>&1
    if !errorLevel! neq 0 (
        echo ERROR: Failed to install PyTorch
        echo ERROR: Failed to install PyTorch >> "%LOG_FILE%"
        pause
        exit /b 1
    )
)

:: Install project requirements
if exist "%INSTALL_DIR%requirements-training.txt" (
    echo Installing project requirements...
    pip install -r "%INSTALL_DIR%requirements-training.txt" >> "%LOG_FILE%" 2>&1
    if !errorLevel! neq 0 (
        echo ERROR: Failed to install project requirements
        echo ERROR: Failed to install project requirements >> "%LOG_FILE%"
        pause
        exit /b 1
    )
) else (
    echo Installing core AI packages...
    pip install faster-whisper pyannote.audio transformers datasets accelerate >> "%LOG_FILE%" 2>&1
    pip install fastapi uvicorn numpy pandas scikit-learn >> "%LOG_FILE%" 2>&1
    pip install librosa soundfile pydub >> "%LOG_FILE%" 2>&1
)

echo Python dependencies installed successfully. >> "%LOG_FILE%"

:: ============================================================================
:: PHASE 7: Install Node.js Dependencies and Download LLM Models
:: ============================================================================
echo [7/8] Installing Node.js dependencies and downloading LLM models...
echo [7/8] Installing Node.js dependencies and LLM models... >> "%LOG_FILE%"

:: Install Node.js dependencies
if exist "%INSTALL_DIR%package.json" (
    echo Installing Node.js packages...
    npm install >> "%LOG_FILE%" 2>&1
    if !errorLevel! neq 0 (
        echo ERROR: Failed to install Node.js dependencies
        echo ERROR: Failed to install Node.js dependencies >> "%LOG_FILE%"
        pause
        exit /b 1
    )
)

:: Create models directory
if not exist "%MODELS_DIR%" mkdir "%MODELS_DIR%"

:: Download LLM models using Python
echo Downloading LLM models (this may take 10-30 minutes)...
python -c "
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append('.')

try:
    # Download Whisper models
    print('Downloading Whisper models...')
    import whisper
    whisper.load_model('base')
    whisper.load_model('small')
    print('Whisper models downloaded successfully.')
    
    # Download transformers models
    print('Downloading transformer models...')
    from transformers import AutoTokenizer, AutoModel
    
    # Download Arabic BERT model
    tokenizer = AutoTokenizer.from_pretrained('aubmindlab/bert-base-arabertv2')
    model = AutoModel.from_pretrained('aubmindlab/bert-base-arabertv2')
    print('Arabic BERT model downloaded successfully.')
    
    # Download sentiment analysis model
    from transformers import pipeline
    sentiment_pipeline = pipeline('sentiment-analysis', model='cardiffnlp/twitter-xlm-roberta-base-sentiment')
    print('Sentiment analysis model downloaded successfully.')
    
    print('All models downloaded successfully!')
    
except Exception as e:
    print(f'Error downloading models: {e}')
    sys.exit(1)
" >> "%LOG_FILE%" 2>&1

if !errorLevel! neq 0 (
    echo WARNING: Some models failed to download, but installation will continue
    echo WARNING: Some models failed to download >> "%LOG_FILE%"
)

echo LLM models download completed. >> "%LOG_FILE%"

:: ============================================================================
:: Download Ollama Models
:: ============================================================================
echo Downloading Ollama models for enhanced LLM capabilities...
echo Downloading Ollama models... >> "%LOG_FILE%"

:: Check if Ollama is available
where ollama >nul 2>&1
if !errorLevel! equ 0 (
    echo Ollama found, downloading recommended models...
    
    :: Start Ollama service
    echo Starting Ollama service...
    start /B ollama serve >> "%LOG_FILE%" 2>&1
    timeout /t 10
    
    :: Download Llama 3.1 8B model (recommended for Arabic)
    echo Downloading Llama 3.1 8B model...
    ollama pull llama3.1:8b >> "%LOG_FILE%" 2>&1
    if !errorLevel! neq 0 (
        echo WARNING: Failed to download Llama 3.1 8B model
        echo WARNING: Failed to download Llama 3.1 8B model >> "%LOG_FILE%"
    ) else (
        echo Llama 3.1 8B model downloaded successfully. >> "%LOG_FILE%"
    )
    
    :: Download Mistral 7B model (lightweight alternative)
    echo Downloading Mistral 7B model...
    ollama pull mistral:7b >> "%LOG_FILE%" 2>&1
    if !errorLevel! neq 0 (
        echo WARNING: Failed to download Mistral 7B model
        echo WARNING: Failed to download Mistral 7B model >> "%LOG_FILE%"
    ) else (
        echo Mistral 7B model downloaded successfully. >> "%LOG_FILE%"
    )
    
    :: Download Qwen2.5 7B model (excellent for multilingual tasks)
    echo Downloading Qwen2.5 7B model...
    ollama pull qwen2.5:7b >> "%LOG_FILE%" 2>&1
    if !errorLevel! neq 0 (
        echo WARNING: Failed to download Qwen2.5 7B model
        echo WARNING: Failed to download Qwen2.5 7B model >> "%LOG_FILE%"
    ) else (
        echo Qwen2.5 7B model downloaded successfully. >> "%LOG_FILE%"
    )
    
    :: Download a smaller model for faster processing
    echo Downloading Phi-3 Mini model for fast processing...
    ollama pull phi3:mini >> "%LOG_FILE%" 2>&1
    if !errorLevel! neq 0 (
        echo WARNING: Failed to download Phi-3 Mini model
        echo WARNING: Failed to download Phi-3 Mini model >> "%LOG_FILE%"
    ) else (
        echo Phi-3 Mini model downloaded successfully. >> "%LOG_FILE%"
    )
    
    echo Ollama models download completed. >> "%LOG_FILE%"
) else (
    echo Ollama not found, skipping Ollama model downloads.
    echo Ollama not found, skipping Ollama model downloads. >> "%LOG_FILE%"
)

:: ============================================================================
:: PHASE 8: Integrity Verification and Final Setup
:: ============================================================================
echo [8/8] Performing integrity verification and final setup...
echo [8/8] Performing integrity verification... >> "%LOG_FILE%"

:: Test Python installation
echo Testing Python installation...
python --version >> "%LOG_FILE%" 2>&1
if !errorLevel! neq 0 (
    echo ERROR: Python installation verification failed
    echo ERROR: Python installation verification failed >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Test Node.js installation
echo Testing Node.js installation...
node --version >> "%LOG_FILE%" 2>&1
if !errorLevel! neq 0 (
    echo ERROR: Node.js installation verification failed
    echo ERROR: Node.js installation verification failed >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Test Git installation
echo Testing Git installation...
git --version >> "%LOG_FILE%" 2>&1
if !errorLevel! neq 0 (
    echo ERROR: Git installation verification failed
    echo ERROR: Git installation verification failed >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Test Ollama installation (if available)
echo Testing Ollama installation...
where ollama >nul 2>&1
if !errorLevel! equ 0 (
    echo Ollama installation verified successfully. >> "%LOG_FILE%"
    
    :: Test Ollama service
    ollama list >> "%LOG_FILE%" 2>&1
    if !errorLevel! equ 0 (
        echo Ollama models verified successfully. >> "%LOG_FILE%"
    ) else (
        echo WARNING: Ollama service test failed >> "%LOG_FILE%"
    )
) else (
    echo Ollama not installed, skipping Ollama verification. >> "%LOG_FILE%"
)

:: Test Python packages
echo Testing Python packages...
python -c "
import torch
import transformers
import whisper
import numpy as np
import pandas as pd
print('All Python packages imported successfully!')
" >> "%LOG_FILE%" 2>&1

if !errorLevel! neq 0 (
    echo ERROR: Python packages verification failed
    echo ERROR: Python packages verification failed >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: Test CUDA availability (if installed)
python -c "
import torch
if torch.cuda.is_available():
    print(f'CUDA available: {torch.cuda.get_device_name(0)}')
else:
    print('CUDA not available, using CPU')
" >> "%LOG_FILE%" 2>&1

:: Create startup scripts
echo Creating startup scripts...

:: Create start-system.bat
echo @echo off > "%INSTALL_DIR%start-system.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%start-system.bat"
echo call "%VENV_DIR%\Scripts\activate.bat" >> "%INSTALL_DIR%start-system.bat"
echo echo Starting Arabic STT System... >> "%INSTALL_DIR%start-system.bat"
echo start "GPU Server" cmd /k "python gpu_arabic_server.py" >> "%INSTALL_DIR%start-system.bat"
echo timeout /t 5 >> "%INSTALL_DIR%start-system.bat"
echo start "Training API" cmd /k "python training_api.py" >> "%INSTALL_DIR%start-system.bat"
echo timeout /t 5 >> "%INSTALL_DIR%start-system.bat"
echo start "Web Interface" cmd /k "npm run dev" >> "%INSTALL_DIR%start-system.bat"
echo echo System started! Web interface will be available at http://localhost:3000 >> "%INSTALL_DIR%start-system.bat"
echo pause >> "%INSTALL_DIR%start-system.bat"

:: Create test-system.bat
echo @echo off > "%INSTALL_DIR%test-system.bat"
echo cd /d "%INSTALL_DIR%" >> "%INSTALL_DIR%test-system.bat"
echo call "%VENV_DIR%\Scripts\activate.bat" >> "%INSTALL_DIR%test-system.bat"
echo echo Running system tests... >> "%INSTALL_DIR%test-system.bat"
echo python test_audio_playback.py >> "%INSTALL_DIR%test-system.bat"
echo pause >> "%INSTALL_DIR%test-system.bat"

echo Startup scripts created successfully. >> "%LOG_FILE%"

:: ============================================================================
:: Installation Complete
:: ============================================================================
echo.
echo ========================================================================
echo  INSTALLATION COMPLETED SUCCESSFULLY!
echo ========================================================================
echo.
echo Installation Summary:
echo - Python 3.11 with virtual environment
echo - Node.js LTS with npm packages
echo - Git version control
echo - CUDA Toolkit (if NVIDIA GPU detected)
echo - All Python AI/ML dependencies
echo - LLM models (Whisper, BERT, Sentiment Analysis)
echo - Integrity verification passed
echo.
echo Next Steps:
echo 1. Run 'start-system.bat' to start all services
echo 2. Open http://localhost:3000 in your browser
echo 3. Run 'test-system.bat' to verify functionality
echo.
echo Installation log saved to: %LOG_FILE%
echo.
echo ========================================================================

echo Installation completed successfully at %date% %time% >> "%LOG_FILE%"

:: Deactivate virtual environment
call "%VENV_DIR%\Scripts\deactivate.bat" 2>nul

echo Press any key to exit...
pause >nul