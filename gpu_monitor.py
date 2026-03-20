"""
GPU性能监控模块
"""

import pynvml
import time
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class GPUMetrics:
    """GPU性能指标"""
    gpu_utilization: float = 0.0    # GPU利用率(%)
    memory_used: float = 0.0        # 已用显存(MB)
    memory_total: float = 0.0       # 总显存(MB)
    memory_percent: float = 0.0    # 显存占用率(%)
    temperature: float = 0.0        # 温度(°C)
    power_usage: float = 0.0        # 功耗(W)
    fan_speed: float = 0.0          # 风扇转速(%)


class GPUMonitor:
    """GPU性能监控器"""
    
    def __init__(self):
        """初始化GPU监控器"""
        self.available = False
        self.handle = None
        self._initialize()
        
    def _initialize(self):
        """初始化NVML"""
        try:
            pynvml.nvmlInit()
            self.handle = pynvml.nvmlDeviceGetHandle(0)
            self.available = True
            print(f"[GPU监控] 初始化成功")
        except Exception as e:
            print(f"[GPU监控] 初始化失败: {e}")
            self.available = False
    
    def get_metrics(self) -> Optional[GPUMetrics]:
        """获取当前GPU性能指标
        
        Returns:
            GPU性能指标
        """
        if not self.available:
            return None
        
        try:
            # GPU利用率
            utilization = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
            gpu_util = utilization.gpu
            
            # 显存信息
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            mem_used_mb = mem_info.used // (1024**2)
            mem_total_mb = mem_info.total // (1024**2)
            mem_percent = (mem_used_mb / mem_total_mb) * 100
            
            # 温度
            try:
                temp = pynvml.nvmlDeviceGetTemperature(self.handle, 
                                                     pynvml.NVML_TEMPERATURE_GPU)
            except:
                temp = 0.0
            
            # 功耗
            try:
                power = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000.0  # 转换为W
            except:
                power = 0.0
            
            # 风扇转速
            try:
                fan = pynvml.nvmlDeviceGetFanSpeed(self.handle)
            except:
                fan = 0.0
            
            return GPUMetrics(
                gpu_utilization=gpu_util,
                memory_used=mem_used_mb,
                memory_total=mem_total_mb,
                memory_percent=mem_percent,
                temperature=temp,
                power_usage=power,
                fan_speed=fan
            )
            
        except Exception as e:
            return None
    
    def print_metrics(self, metrics: GPUMetrics):
        """打印GPU性能指标
        
        Args:
            metrics: GPU性能指标
        """
        print("\n" + "="*50)
        print("GPU性能监控")
        print("="*50)
        print(f"GPU利用率: {metrics.gpu_utilization}%")
        print(f"显存占用:  {metrics.memory_used:.0f} MB / {metrics.memory_total:.0f} MB ({metrics.memory_percent:.1f}%)")
        if metrics.temperature > 0:
            print(f"GPU温度:   {metrics.temperature:.0f}°C")
        if metrics.power_usage > 0:
            print(f"功耗:       {metrics.power_usage:.1f} W")
        if metrics.fan_speed > 0:
            print(f"风扇转速:   {metrics.fan_speed}%")
        print("="*50)
    
    def get_device_info(self) -> Optional[Dict]:
        """获取GPU设备信息
        
        Returns:
            设备信息字典
        """
        if not self.available:
            return None
        
        try:
            name = pynvml.nvmlDeviceGetName(self.handle).decode('utf-8')
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            
            return {
                'name': name,
                'memory_gb': mem_info.total // (1024**3),
                'available': True
            }
        except:
            return None
    
    def shutdown(self):
        """关闭监控器"""
        if self.available:
            try:
                pynvml.nvmlShutdown()
            except:
                pass


# 测试代码
if __name__ == '__main__':
    monitor = GPUMonitor()
    
    if monitor.available:
        info = monitor.get_device_info()
        print(f"GPU设备: {info}")
        
        metrics = monitor.get_metrics()
        if metrics:
            monitor.print_metrics(metrics)
        
        monitor.shutdown()
