@echo off
chcp 65001 >nul
echo ========================================
echo 敏感数据识别与分类系统 - 一键启动
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python,请先安装Python 3.10+
    pause
    exit /b 1
)

echo [1] 检查依赖...
pip show paddlepaddle >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 未检测到依赖包,正在安装...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败!
        pause
        exit /b 1
    )
)

echo [2] 检查PCAP文件...
if not exist "test_sample.pcap" (
    echo [提示] 未找到test_sample.pcap文件
    echo 请将PCAP文件放在当前目录下,或者手动指定:
    echo   python main.py ^<pcap文件路径^>
    echo.
    set /p pcap_path="请输入PCAP文件路径: "
    if "%pcap_path%"=="" (
        echo [错误] 未指定文件!
        pause
        exit /b 1
    )
    set PCAP_FILE=%pcap_path%
) else (
    set PCAP_FILE=test_sample.pcap
)

echo [3] 开始处理...
echo.

REM 运行主程序
python main.py "%PCAP_FILE%"

if %errorlevel% neq 0 (
    echo.
    echo [错误] 程序运行失败!
    pause
    exit /b 1
)

echo.
echo ========================================
echo 处理完成!
echo ========================================
echo 请将生成的CSV文件上传到验证靶机:
echo https://gdufs2025.dasctf.com/
echo ========================================
echo.
pause
