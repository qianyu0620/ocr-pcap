import pandas as pd
from typing import List, Dict, Optional
import os
from datetime import datetime


class CSVExporter:
    """CSV文件导出器"""
    
    def __init__(self, output_dir: str = "./output"):
        """初始化导出器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
        
    def _ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"[导出器] 创建输出目录: {self.output_dir}")
    
    def export_to_csv(self, results: List[Dict], output_filename: str = "result.csv") -> str:
        """导出结果到CSV文件
        
        Args:
            results: 结果数据列表
            output_filename: 输出文件名
            
        Returns:
            输出文件路径
        """
        if not results:
            print(f"[导出器] 警告: 没有数据可导出")
            return ""
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # 创建DataFrame
            df = pd.DataFrame(results)
            
            # 确保列顺序
            required_columns = ['data_type', 'content', 'confidence', 'source_ip', 'dest_ip', 'timestamp']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # 按照指定列顺序重新排列
            df = df[required_columns]
            
            # 导出CSV
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"[导出器] 成功导出 {len(results)} 条记录到: {output_path}")
            print(f"[导出器] 文件列: {', '.join(df.columns.tolist())}")
            
            return output_path
            
        except Exception as e:
            print(f"[导出器] 导出失败: {e}")
            raise
    
    def export_with_format(self, results: List[Dict], output_filename: str = "result.csv") -> str:
        """按照比赛要求的格式导出CSV文件
        
        Args:
            results: 结果数据列表
            output_filename: 输出文件名
            
        Returns:
            输出文件路径
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # 准备数据
            export_data = []
            for result in results:
                export_data.append({
                    '数据类型': result.get('data_type', ''),
                    '敏感内容': result.get('content', ''),
                    '源IP': result.get('source_ip', ''),
                    '目标IP': result.get('dest_ip', ''),
                    '时间戳': result.get('timestamp', ''),
                    '置信度': result.get('confidence', 0.0)
                })
            
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 导出CSV
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"[导出器] 成功导出 {len(export_data)} 条记录到: {output_path}")
            print(f"[导出器] 文件列: {', '.join(df.columns.tolist())}")
            
            return output_path
            
        except Exception as e:
            print(f"[导出器] 导出失败: {e}")
            raise
    
    def append_to_csv(self, new_data: List[Dict], output_filename: str = "result.csv"):
        """追加数据到已有CSV文件
        
        Args:
            new_data: 新数据列表
            output_filename: 输出文件名
        """
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # 如果文件存在,读取并追加
            if os.path.exists(output_path):
                df = pd.read_csv(output_path, encoding='utf-8-sig')
                new_df = pd.DataFrame(new_data)
                df = pd.concat([df, new_df], ignore_index=True)
            else:
                df = pd.DataFrame(new_data)
            
            # 导出CSV
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"[导出器] 成功追加 {len(new_data)} 条记录到: {output_path}")
            
        except Exception as e:
            print(f"[导出器] 追加失败: {e}")
            raise
    
    def get_statistics(self, results: List[Dict]) -> Dict:
        """获取统计信息
        
        Args:
            results: 结果数据列表
            
        Returns:
            统计信息字典
        """
        stats = {
            'total_count': len(results),
            'by_type': {},
            'avg_confidence': 0.0
        }
        
        if not results:
            return stats
        
        # 按类型统计
        type_counts = {}
        total_confidence = 0.0
        
        for result in results:
            data_type = result.get('data_type', '未知')
            type_counts[data_type] = type_counts.get(data_type, 0) + 1
            total_confidence += result.get('confidence', 0.0)
        
        stats['by_type'] = type_counts
        stats['avg_confidence'] = total_confidence / len(results)
        
        return stats
    
    def print_statistics(self, results: List[Dict]):
        """打印统计信息
        
        Args:
            results: 结果数据列表
        """
        stats = self.get_statistics(results)
        
        print("\n" + "="*50)
        print("识别结果统计")
        print("="*50)
        print(f"总识别数量: {stats['total_count']}")
        print(f"平均置信度: {stats['avg_confidence']:.2%}")
        print("\n按类型分布:")
        for data_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {data_type}: {count}")
        print("="*50)
