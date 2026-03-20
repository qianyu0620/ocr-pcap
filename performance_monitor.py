import psutil
import time
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    elapsed_time: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'elapsed_time': self.elapsed_time,
            'start_time': self.start_time,
            'end_time': self.end_time
        }


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = PerformanceMetrics()
        self._cpu_samples: List[float] = []
        self._memory_samples: List[float] = []
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
    def start(self):
        """开始监控"""
        self.metrics.start_time = time.time()
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print(f"[性能监控] 监控已启动")
        
    def stop(self) -> PerformanceMetrics:
        """停止监控并返回结果"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        
        self.metrics.end_time = time.time()
        self.metrics.elapsed_time = self.metrics.end_time - self.metrics.start_time
        
        # 计算平均值
        if self._cpu_samples:
            self.metrics.cpu_usage = sum(self._cpu_samples) / len(self._cpu_samples)
        if self._memory_samples:
            self.metrics.memory_usage = sum(self._memory_samples) / len(self._memory_samples)
        
        print(f"[性能监控] 监控已停止")
        return self.metrics
    
    def _monitor_loop(self):
        """监控循环"""
        interval = 0.5  # 采样间隔(秒)
        
        while self._monitoring:
            try:
                # CPU使用率
                cpu_percent = psutil.cpu_percent(interval=None)
                self._cpu_samples.append(cpu_percent)
                
                # 内存使用率
                memory_info = psutil.virtual_memory()
                memory_percent = memory_info.percent
                self._memory_samples.append(memory_percent)
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"[性能监控] 监控错误: {e}")
                break
    
    def get_current_metrics(self) -> Dict:
        """获取当前指标"""
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'elapsed_time': time.time() - self.metrics.start_time if self.metrics.start_time > 0 else 0
        }
    
    def print_summary(self):
        """打印性能摘要"""
        print("\n" + "="*50)
        print("性能监控报告")
        print("="*50)
        print(f"运行时间: {self.metrics.elapsed_time:.2f} 秒")
        print(f"CPU平均占用率: {self.metrics.cpu_usage:.2f}%")
        print(f"内存平均占用率: {self.metrics.memory_usage:.2f}%")
        print(f"CPU采样次数: {len(self._cpu_samples)}")
        print(f"内存采样次数: {len(self._memory_samples)}")
        print("="*50)
