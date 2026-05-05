@echo off
echo ============================================================
echo BHIV TTG/TTV Integration - Comprehensive Startup and Test
echo ============================================================
echo.

REM Kill any existing processes on required ports
echo [1/6] Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8003') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8004') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8005') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8006') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak >nul

echo [2/6] Starting Prompt Runner (Port 8003)...
cd prompt-runner01
start "Prompt Runner" cmd /k "python run_server.py 8003"
cd ..
timeout /t 5 /nobreak >nul

echo [3/6] Starting BHIV Core (Port 8001)...
start "BHIV Core" cmd /k "python main.py"
timeout /t 5 /nobreak >nul

echo [4/6] Starting Integration Bridge (Port 8004)...
start "Integration Bridge" cmd /k "python integration_bridge.py"
timeout /t 3 /nobreak >nul

echo [5/6] Starting BHIV Bucket (Port 8005)...
start "BHIV Bucket" cmd /k "python bhiv_bucket.py"
timeout /t 3 /nobreak >nul

echo [6/6] Starting TTG/TTV API (Port 8006)...
start "TTG/TTV API" cmd /k "python ttg_ttv_api.py"
timeout /t 5 /nobreak >nul

echo.
echo ============================================================
echo All services started! Waiting for initialization...
echo ============================================================
timeout /t 10 /nobreak >nul

echo.
echo ============================================================
echo Running Comprehensive Flow Tests...
echo ============================================================
python comprehensive_flow_test.py

echo.
echo ============================================================
echo Startup Complete!
echo ============================================================
echo.
echo Services running:
echo   - Prompt Runner:       http://localhost:8003
echo   - BHIV Core:           http://localhost:8001
echo   - Integration Bridge:  http://localhost:8004
echo   - BHIV Bucket:         http://localhost:8005
echo   - TTG/TTV API:         http://localhost:8006
echo.
echo Test Report: test_report.json
echo Breaking Points: BREAKING_POINTS_ANALYSIS.md
echo.
echo Press any key to view test report...
pause >nul

if exist test_report.json (
    type test_report.json
) else (
    echo Test report not found.
)

echo.
echo Press any key to exit...
pause >nul
