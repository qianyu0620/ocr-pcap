#!/bin/bash

echo "========================================"
echo "敏感数据识别与分类系统 - 一键启动"
echo "========================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python,请先安装Python 3.10+"
    exit 1
fi

echo "[1] 检查依赖..."
python3 -c "import paddlepaddle" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[提示] 未检测到依赖包,正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败!"
        exit 1
    fi
fi

echo "[2] 检查PCAP文件..."
if [ ! -f "test_sample.pcap" ]; then
    echo "[提示] 未找到test_sample.pcap文件"
    echo "请将PCAP文件放在当前目录下,或者手动指定:"
    echo "  python3 main.py <pcap文件路径>"
    echo
    read -p "请输入PCAP文件路径: " pcap_path
    if [ -z "$pcap_path" ]; then
        echo "[错误] 未指定文件!"
        exit 1
    fi
    PCAP_FILE="$pcap_path"
else
    PCAP_FILE="test_sample.pcap"
fi

echo "[3] 开始处理..."
echo

# 运行主程序
python3 main.py "$PCAP_FILE"

if [ $? -ne 0 ]; then
    echo
    echo "[错误] 程序运行失败!"
    exit 1
fi

echo
echo "========================================"
echo "处理完成!"
echo "========================================"
echo "请将生成的CSV文件上传到验证靶机:"
echo "https://gdufs2025.dasctf.com/"
echo "========================================"
echo
