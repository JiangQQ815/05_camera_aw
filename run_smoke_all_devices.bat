@echo off
chcp 65001 > nul
echo ============================================================
echo    多设备并行执行 - 快速冒烟测试
echo ============================================================
echo.

:: 检查Python环境
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python
    pause
    exit /b 1
)

:: 检查设备
adb devices > temp_devices.txt
findstr /C:"device" temp_devices.txt > nul
if errorlevel 1 (
    echo [错误] 没有找到已连接的设备
    del temp_devices.txt
    pause
    exit /b 1
)

:: 获取第一个设备（冒烟测试只用一台）
for /f "skip=1 tokens=1" %%a in ('findstr "device" temp_devices.txt') do (
    set DEVICE=%%a
    goto :run_test
)

:run_test
echo 使用设备: %DEVICE%
echo.

:: 创建报告目录
set REPORT_DIR=%~dp0reports\smoke_%date:~0,4%%date:~5,2%%date:~8,2%
mkdir "%REPORT_DIR%" 2>nul

:: 运行冒烟测试
echo 开始执行冒烟测试...
python -m pytest test_cases/test_camera_template.py::TestHuaweiCameraTemplate::test_quick_smoke ^
    --device-serial=%DEVICE% ^
    --html="%REPORT_DIR%\smoke_report.html" ^
    --self-contained-html ^
    -v --tb=short

echo.
echo [完成] 报告: %REPORT_DIR%\smoke_report.html

del temp_devices.txt
pause
