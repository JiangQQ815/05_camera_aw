@echo off
chcp 65001 > nul
echo ============================================================
echo    多设备并行执行 - 自动分发用例
echo ============================================================
echo.

:: 检查Python环境
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python
    pause
    exit /b 1
)

:: 获取所有设备
echo [1/3] 扫描已连接设备...
adb devices > temp_devices.txt

set DEVICES=
set /a COUNT=0
for /f "skip=1 tokens=1,2" %%a in ('findstr "device" temp_devices.txt') do (
    set DEVICES=!DEVICES!%%a,
    set /a COUNT+=1
)

if %COUNT%==0 (
    echo [错误] 没有找到已连接的设备
    del temp_devices.txt
    pause
    exit /b 1
)

:: 去掉最后一个逗号
set DEVICES=%DEVICES:~0,-1%

echo 找到 %COUNT% 个设备: %DEVICES%
echo.

:: 选择测试类型
echo [2/3] 选择测试集：
echo   1. 拍照模式 (PHOTO)
echo   2. 录像模式 (VIDEO)
echo   3. 夜景模式 (NIGHT)
echo   4. 专业模式 (PRO)
echo   5. 全部模式 (ALL)
set /p choice=请选择 (1-5):

if "%choice%"=="1" set TEST_TARGET=test_photo_mode
if "%choice%"=="2" set TEST_TARGET=test_video_mode
if "%choice%"=="3" set TEST_TARGET=test_night_mode
if "%choice%"=="4" set TEST_TARGET=test_pro_mode
if "%choice%"=="5" set TEST_TARGET=test_all_modes

:: 创建报告目录
set REPORT_DIR=%~dp0reports\parallel_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set REPORT_DIR=%REPORT_DIR: =0%
mkdir "%REPORT_DIR%" 2>nul

:: 并行执行目录
mkdir "%REPORT_DIR%\logs" 2>nul

echo [3/3] 开始并行执行...
echo   测试目标: %TEST_TARGET%
echo   设备数量: %COUNT%
echo   报告目录: %REPORT_DIR%
echo.

:: 启动并行执行
start "Device_1" cmd /c "python -m pytest test_cases/test_camera_template.py::TestHuaweiCameraAll::%TEST_TARGET% --device-serial=%DEVICES% --html="%REPORT_DIR%\device_1_report.html" --self-contained-html -v --tb=short > "%REPORT_DIR%\logs\device_1.log" 2>&1"

echo 已启动并行测试任务
echo 请查看报告: %REPORT_DIR%
echo.
pause
