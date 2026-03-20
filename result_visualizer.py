"""
数据可视化模块
用于展示敏感数据识别结果
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
from typing import List, Dict
import pandas as pd
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class ResultVisualizer:
    """结果可视化器"""
    
    def __init__(self, output_dir: str = "./output"):
        """初始化可视化器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def visualize_all(self, results: List[Dict]):
        """生成所有可视化图表
        
        Args:
            results: 识别结果列表
        """
        if not results:
            print("[可视化] 没有数据可可视化")
            return
        
        print(f"[可视化] 开始生成图表...")
        
        # 生成各类图表
        self.plot_type_distribution(results)
        self.plot_confidence_distribution(results)
        self.plot_source_dest_stats(results)
        self.plot_top_sensitive_data(results)
        
        print(f"[可视化] 图表生成完成,保存在: {self.output_dir}")
    
    def plot_type_distribution(self, results: List[Dict]):
        """绘制敏感数据类型分布饼图
        
        Args:
            results: 识别结果列表
        """
        df = pd.DataFrame(results)
        type_counts = df['data_type'].value_counts()
        
        plt.figure(figsize=(10, 8))
        colors = plt.cm.Set3(range(len(type_counts)))
        
        wedges, texts, autotexts = plt.pie(
            type_counts.values,
            labels=type_counts.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        # 设置文本样式
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        plt.title('敏感数据类型分布', fontsize=14, fontweight='bold', pad=20)
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'type_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_confidence_distribution(self, results: List[Dict]):
        """绘制置信度分布直方图
        
        Args:
            results: 识别结果列表
        """
        df = pd.DataFrame(results)
        confidences = df['confidence'] * 100
        
        plt.figure(figsize=(12, 6))
        
        # 创建直方图
        n, bins, patches = plt.hist(confidences, bins=20, edgecolor='black', alpha=0.7, color='steelblue')
        
        # 添加均值线
        mean_conf = confidences.mean()
        plt.axvline(mean_conf, color='red', linestyle='--', linewidth=2, 
                   label=f'平均置信度: {mean_conf:.1f}%')
        
        plt.xlabel('置信度 (%)', fontsize=12)
        plt.ylabel('数据量', fontsize=12)
        plt.title('识别置信度分布', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'confidence_distribution.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_source_dest_stats(self, results: List[Dict]):
        """绘制源IP和目标IP统计
        
        Args:
            results: 识别结果列表
        """
        df = pd.DataFrame(results)
        
        # 统计源IP和目标IP
        source_ips = df['source_ip'].value_counts().head(10)
        dest_ips = df['dest_ip'].value_counts().head(10)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # 源IP柱状图
        source_ips.plot(kind='bar', ax=ax1, color='coral', edgecolor='black')
        ax1.set_title('Top 10 源IP', fontsize=12, fontweight='bold')
        ax1.set_xlabel('IP地址', fontsize=10)
        ax1.set_ylabel('出现次数', fontsize=10)
        ax1.tick_params(axis='x', rotation=45, labelsize=8)
        
        # 目标IP柱状图
        dest_ips.plot(kind='bar', ax=ax2, color='skyblue', edgecolor='black')
        ax2.set_title('Top 10 目标IP', fontsize=12, fontweight='bold')
        ax2.set_xlabel('IP地址', fontsize=10)
        ax2.set_ylabel('出现次数', fontsize=10)
        ax2.tick_params(axis='x', rotation=45, labelsize=8)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'ip_statistics.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_top_sensitive_data(self, results: List[Dict]):
        """绘制各类敏感数据的Top内容
        
        Args:
            results: 识别结果列表
        """
        df = pd.DataFrame(results)
        types = df['data_type'].unique()
        
        n_types = len(types)
        if n_types == 0:
            return
        
        # 计算子图行列数
        n_cols = min(3, n_types)
        n_rows = (n_types + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        if n_rows == 1 and n_cols == 1:
            axes = [axes]
        elif n_rows == 1:
            axes = axes.reshape(1, -1)
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                 '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE']
        
        for idx, data_type in enumerate(sorted(types)):
            row = idx // n_cols
            col = idx % n_cols
            ax = axes[row, col] if n_rows > 1 else axes[col]
            
            # 获取该类型的数据
            type_data = df[df['data_type'] == data_type]['content'].value_counts().head(10)
            
            if len(type_data) > 0:
                # 部分隐藏敏感内容(只显示前4位和后4位)
                labels = type_data.index.tolist()
                masked_labels = []
                for label in labels:
                    if len(label) > 8:
                        masked = label[:4] + '*' * (len(label) - 8) + label[-4:]
                    else:
                        masked = '*' * len(label)
                    masked_labels.append(masked)
                
                type_data.plot(kind='bar', ax=ax, color=colors[idx % len(colors)], edgecolor='black')
                ax.set_title(f'{data_type} (Top 10)', fontsize=10, fontweight='bold')
                ax.set_xlabel('敏感内容(已脱敏)', fontsize=8)
                ax.set_ylabel('出现次数', fontsize=8)
                ax.set_xticklabels(masked_labels, rotation=45, ha='right', fontsize=7)
            else:
                ax.text(0.5, 0.5, '无数据', ha='center', va='center', fontsize=12)
                ax.set_title(f'{data_type}', fontsize=10, fontweight='bold')
        
        # 隐藏多余的子图
        for idx in range(n_types, n_rows * n_cols):
            row = idx // n_cols
            col = idx % n_cols
            if n_rows > 1:
                fig.delaxes(axes[row, col])
            else:
                fig.delaxes(axes[col])
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'top_sensitive_data.png'), dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_html_report(self, results: List[Dict], metrics: Dict):
        """生成HTML可视化报告
        
        Args:
            results: 识别结果列表
            metrics: 性能指标字典
        """
        df = pd.DataFrame(results)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>敏感数据识别报告</title>
            <style>
                body {{
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    text-align: center;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    border-left: 4px solid #3498db;
                    padding-left: 10px;
                    margin-top: 30px;
                }}
                .metrics {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .metric-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                }}
                .metric-value {{
                    font-size: 2em;
                    font-weight: bold;
                }}
                .metric-label {{
                    font-size: 0.9em;
                    opacity: 0.9;
                }}
                .chart-container {{
                    margin: 20px 0;
                    text-align: center;
                }}
                .chart-container img {{
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>敏感数据识别与分析报告</h1>
                
                <h2>性能指标</h2>
                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-value">{len(results)}</div>
                        <div class="metric-label">识别总数</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('elapsed_time', 0):.1f}s</div>
                        <div class="metric-label">运行时间</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('cpu_usage', 0):.1f}%</div>
                        <div class="metric-label">CPU占用</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.get('memory_usage', 0):.1f}%</div>
                        <div class="metric-label">内存占用</div>
                    </div>
                </div>
                
                <h2>可视化图表</h2>
                <div class="chart-container">
                    <h3>敏感数据类型分布</h3>
                    <img src="type_distribution.png" alt="类型分布">
                </div>
                <div class="chart-container">
                    <h3>置信度分布</h3>
                    <img src="confidence_distribution.png" alt="置信度分布">
                </div>
                <div class="chart-container">
                    <h3>IP地址统计</h3>
                    <img src="ip_statistics.png" alt="IP统计">
                </div>
                <div class="chart-container">
                    <h3>Top 敏感数据</h3>
                    <img src="top_sensitive_data.png" alt="Top敏感数据">
                </div>
                
                <h2>识别结果预览 (前20条)</h2>
                <table>
                    <tr>
                        <th>数据类型</th>
                        <th>敏感内容</th>
                        <th>置信度</th>
                        <th>源IP</th>
                        <th>目标IP</th>
                        <th>时间戳</th>
                    </tr>
        """
        
        # 添加前20条结果
        for _, row in df.head(20).iterrows():
            html_content += f"""
                    <tr>
                        <td>{row['data_type']}</td>
                        <td>{row['content'][:30]}{'...' if len(row['content']) > 30 else ''}</td>
                        <td>{row['confidence']:.2%}</td>
                        <td>{row['source_ip']}</td>
                        <td>{row['dest_ip']}</td>
                        <td>{row['timestamp']}</td>
                    </tr>
            """
        
        html_content += """
                </table>
                
                <p style="text-align: center; color: #7f8c8d; margin-top: 50px;">
                    生成时间: """ + str(pd.Timestamp.now()) + """
                </p>
            </div>
        </body>
        </html>
        """
        
        # 保存HTML报告
        html_path = os.path.join(self.output_dir, 'report.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[可视化] HTML报告已生成: {html_path}")
        return html_path
