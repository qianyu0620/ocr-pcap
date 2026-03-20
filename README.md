<img width   宽度="985" height="932" alt="捕获" src="https://github.com/user-attachments/assets/7c964a8a-46d0-44d6-933b-6af4a69f7eb4" /><img width   宽度="985" height="932" alt="image" src="https://github.com/user-attachments/assets/1862a703-55d7-4fb8-81f7-b03c06061b50" /># 敏感数据识别与分类系统

## 项目简介
基于OCR技术和国产AI模型的敏感数据识别与分类系统，用于分析PCAP流量文件中的敏感信息。

## 技术架构

### 核心技术栈
- **编程语言**: Python 3.10+   - **Programming Language   编程语言**: Python 3.10
- **PCAP解析**: Scapy
- **OCR识别**: PaddleOCR (国产AI模型)- **OCR Recognition   OCR识别**: PaddleOCR (a domestic AI model)
- **敏感数据识别**: 正则表达式 + 深度学习模型
- **数据提取**: requests, pyshark- **Data Extraction   数据提取**: requests, pyshark

### 系统模块
1. **流量解析模块**: 解析PCAP文件，提取HTTP/HTTPS/FTP等协议流量
2. **数据提取模块**: 从流量中提取文本、图片等多格式数据
3. **OCR识别模块**: 使用PaddleOCR识别图片中的文本信息
4. **敏感数据分类模块**: 识别身份证、银行卡、手机号、邮箱等敏感信息
5. **结果输出模块**: 生成符合格式的CSV文件
6. **性能监控模块**: 监控CPU、内存、运行时间等指标

## 安装依赖

```bash   ”“bash
pip install -r requirements.txt运行 `pip install -r requirements.txt` 安装依赖包。运行 `pip install -r requirements.txt` 安装依赖包。
```

## 使用方法

### 一键启动
```bash   ”“bash
python main.py test_sample.pcap运行 `python main.py test_sample.pcap` 命令。
```

### 使用参数说明
```bash   ”“bash
python main.py <pcap文件路径> [--output <输出路径>]python main.py < pcap file path> [--output ]
```

## 系统要求
- Windows 11
- Python 3.10+   - Python 3.10
- Intel 酷睿10代i5-10400 (推荐)Intel Core 10th Gen i5-10400 (Recommended)
- 16G 内存
- 处理时间: <10分钟

## 输出格式
系统将生成符合example.csv格式的结果文件，包含以下字段：
- 数据类型
- 敏感内容
- 源IP
- 目标IP
- 时间戳
- 置信度


## 生成报告效果：
<img width   宽度="785" height="249" alt="捕获" src="https://github.com/user-attachments/assets/e6fa8c00-39ff-48e2-b308-1fdc0037c98e" />
<img width   宽度="934" height="871" alt="捕获3" src="https://github.com/user-attachments/assets/521f2199-54c8-4199-8de3-f1e560266341" />
<img width   宽度="985" height="932" alt="捕获2" src="https://github.com/user-attachments/assets/84ee1e17-0bdd-4177-8616-1a9cf3301f45" />




## 测试pcap文件下载：https://pan.baidu.com/s/1RS09TED2zWpY1A6Z5l0Byw?pwd=bq2n
