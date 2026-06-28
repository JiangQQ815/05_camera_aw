@echo off
chcp 65001 > nul
echo ============================================================
echo    相机自动化测试 - 多设备并行执行
echo ============================================================
echo.

:: 检查Python环境
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.x
    pause
    exit /b 1
)

:: 检查设备连接
echo [1/5] 检查已连接的设备...
adb devices > devices_list.txt
type devices_list.txt
echo.

:: 解析设备数量
set device_count=0
for /f "skip=1 tokens=1,2" %%a in (devices_list.txt) do (
    if "%%b"=="device" (
        set /a device_count+=1
    )
)

if %device_count%==0 (
    echo [错误] 没有找到已连接的设备
    echo 请确保：
    echo   1. 手机已通过USB连接到电脑
    echo   2. USB调试已开启
    echo   3. 手机已授权此电脑进行USB调试
    del devices_list.txt
    pause
    exit /b 1
)

echo 找到 %device_count% 个设备
echo.

:: 选择测试模式
echo [2/5] 选择测试模式：
echo   1. 快速冒烟测试 (SMOKE)
echo   2. 拍照模式测试 (PHOTO)
echo   3. 录像模式测试 (VIDEO)
echo   4. 全部模式测试 (ALL)
echo   5. 自定义测试
echo.
set /p test_mode=请选择测试模式 (1-5):

:: 选择执行模式
echo [3/5] 选择执行模式：
echo   1. 串行执行 (所有设备顺序执行相同用例)
echo   2. 并行执行 (用例分发到多设备)
echo   3. 单设备执行 (指定设备运行)
set /p exec_mode=请选择执行模式 (1-3):

:: 生成报告目录
set report_dir=%~dp0reports\%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set report_dir=%report_dir: =0%
mkdir "%report_dir%" 2>nul

:: 获取设备列表
set devices=
for /f "skip=1 tokens=1,2" %%a in (devices_list.txt) do (
    if "%%b"=="device" (
        if defined devices (
            set devices=!devices!,%%a
        ) else (
            set devices=%%a
        )
    )
)

echo [4/5] 准备执行测试...
echo   设备: %devices%
echo   报告目录: %report_dir%
echo.

:: 设置pytest参数
set PYTEST_ARGS=--html="%report_dir%/report.html" --self-contained-html -v

:: 根据测试模式设置用例
if "%test_mode%"=="1" (
    set TEST_MODULE=test_camera_template.py::TestHuaweiCameraTemplate::test_quick_smoke
) else if "%test_mode%"=="2" (
    set TEST_MODULE=test_camera_template.py::TestHuaweiCameraTemplate::test_photo_mode
) else if "%test_mode%"=="3" (
    set TEST_MODULE=test_camera_template.py::TestHuaweiCameraTemplate::test_video_mode
) else if "%test_mode%"=="4" (
    set TEST_MODULE=test_camera_template.py::TestHuaweiCameraAll::test_all_modes
) else (
    set TEST_MODULE=test_camera_template.py
)

echo [5/5] 开始执行测试...
echo ============================================================
echo.

:: 根据执行模式运行
if "%exec_mode%"=="1" (
    :: 串行执行 - 所有设备执行相同用例
    echo [串行模式] 多设备顺序执行相同用例...
    echo.
    for %%d in (%devices%) do (
        echo -------- 设备: %%d --------
        python -m pytest %TEST_MODULE% --device-serial=%%d %PYTEST_ARGS% --tb=short
        echo.
    )
) else if "%exec_mode%"=="2" (
    :: 并行执行 - 用例分发到多设备
    echo [并行模式] 多设备并行执行用例...
    echo.
    python -m pytest %TEST_MODULE% --devices=%devices% --distribute %PYTEST_ARGS% --tb=short
) else if "%exec_mode%"=="3" (
    :: 单设备执行
    echo [单设备模式] 在指定设备上执行...
    echo 请输入设备序列号:
    set /p target_device=
    echo.
    python -m pytest %TEST_MODULE% --device-serial=%target_device% %PYTEST_ARGS% --tb=short
)

echo ============================================================
echo.
echo [完成] 测试执行完毕
echo 报告位置: %report_dir%\report.html
echo.

:: 清理临时文件
del devices_list.txt 2>nul

:: 显示设备统计
echo 按任意键显示设备统计...
pause > nul
python -c "from device_manager import device_manager; device_manager.connect_all_devices(); device_manager.print_status()"

pause
