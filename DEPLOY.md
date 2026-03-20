# 一键部署指南

## 前置要求

### 必需环境
- **Python**: 3.10 或更高版本
- **CUDA**: 11.2 或更高版本 (如使用GPU)
- **操作系统**: Windows 10/11, Linux, macOS

### 可选环境
- **NVIDIA GPU**: 用于GPU加速OCR (推荐)
- **LM Studio**: 用于AI增强分类

## 快速部署

### 方法一: 一键部署脚本(推荐)

```bash
# Windows
python deploy.py

# Linux/Mac
python3 deploy.py
```

部署脚本会自动:
1. 检查系统环境
2. 检测GPU和LM Studio
3. 安装所需依赖
4. 创建必要目录
5. 测试系统功能

### 方法二: 手动部署

#### 1. 安装依赖

**有GPU (推荐):**
```bash
pip install -r requirements.txt
```

**无GPU:**
```bash
pip install paddlepaddle
pip install -r requirements.txt
```

#### 2. 启动LM Studio (可选)

1. 下载并安装 [LM Studio](https://lmstudio.ai/)
2. 启动LM Studio
3. 加载 Qwen2.5 模型
4. 启动本地API服务器 (默认端口: 1234)

#### 3. 配置系统

编辑 `config.yaml`:

```yaml
# GPU配置
gpu:
  use_gpu: true        # 是否使用GPU
  gpu_mem: 8000        # GPU内存(MB)

# AI分类配置
ai:
  enable: true          # 是否启用AI分类
  api_url: "http://localhost:1234/v1/chat/completions"
  model_name: "qwen2.5"
```

## 使用方法

### 基础使用

```bash
# 使用默认配置
python main.py test_sample.pcap

# 指定输出目录
python main.py test_sample.pcap --output ./results

# 限制解析包数
python main.py test_sample.pcap --max-packets 100000

# 使用自定义配置
python main.py test_sample.pcap --config custom.yaml
```

### 性能模式

**GPU加速模式 (推荐):**
```yaml
gpu:
  use_gpu: true
```

**CPU模式:**
```yaml
gpu:
  use_gpu: false
```

**AI增强模式:**
```yaml
ai:
  enable: true
```

## 配置说明

### config.yaml 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `gpu.use_gpu` | 是否使用GPU加速OCR | true |
| `gpu.gpu_mem` | GPU内存(MB) | 8000 |
| `ai.enable` | 是否启用AI分类 | true |
| `ai.api_url` | LM Studio API地址 | http://localhost:1234/v1/chat/completions |
| `ai.model_name` | 模型名称 | qwen2.5 |
| `pcap.max_packets` | 最大解析包数 | null (全部) |
| `output.directory` | 输出目录 | ./output |

## 故障排除

### GPU相关问题

**问题**: CUDA错误
```
解决: 
1. 检查CUDA版本: nvidia-smi
2. 安装正确版本的CUDA: https://developer.nvidia.com/cuda-downloads
3. 重启系统
```

**问题**: GPU内存不足
```
解决:
1. 降低gpu_mem配置值
2. 或设置use_gpu: false使用CPU
```

### LM Studio相关问题

**问题**: 无法连接LM Studio
```
解决:
1. 确保LM Studio已启动
2. 检查API地址: http://localhost:1234/v1/chat/completions
3. 或设置ai.enable: false禁用AI分类
```

### 性能问题

**问题**: 处理速度慢
```
解决:
1. 启用GPU: gpu.use_gpu = true
2. 禁用AI分类: ai.enable = false
3. 增加批处理大小
```

## 验证部署

运行测试命令:

```bash
# 测试OCR
python -c "from ocr_recognizer import OCRRecognizer; ocr=OCRRecognizer(); ocr.initialize(); print('OCR OK')"

# 测试AI分类
python -c "from ai_classifier import AIClassifier; ai=AIClassifier(); print('AI OK')"

# 测试完整系统
python main.py test_sample.pcap --max-packets 100
```

## 系统要求

### 最低配置
- CPU: 4核心
- 内存: 8GB
- 存储: 10GB可用空间
- GPU: 无 (CPU模式)

### 推荐配置
- CPU: Intel i5-10400 或更高
- 内存: 16GB
- 存储: 20GB可用空间
- GPU: NVIDIA GTX 1660 或更高 (6GB+)

### 最佳配置
- CPU: Intel i7/i9 或 AMD Ryzen 7/9
- 内存: 32GB
- 存储: 50GB SSD
- GPU: NVIDIA RTX 3060 或更高 (8GB+)

## 技术支持

如遇问题,请检查:
1. Python版本是否 >= 3.10
2. 依赖是否完整安装
3. GPU驱动是否正确安装
4. LM Studio是否正常启动
5. 配置文件是否正确

## 更新日志

### v2.0 (GPU+CPU混合版)
- ✅ 添加GPU加速OCR
- ✅ 集成LM Studio AI分类
- ✅ 一键部署脚本
- ✅ 配置文件支持
- ✅ 性能监控优化
