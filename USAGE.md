# 使用说明

## 环境要求

- 操作系统: Windows 11
- Python版本: 3.10或更高
- 硬件配置:
  - CPU: Intel 酷睿10代i5-10400 (推荐)
  - 内存: 16GB 或更多

## 安装步骤

### 1. 安装Python
- 下载Python 3.10+: https://www.python.org/downloads/
- 安装时勾选 "Add Python to PATH"

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 准备PCAP文件
将待分析的PCAP文件放到项目目录下,或使用绝对路径

## 使用方法

### 方法一: 一键启动 (推荐)

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

### 方法二: 命令行启动

```bash
python main.py test_sample.pcap
```

或指定输出目录:
```bash
python main.py test_sample.pcap --output ./results
```

### 方法三: Python脚本调用

```python
from main import SensitiveDataDetectionSystem

system = SensitiveDataDetectionSystem(
    pcap_file='test_sample.pcap',
    output_dir='./output'
)
system.initialize()
system.process()
```

## 输出说明

### CSV文件格式
程序会在输出目录生成CSV文件,包含以下字段:

| 字段名 | 说明 |
|--------|------|
| data_type | 敏感数据类型 (身份证号/银行卡号/手机号/邮箱等) |
| content | 识别到的敏感内容 |
| confidence | 识别置信度 (0-1) |
| source_ip | 源IP地址 |
| dest_ip | 目标IP地址 |
| timestamp | 时间戳 |

### 输出目录
默认输出目录: `./output/`
文件命名格式: `result_YYYYMMDD_HHMMSS.csv`

## 性能优化建议

1. **减少图片处理**: 如果不需要OCR识别,可以注释掉`_process_image_data`方法
2. **调整采样频率**: 修改`PerformanceMonitor`中的`interval`参数
3. **限制数据包数量**: 在`parse()`方法中设置`max_packets`参数

## 常见问题

### Q1: 提示"未检测到Python"
**A:** 请确保已安装Python 3.10+,并添加到系统PATH环境变量

### Q2: 依赖安装失败
**A:** 尝试使用国内镜像源:
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: OCR初始化失败
**A:** 首次运行会自动下载PaddleOCR模型,请确保网络畅通

### Q4: 处理时间过长
**A:** 可以在代码中设置最大处理包数:
```python
packets = self.parser.parse(max_packets=10000)
```

### Q5: 内存占用过高
**A:** 可以分批次处理数据包,或减少OCR图片的分辨率

## 验证步骤

1. 运行程序完成分析
2. 找到生成的CSV文件
3. 访问验证靶机: https://gdufs2025.dasctf.com/
4. 上传CSV文件获取准确率
5. 查看性能报告 (运行结束后会自动显示)

## 技术支持

如遇问题,请检查:
1. Python版本是否为3.10+
2. 依赖是否完整安装
3. PCAP文件是否有效
4. 磁盘空间是否充足

## 附录: 验证指标说明

系统的最终得分由以下四个部分组成:

1. **识别准确率得分** (权重70%): 识别准确率 / 最高识别准确率 × 100
2. **时间得分** (权重15%): 最短识别时间 / 当前识别时间 × 100
3. **CPU占用得分** (权重10%): 最低CPU占用率 / 当前CPU占用率 × 100
4. **内存占用得分** (权重5%): 最低内存占用率 / 当前内存占用率 × 100

**总得分** = 准确率×0.7 + 时间×0.15 + CPU×0.1 + 内存×0.05
