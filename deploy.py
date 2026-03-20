#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一键部署脚本
"""

import os
import sys
import subprocess
import yaml
import platform
from typing import Dict, Any


class DeploymentManager:
    """部署管理器"""
    
    def __init__(self, config_file: str = "config.yaml"):
        """初始化部署管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.system_info = self._get_system_info()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[错误] 配置文件加载失败: {e}")
            return {}
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'machine': platform.machine(),
            'python_version': platform.python_version(),
        }
    
    def check_environment(self) -> bool:
        """检查运行环境"""
        print("="*60)
        print("环境检查")
        print("="*60)
        
        all_ok = True
        
        # 检查Python版本
        python_version = self.system_info['python_version']
        print(f"[检查] Python版本: {python_version}")
        
        major, minor, _ = map(int, python_version.split('.'))
        if major < 3 or (major == 3 and minor < 10):
            print("[错误] Python版本需要 >= 3.10")
            all_ok = False
        else:
            print("[✓] Python版本满足要求")
        
        # 检查CUDA
        if self.config.get('gpu', {}).get('use_gpu', True):
            try:
                import pynvml
                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandle(0)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                total_memory = info.total // (1024**2)
                print(f"[检查] GPU内存: {total_memory} MB")
                print("[✓] GPU已检测")
            except:
                print("[警告] 未检测到GPU,将使用CPU模式")
        
        # 检查LM Studio
        if self.config.get('ai', {}).get('enable', True):
            api_url = self.config['ai']['api_url']
            try:
                import requests
                response = requests.get(api_url.replace('/chat/completions', '/models'), 
                                     timeout=5)
                if response.status_code == 200:
                    print("[✓] LM Studio API可访问")
                else:
                    print("[警告] LM Studio API无法访问,AI分类将被禁用")
            except:
                print("[警告] 无法连接LM Studio,请确保LM Studio已启动")
                print(f"[提示] API地址: {api_url}")
        
        print()
        return all_ok
    
    def install_dependencies(self):
        """安装依赖"""
        print("="*60)
        print("安装依赖")
        print("="*60)
        
        # 检查是否已安装
        try:
            import paddlepaddle
            print("[检查] PaddlePaddle已安装")
        except:
            print("[安装] 安装PaddlePaddle...")
            self._run_command("pip install paddlepaddle-gpu")
        
        try:
            import paddleocr
            print("[检查] PaddleOCR已安装")
        except:
            print("[安装] 安装PaddleOCR...")
            self._run_command("pip install paddleocr")
        
        # 安装其他依赖
        print("[安装] 安装其他依赖...")
        self._run_command("pip install -r requirements.txt")
        
        print("[✓] 依赖安装完成\n")
    
    def setup_directories(self):
        """设置目录结构"""
        print("="*60)
        print("设置目录")
        print("="*60)
        
        directories = [
            self.config.get('output', {}).get('directory', './output'),
            './logs',
            './temp'
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"[创建] 目录: {directory}")
        
        print("[✓] 目录设置完成\n")
    
    def test_deployment(self):
        """测试部署"""
        print("="*60)
        print("测试部署")
        print("="*60)
        
        try:
            # 测试OCR
            print("[测试] OCR识别器...")
            from ocr_recognizer import OCRRecognizer
            ocr = OCRRecognizer(use_gpu=self.config['gpu']['use_gpu'])
            ocr.initialize()
            print("[✓] OCR初始化成功")
            
            # 测试AI分类器
            if self.config['ai']['enable']:
                print("[测试] AI分类器...")
                from ai_classifier import AIClassifier
                ai = AIClassifier(
                    api_url=self.config['ai']['api_url'],
                    model_name=self.config['ai']['model_name'],
                    enable=True
                )
                print("[✓] AI分类器初始化成功")
            
            print("[✓] 部署测试完成\n")
            return True
            
        except Exception as e:
            print(f"[错误] 部署测试失败: {e}\n")
            return False
    
    def _run_command(self, command: str):
        """运行命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"[错误] 命令执行失败: {e}")
            print(f"[错误] {e.stderr}")
    
    def deploy(self):
        """执行部署"""
        print("\n" + "="*60)
        print("敏感数据识别与分类系统 - 一键部署")
        print("="*60)
        print(f"[系统] {self.system_info['os']} {self.system_info['os_version']}")
        print(f"[系统] Python {self.system_info['python_version']}")
        print()
        
        # 检查环境
        if not self.check_environment():
            print("[错误] 环境检查失败,请修复后重试")
            return False
        
        # 安装依赖
        self.install_dependencies()
        
        # 设置目录
        self.setup_directories()
        
        # 测试部署
        if self.test_deployment():
            print("="*60)
            print("✓ 部署成功!")
            print("="*60)
            print()
            print("使用方法:")
            print("  python main.py <pcap文件>")
            print()
            print("示例:")
            print("  python main.py test_sample.pcap")
            print()
            return True
        else:
            print("[错误] 部署失败")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='一键部署脚本')
    parser.add_argument('--config', '-c', default='config.yaml', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建部署管理器
    manager = DeploymentManager(config_file=args.config)
    
    # 执行部署
    success = manager.deploy()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
