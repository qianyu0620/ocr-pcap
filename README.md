## 项目简介
基于OCR技术和国产AI模型的敏感数据识别与分类系统，用于分析PCAP流量文件中的敏感信息。

## 技术架构

### 核心技术栈
- **编程语言**: Python 3.10+  
- **PCAP解析**: Scapy
- **OCR识别**: PaddleOCR (国产AI模型)
- **敏感数据识别**: 正则表达式 + 深度学习模型
- **数据提取**: requests, pyshark

### 系统模块
1. **流量解析模块**: 解析PCAP文件，提取HTTP/HTTPS/FTP等协议流量
2. **数据提取模块**: 从流量中提取文本、图片等多格式数据
3. **OCR识别模块**: 使用PaddleOCR识别图片中的文本信息
4. **敏感数据分类模块**: 识别身份证、银行卡、手机号、邮箱等敏感信息
5. **结果输出模块**: 生成符合格式的CSV文件
6. **性能监控模块**: 监控CPU、内存、运行时间等指标

## 安装依赖

```bash 
pip install -r requirements.txt
```

## 使用方法

### 一键启动
```bash  
python main.py test_sample.pcap
```
### 使用参数说明
```bash  
python main.py <pcap文件路径> [--output <输出路径>]
```

## 系统要求
- Windows 11
- Python 3.10+ 
- Intel 酷睿10代i5-10400 (推荐)
- 16G 内存
- 处理时间: 10分钟

## 输出格式
系统将生成符合example.csv格式的结果文件，包含以下字段：
- 数据类型
- 敏感内容
- 源IP
- 目标IP
- 时间戳
- 置信度

  
![生成报告展示1](https://github.com/qianyu0620/ocr-pcap/blob/main/%E7%94%9F%E6%88%90%E6%8A%A5%E5%91%8A%E7%A4%BA%E4%BE%8B%E5%9B%BE/1.PNG)
![生成报告展示2](https://github.com/qianyu0620/ocr-pcap/blob/main/%E7%94%9F%E6%88%90%E6%8A%A5%E5%91%8A%E7%A4%BA%E4%BE%8B%E5%9B%BE/2.PNG)
![生成报告展示3](https://github.com/qianyu0620/ocr-pcap/blob/main/%E7%94%9F%E6%88%90%E6%8A%A5%E5%91%8A%E7%A4%BA%E4%BE%8B%E5%9B%BE/3.PNG)

## 测试pcap文件下载：https://pan.baidu.com/s/1RS09TED2zWpY1A6Z5l0Byw?pwd=bq2n
## Test pcap file download: https://pan.baidu.com/s/1RS09TED2zWpY1A6Z5l0Byw?pwd=bq2n
