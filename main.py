#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
敏感数据识别与分类系统 - 主程序
"""

import os
import sys
import argparse
import time
import multiprocessing
from datetime import datetime
from typing import List, Dict, Optional
import yaml

from pcap_parser import PCAPParser, PacketInfo
from ocr_recognizer import OCRRecognizer
from sensitive_data_classifier import SensitiveDataClassifier, SensitiveDataResult
from csv_exporter import CSVExporter
from performance_monitor import PerformanceMonitor
from result_visualizer import ResultVisualizer
from ai_classifier import AIClassifier
from gpu_monitor import GPUMonitor, GPUMetrics


class SensitiveDataDetectionSystem:
    """敏感数据识别与分类系统 (GPU+CPU混合版本)"""
    
    def __init__(self, pcap_file: str, output_dir: str = "./output", 
                 max_packets: Optional[int] = None, config_file: str = "config.yaml"):
        """初始化系统
        
        Args:
            pcap_file: PCAP文件路径
            output_dir: 输出目录
            max_packets: 最大解析包数
            config_file: 配置文件路径
        """
        self.pcap_file = pcap_file
        self.output_dir = output_dir
        self.max_packets = max_packets
        self.config = self._load_config(config_file)
        
        # 初始化各模块
        self.parser: Optional[PCAPParser] = None
        self.ocr: Optional[OCRRecognizer] = None
        self.classifier: Optional[SensitiveDataClassifier] = None
        self.ai_classifier: Optional[AIClassifier] = None
        self.exporter: Optional[CSVExporter] = None
        self.monitor: Optional[PerformanceMonitor] = None
        self.visualizer: Optional[ResultVisualizer] = None
        
        # 识别结果
        self.all_results: List[Dict[str, any]] = []
        self.metrics: Dict[str, any] = {}
    
    def _load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[警告] 配置文件加载失败: {e},使用默认配置")
            return {}
        
    def initialize(self):
        """初始化系统模块"""
        print("\n" + "="*60)
        print("敏感数据识别与分类系统 (GPU+CPU混合版)")
        print("="*60)
        print(f"[系统] 初始化系统模块...")
        
        # 初始化性能监控器
        self.monitor = PerformanceMonitor()
        
        # 初始化PCAP解析器 (单线程CPU)
        self.parser = PCAPParser(self.pcap_file)
        
        # 初始化OCR识别器 (GPU加速)
        use_gpu = self.config.get('gpu', {}).get('use_gpu', True)
        batch_size = self.config.get('gpu', {}).get('batch_size', 16)
        self.ocr = OCRRecognizer(use_angle_cls=True, lang='ch', use_gpu=use_gpu, batch_size=batch_size)
        
        # 初始化GPU监控器
        if use_gpu:
            self.gpu_monitor = GPUMonitor()
        else:
            self.gpu_monitor = None
        
        # 初始化分类器 (CPU)
        self.classifier = SensitiveDataClassifier()
        
        # 初始化AI分类器 (可选)
        ai_config = self.config.get('ai', {})
        if ai_config.get('enable', False):
            self.ai_classifier = AIClassifier(
                api_url=ai_config.get('api_url', 'http://localhost:1234/v1/chat/completions'),
                model_name=ai_config.get('model_name', 'qwen2.5'),
                enable=True
            )
        else:
            self.ai_classifier = AIClassifier(enable=False)
        
        # 初始化导出器
        self.exporter = CSVExporter(output_dir=self.output_dir)
        
        # 初始化可视化器
        self.visualizer = ResultVisualizer(output_dir=self.output_dir)
        
        print(f"[系统] 系统模块初始化完成")
        print(f"[系统] OCR加速: {'GPU' if use_gpu else 'CPU'}")
        print(f"[系统] AI分类: {'启用' if self.ai_classifier.enable else '禁用'}")
        if self.max_packets:
            print(f"[系统] 最大解析包数: {self.max_packets}")
        print("="*60 + "\n")
        
    def process(self) -> bool:
        """处理PCAP文件
        
        Returns:
            是否成功
        """
        try:
            # 开始性能监控
            self.monitor.start()
            
            # 步骤1: 解析PCAP文件
            print("\n[步骤 1/5] 解析PCAP文件")
            print("-" * 60)
            packets = self.parser.parse(
                max_packets=self.max_packets,
                show_progress=True
            )
            print(f"成功解析 {len(packets)} 个数据包")
            
            # 步骤2: 处理文本数据
            print("\n[步骤 2/5] 处理文本数据")
            print("-" * 60)
            self._process_text_data(packets)
            
            # 步骤3: 处理图片数据
            print("\n[步骤 3/5] 处理图片数据")
            print("-" * 60)
            self._process_image_data(packets)
            
            # 步骤3.5: AI增强分类
            if self.ai_classifier.enable:
                print("\n[步骤 3.5/5] AI增强分类")
                print("-" * 60)
                self._ai_enhance_classification()
            
            # 清理内存
            print("\n[内存管理] 清理数据包缓存...")
            del packets
            import gc
            gc.collect()
            print("[内存管理] 缓存已清理")
            
            # 步骤4: 导出结果
            print("\n[步骤 4/5] 导出结果")
            print("-" * 60)
            self._export_results()
            
            # 步骤5: 生成可视化报告
            print("\n[步骤 5/5] 生成可视化报告")
            print("-" * 60)
            self._generate_visualization()
            
            # 停止性能监控
            metrics = self.monitor.stop()
            self.metrics = metrics.to_dict()
            
            # 获取GPU性能指标
            if self.gpu_monitor:
                gpu_metrics = self.gpu_monitor.get_metrics()
                if gpu_metrics:
                    print("\nGPU性能指标:")
                    self.gpu_monitor.print_metrics(gpu_metrics)
                    self.metrics['gpu_utilization'] = gpu_metrics.gpu_utilization
                    self.metrics['gpu_memory'] = gpu_metrics.memory_percent
                    self.gpu_monitor.shutdown()
            
            # 打印性能报告
            self.monitor.print_summary()
            
            return True
            
        except Exception as e:
            print(f"[错误] 处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _process_text_data(self, packets: List[PacketInfo]):
        """处理文本数据(批量多线程版本)
        
        Args:
            packets: 数据包列表
        """
        text_packets = self.parser.get_packets_with_text()
        print(f"包含文本的数据包: {len(text_packets)}")
        
        if not text_packets:
            print("没有文本数据需要处理")
            return
        
        # 准备批量数据
        text_data_list = []
        for packet in text_packets:
            text_data_list.append({
                'text_data': packet.text_data,
                'source_ip': packet.source_ip,
                'dest_ip': packet.dest_ip,
                'timestamp': datetime.fromtimestamp(packet.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # 使用批量多线程分类
        results = self.classifier.classify_batch(text_data_list, show_progress=True)
        self.all_results.extend(results)
        
        print(f"文本数据处理完成,共识别 {len(text_packets)} 个数据包")
        
    def _process_image_data(self, packets: List[PacketInfo]):
        """处理图片数据(GPU加速版本)
        
        Args:
            packets: 数据包列表
        """
        image_packets = self.parser.get_packets_with_image()
        print(f"包含图片的数据包: {len(image_packets)}")
        
        if not image_packets:
            print("没有图片数据需要处理")
            return
        
        # 初始化OCR
        try:
            self.ocr.initialize()
        except Exception as e:
            print(f"OCR初始化失败: {e}")
            return
        
        # 准备批量数据
        image_data_list = []
        for packet in image_packets:
            image_data_list.append((packet.image_data, packet.source_ip, packet.dest_ip))
        
        # 使用GPU加速OCR识别
        ocr_results = self.ocr.recognize_batch_from_bytes(image_data_list, show_progress=True)
        
        # 对OCR结果进行敏感数据分类
        print(f"开始对OCR识别结果进行分类...")
        classification_results = self.classifier.classify_batch(ocr_results, show_progress=True)
        self.all_results.extend(classification_results)
        
        print(f"图片数据处理完成,共识别 {len(image_packets)} 个数据包")
    
    def _ai_enhance_classification(self):
        """AI增强分类"""
        if not self.ai_classifier.enable:
            print("AI分类已禁用,跳过")
            return
        
        # 提取文本数据
        text_packets = self.parser.get_packets_with_text()
        text_data_list = []
        for packet in text_packets:
            text_data_list.append({
                'text_data': packet.text_data,
                'source_ip': packet.source_ip,
                'dest_ip': packet.dest_ip,
                'timestamp': datetime.fromtimestamp(packet.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # AI分类
        ai_results = self.ai_classifier.classify_batch_with_ai(text_data_list, show_progress=True)
        self.all_results.extend(ai_results)
        
    def _export_results(self):
        """导出结果"""
        # 去重
        unique_results = self._deduplicate_results()
        print(f"去重前: {len(self.all_results)} 条")
        print(f"去重后: {len(unique_results)} 条")
        
        if not unique_results:
            print("没有识别到敏感数据")
            return
        
        # 打印统计信息
        self.exporter.print_statistics(unique_results)
        
        # 导出CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"result_{timestamp}.csv"
        
        self.exporter.export_to_csv(unique_results, output_filename)
        
        print(f"\n结果已导出到: {os.path.join(self.output_dir, output_filename)}")
        
        # 保存去重后的结果用于可视化
        self.all_results = unique_results
    
    def _generate_visualization(self):
        """生成可视化报告"""
        if not self.all_results:
            print("没有数据可可视化")
            return
        
        try:
            # 生成图表
            self.visualizer.visualize_all(self.all_results)
            
            # 生成HTML报告
            html_path = self.visualizer.generate_html_report(self.all_results, self.metrics)
            
            print(f"\n可视化报告已生成,请在浏览器中打开:")
            print(f"  {html_path}")
            
        except Exception as e:
            print(f"[警告] 可视化生成失败: {e}")
        
    def _deduplicate_results(self) -> List[Dict[str, any]]:
        """去重结果
        
        Returns:
            去重后的结果列表
        """
        seen = set()
        unique_results = []
        
        for result in self.all_results:
            # 创建唯一键
            key = (
                result.get('data_type'),
                result.get('content'),
                result.get('source_ip'),
                result.get('dest_ip')
            )
            
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return unique_results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='敏感数据识别与分类系统 (GPU+CPU混合版)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
性能说明:
  GPU加速OCR - 利用GPU加速图片文字识别
  AI增强分类 - 使用LM Studio的Qwen模型提高准确率
  CPU单线程 - 避免多线程开销,吃满单核心

配置文件:
  config.yaml - 配置GPU、AI、输出等参数

使用示例:
  python main.py test_sample.pcap              # 使用默认配置
  python main.py test_sample.pcap --config custom.yaml  # 使用自定义配置
        """
    )
    parser.add_argument('pcap_file', help='PCAP文件路径')
    parser.add_argument('--output', '-o', default='./output', help='输出目录 (默认: ./output)')
    parser.add_argument('--max-packets', '-m', type=int, default=None,
                       help='最大解析包数 (默认: 全部)')
    parser.add_argument('--config', '-c', default='config.yaml', help='配置文件路径 (默认: config.yaml)')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.pcap_file):
        print(f"错误: PCAP文件不存在: {args.pcap_file}")
        sys.exit(1)
    
    # 显示文件信息
    file_size = os.path.getsize(args.pcap_file)
    file_size_mb = file_size / (1024 * 1024)
    file_size_gb = file_size_mb / 1024
    print(f"文件大小: {file_size_gb:.2f} GB ({file_size_mb:.2f} MB, {file_size} 字节)")
    print(f"配置文件: {args.config}")
    
    # 创建系统实例
    system = SensitiveDataDetectionSystem(
        pcap_file=args.pcap_file,
        output_dir=args.output,
        max_packets=args.max_packets,
        config_file=args.config
    )
    
    # 初始化
    system.initialize()
    
    # 处理
    start_time = time.time()
    success = system.process()
    elapsed_time = time.time() - start_time
    
    if success:
        print(f"\n✓ 处理完成! 总耗时: {elapsed_time:.2f} 秒")
        print(f"\n请将生成的CSV文件上传到验证靶机: https://gdufs2025.dasctf.com/")
        print(f"可视化报告: {os.path.join(args.output, 'report.html')}")
    else:
        print(f"\n✗ 处理失败!")
        sys.exit(1)


if __name__ == '__main__':
    main()
