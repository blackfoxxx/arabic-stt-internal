@echo off
setlocal enabledelayedexpansion

:: Arabic STT System Startup Script
:: ================================
:: This script starts all system components in the correct order
:: Includes health checks and automatic recovery

echo.
echo ========================================
echo Arabic STT System - System Startup
echo ========================================
echo.

:: Set colors for output
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "NC=[0m"

:: Configuration
set "FRONTEND_PORT=3000"
set "BACKEND_PORT=8000"
set "TRAINING_PORT=8001"
set "MAX_STARTUP_WAIT=30"

:: Check if we're in the correct directory
if not exist "package.json" (
    echo %RED%Error: Please run this script from the project root directory%NC%
    echo Current directory: %CD%
    echo Expected files: package.json, gpu_arabic_server.py, training_api.py
    pause
    exit /b 1
)

echo %BLUE%Initializing Arabic STT System...%NC%
echo.

:: Function to check if port is in use
:check_port
netstat -an | find ":%1 " >nul 2>&1
if errorlevel 1 (
    set "PORT_%1_STATUS=FREE"
) else (
    set "PORT_%1_STATUS=BUSY"
)
goto :eof

:: Function to wait for service to be ready
:wait_for_service
set "service_name=%1"
set "port=%2"
set "max_wait=%3"
set "wait_count=0"

echo %YELLOW%Waiting for %service_name% to be ready on port %port%...%NC%

:wait_loop
call :check_port %port%
if "!PORT_%port%_STATUS!"=="BUSY" (
    echo %GREEN%✓ %service_name% is ready on port %port%%NC%
    goto :eof
)

set /a wait_count+=1
if %wait_count% geq %max_wait% (
    echo %RED%✗ Timeout waiting for %service_name% on port %port%%NC%
    goto :eof
)

timeout /t 1 /nobreak >nul
goto wait_loop

:: Check system prerequisites
echo %CYAN%Checking system prerequisites...%NC%

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%✗ Python is not installed or not in PATH%NC%
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
) else (
    echo %GREEN%✓ Python is available%NC%
)

:: Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo %RED%✗ Node.js is not installed or not in PATH%NC%
    echo Please install Node.js and try again
    pause
    exit /b 1
) else (
    echo %GREEN%✓ Node.js is available%NC%
)

:: Check Ollama (optional)
echo %CYAN%Checking Ollama service...%NC%
ollama --version >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%⚠ Ollama is not installed or not in PATH%NC%
    echo %YELLOW%LLM features will be limited without Ollama%NC%
    set "OLLAMA_AVAILABLE=false"
) else (
    echo %GREEN%✓ Ollama is available%NC%
    set "OLLAMA_AVAILABLE=true"
    
    :: Check if Ollama service is running
    ollama list >nul 2>&1
    if errorlevel 1 (
        echo %YELLOW%⚠ Ollama service is not running, starting...%NC%
        
        :: Start Ollama service in background
        start "Ollama Service" /min ollama serve
        
        :: Wait a moment for service to start
        timeout /t 3 /nobreak >nul
        
        :: Check again
        ollama list >nul 2>&1
        if errorlevel 1 (
            echo %RED%✗ Failed to start Ollama service%NC%
            set "OLLAMA_AVAILABLE=false"
        ) else (
            echo %GREEN%✓ Ollama service started successfully%NC%
            
            :: Check for available models
            for /f "tokens=*" %%i in ('ollama list 2^>nul') do (
                echo %%i | findstr /C:"llama3.1" >nul && echo %GREEN%  ✓ Llama 3.1 model available%NC%
                echo %%i | findstr /C:"mistral" >nul && echo %GREEN%  ✓ Mistral model available%NC%
                echo %%i | findstr /C:"qwen2.5" >nul && echo %GREEN%  ✓ Qwen2.5 model available%NC%
                echo %%i | findstr /C:"phi3" >nul && echo %GREEN%  ✓ Phi-3 model available%NC%
            )
        )
    ) else (
        echo %GREEN%✓ Ollama service is already running%NC%
        
        :: Show available models
        echo %CYAN%Available Ollama models:%NC%
        for /f "skip=1 tokens=1" %%i in ('ollama list 2^>nul') do (
            if not "%%i"=="" echo %GREEN%  ✓ %%i%NC%
        )
    )
)

:: Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo %GREEN%✓ Python virtual environment found%NC%
    call venv\Scripts\activate.bat
) else (
    echo %YELLOW%⚠ Virtual environment not found, using system Python%NC%
)

:: Check critical files
set "critical_files=gpu_arabic_server.py training_api.py multimodal_analysis_system.py"
for %%f in (%critical_files%) do (
    if exist "%%f" (
        echo %GREEN%✓ %%f found%NC%
    ) else (
        echo %RED%✗ %%f missing%NC%
        echo Please ensure all system files are present
        pause
        exit /b 1
    )
)

:: Check Node.js dependencies
if exist "node_modules" (
    echo %GREEN%✓ Node.js dependencies installed%NC%
) else (
    echo %YELLOW%⚠ Node.js dependencies not found, installing...%NC%
    npm install
    if errorlevel 1 (
        echo %RED%✗ Failed to install Node.js dependencies%NC%
        pause
        exit /b 1
    )
)

echo.
echo %CYAN%Starting system components...%NC%
echo.

:: Check if ports are already in use
call :check_port %FRONTEND_PORT%
call :check_port %BACKEND_PORT%
call :check_port %TRAINING_PORT%

if "!PORT_%FRONTEND_PORT%_STATUS!"=="BUSY" (
    echo %YELLOW%⚠ Port %FRONTEND_PORT% is already in use%NC%
    echo %YELLOW%Frontend may already be running%NC%
)

if "!PORT_%BACKEND_PORT%_STATUS!"=="BUSY" (
    echo %YELLOW%⚠ Port %BACKEND_PORT% is already in use%NC%
    echo %YELLOW%Backend API may already be running%NC%
)

if "!PORT_%TRAINING_PORT%_STATUS!"=="BUSY" (
    echo %YELLOW%⚠ Port %TRAINING_PORT% is already in use%NC%
    echo %YELLOW%Training API may already be running%NC%
)

:: Create logs directory
if not exist "logs" mkdir logs

:: Start Backend API Server
echo %BLUE%1. Starting Backend API Server (GPU Arabic Server)...%NC%
start "Arabic STT - Backend API" cmd /k "title Arabic STT - Backend API && python gpu_arabic_server.py"

:: Wait for backend to be ready
call :wait_for_service "Backend API" %BACKEND_PORT% %MAX_STARTUP_WAIT%

:: Start Training API Server
echo %BLUE%2. Starting Training API Server...%NC%
start "Arabic STT - Training API" cmd /k "title Arabic STT - Training API && python training_api.py"

:: Wait for training API to be ready
call :wait_for_service "Training API" %TRAINING_PORT% %MAX_STARTUP_WAIT%

:: Start Frontend Development Server
echo %BLUE%3. Starting Frontend Development Server...%NC%
start "Arabic STT - Frontend" cmd /k "title Arabic STT - Frontend && npm run dev"

:: Wait for frontend to be ready
call :wait_for_service "Frontend" %FRONTEND_PORT% %MAX_STARTUP_WAIT%

:: System startup complete
echo.
echo %GREEN%========================================%NC%
echo %GREEN%🎉 SYSTEM STARTUP COMPLETE%NC%
echo %GREEN%========================================%NC%
echo.

:: Display service status
echo %CYAN%Service Status:%NC%
call :check_port %FRONTEND_PORT%
if "!PORT_%FRONTEND_PORT%_STATUS!"=="BUSY" (
    echo %GREEN%✓ Frontend Server: Running on http://localhost:%FRONTEND_PORT%%NC%
) else (
    echo %RED%✗ Frontend Server: Not responding%NC%
)

call :check_port %BACKEND_PORT%
if "!PORT_%BACKEND_PORT%_STATUS!"=="BUSY" (
    echo %GREEN%✓ Backend API: Running on http://localhost:%BACKEND_PORT%%NC%
) else (
    echo %RED%✗ Backend API: Not responding%NC%
)

call :check_port %TRAINING_PORT%
if "!PORT_%TRAINING_PORT%_STATUS!"=="BUSY" (
    echo %GREEN%✓ Training API: Running on http://localhost:%TRAINING_PORT%%NC%
) else (
    echo %RED%✗ Training API: Not responding%NC%
)

echo.
echo %CYAN%Available Endpoints:%NC%
echo %BLUE%🌐 Main Application:%NC%      http://localhost:%FRONTEND_PORT%
echo %BLUE%📊 Multimodal Results:%NC%    http://localhost:%FRONTEND_PORT%/multimodal-results
echo %BLUE%🔧 Backend API Docs:%NC%      http://localhost:%BACKEND_PORT%/docs
echo %BLUE%🎓 Training API Docs:%NC%     http://localhost:%TRAINING_PORT%/docs
echo %BLUE%📈 Health Check:%NC%          http://localhost:%BACKEND_PORT%/health

echo.
echo %CYAN%System Features:%NC%
echo %GREEN%✓ Arabic Speech-to-Text (Whisper)%NC%
echo %GREEN%✓ Multimodal Analysis%NC%
echo %GREEN%✓ Truth Detection%NC%
echo %GREEN%✓ Sentiment Analysis%NC%
echo %GREEN%✓ Speaker Identification%NC%
echo %GREEN%✓ Real-time Audio Playback%NC%
echo %GREEN%✓ Arabic RTL Text Support%NC%
echo %GREEN%✓ GPU Acceleration (if available)%NC%
if "%OLLAMA_AVAILABLE%"=="true" (
    echo %GREEN%✓ LLM Enhancement (Ollama)%NC%
) else (
    echo %YELLOW%⚠ LLM Enhancement (Ollama not available)%NC%
)

echo.
echo %CYAN%Quick Start Guide:%NC%
echo 1. Open your browser to: %BLUE%http://localhost:%FRONTEND_PORT%%NC%
echo 2. Upload an Arabic audio file (.wav, .mp3, .m4a)
echo 3. Wait for processing to complete
echo 4. View comprehensive analysis results
echo 5. Use the interactive features to explore the data

echo.
echo %CYAN%Development Commands:%NC%
echo %YELLOW%Frontend Development:%NC%  npm run dev
echo %YELLOW%Backend API:%NC%           python gpu_arabic_server.py
echo %YELLOW%Training API:%NC%          python training_api.py
echo %YELLOW%Run Tests:%NC%             test-system.bat
echo %YELLOW%Verify Installation:%NC%   python verify-installation.py
if "%OLLAMA_AVAILABLE%"=="true" (
    echo %YELLOW%Ollama Models:%NC%         ollama list
    echo %YELLOW%Ollama Chat:%NC%           ollama run llama3.1
)

echo.
echo %CYAN%Troubleshooting:%NC%
echo - If services don't start, check if ports are already in use
echo - For GPU issues, ensure CUDA is properly installed
echo - For model loading issues, check internet connection
echo - Run test-system.bat to diagnose problems
echo - Check logs in the opened terminal windows
if "%OLLAMA_AVAILABLE%"=="false" (
    echo - For LLM features, install Ollama: https://ollama.ai/download
)

echo.
echo %YELLOW%Note: Keep this window open to monitor the system%NC%
echo %YELLOW%Close this window or press Ctrl+C to stop all services%NC%

:: Monitor system health
echo.
echo %CYAN%Monitoring system health... (Press Ctrl+C to stop)%NC%
echo.

:monitor_loop
timeout /t 10 /nobreak >nul

:: Check if services are still running
call :check_port %FRONTEND_PORT%
call :check_port %BACKEND_PORT%
call :check_port %TRAINING_PORT%

set "services_running=0"
if "!PORT_%FRONTEND_PORT%_STATUS!"=="BUSY" set /a services_running+=1
if "!PORT_%BACKEND_PORT%_STATUS!"=="BUSY" set /a services_running+=1
if "!PORT_%TRAINING_PORT%_STATUS!"=="BUSY" set /a services_running+=1

if %services_running% equ 3 (
    echo %GREEN%[%time%] All services running normally (%services_running%/3)%NC%
) else if %services_running% geq 1 (
    echo %YELLOW%[%time%] Some services may have issues (%services_running%/3)%NC%
) else (
    echo %RED%[%time%] All services appear to be down (%services_running%/3)%NC%
    echo %RED%System may need to be restarted%NC%
)

goto monitor_loop

:: This point should never be reached due to the infinite loop above
:: But included for completeness
echo.
echo %YELLOW%System monitoring stopped%NC%
pause