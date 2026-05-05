@echo off
echo ========================================
echo TTG/TTV Integration - Complete Startup
echo ========================================
echo.

echo Starting all services...
echo.

echo [1/5] Starting Prompt Runner (Port 8003)...
start "Prompt Runner" cmd /k "cd prompt-runner01 && python run_server.py 8003"
timeout /t 3 /nobreak >nul

echo [2/5] Starting Creator Core (Port 8000)...
start "Creator Core" cmd /k "cd creator-core\Core-Integrator-Sprint-1.1 && python main.py"
timeout /t 3 /nobreak >nul

echo [3/5] Starting BHIV Core (Port 8001)...
start "BHIV Core" cmd /k "python main.py"
timeout /t 3 /nobreak >nul

echo [4/5] Starting Bucket (Port 8005)...
start "Bucket" cmd /k "python bhiv_bucket.py"
timeout /t 3 /nobreak >nul

echo [5/5] Starting TTG/TTV Integration (Port 8006)...
start "TTG/TTV API" cmd /k "python ttg_ttv_api.py"
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Service URLs:
echo   Prompt Runner:    http://localhost:8003
echo   Creator Core:     http://localhost:8000
echo   BHIV Core:        http://localhost:8001
echo   Bucket:           http://localhost:8005
echo   TTG/TTV API:      http://localhost:8006
echo.
echo ========================================
echo Running Integration Tests...
echo ========================================
echo.

timeout /t 5 /nobreak >nul
python test_ttg_ttv_integration.py

echo.
echo ========================================
echo Integration test complete!
echo ========================================
echo.
echo Press any key to exit...
pause >nul
