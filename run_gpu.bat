@echo off
chcp 65001 >nul
echo ========================================
echo GPU加速版 - 敏感数据识别系统
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python,请先安装Python 3.10+
    pause
    exit /b 1
)

echo [1] 检查NVIDIA GPU...
nvidia-smi >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到NVIDIA GPU或驱动未安装
    echo 请访问: https://www.nvidia.com/Download/index.aspx
    pause
    exit /b 1
)

echo [√] NVIDIA GPU已检测
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

echo.
echo [2] 检查CUDA...
nvcc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] CUDA未检测到,将尝试使用CPU模式
    echo 建议安装CUDA: https://developer.nvidia.com/cuda-downloads
)

echo.
echo [3] 检查PaddlePaddle-GPU...
python -c "import paddle; print('PaddlePaddle版本:', paddle.__version__); print('GPU可用:', paddle.is_compiled_with_cuda())" 2>nul
if %errorlevel% neq 0 (
    echo [提示] PaddlePaddle-GPU未安装,正在安装...
    pip install paddlepaddle-gpu
    if %errorlevel% neq 0 (
        echo [错误] PaddlePaddle-GPU安装失败
        pause
        exit /b 1
    )
)

echo.
echo [4] 检查LM Studio (可选)...
curl -s http://localhost:1234/v1/models >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] LM Studio未运行,AI分类将被禁用
    echo [提示] 如需启用,请启动LM Studio并确保API运行在端口1234
) else (
    echo [√] LM Studio已检测
)

echo.
echo [5] 检查PCAP文件...
if not exist "test_sample.pcap" (
    echo [提示] 未找到test_sample.pcap文件
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

echo.
echo [6] 开始GPU加速处理...
echo.

REM 运行主程序
python main.py "%PCAP_FILE%" --config config.yaml

if %errorlevel% neq 0 (
    echo.
    echo [错误] 程序运行失败!
    pause
    exit /b 1
)

echo.
echo ========================================
echo GPU加速处理完成!
echo ========================================
echo 请将生成的CSV文件上传到验证靶机:
echo https://gdufs2025.dasctf.com/
echo ========================================
echo.
pause
