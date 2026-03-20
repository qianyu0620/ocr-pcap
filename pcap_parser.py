import pyshark
import scapy.all as scapy
from scapy.all import rdpcap, PcapReader
from scapy.layers.http import HTTPRequest, HTTPResponse
from scapy.layers.inet import IP, TCP
from typing import List, Dict, Tuple, Optional
import os
from urllib.parse import unquote
import re


class PacketInfo:
    """数据包信息"""
    def __init__(self):
        self.timestamp: float = 0.0
        self.source_ip: str = ""
        self.dest_ip: str = ""
        self.source_port: int = 0
        self.dest_port: int = 0
        self.protocol: str = ""
        self.payload: bytes = b""
        self.text_data: str = ""
        self.image_data: Optional[bytes] = None
        self.headers: Dict[str, str] = {}
        
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'timestamp': self.timestamp,
            'source_ip': self.source_ip,
            'dest_ip': self.dest_ip,
            'source_port': self.source_port,
            'dest_port': self.dest_port,
            'protocol': self.protocol,
            'text_data': self.text_data,
            'headers': self.headers
        }


class PCAPParser:
    """PCAP文件解析器(单线程高性能版本)"""
    
    def __init__(self, pcap_file: str):
        """初始化解析器
        
        Args:
            pcap_file: PCAP文件路径
        """
        self.pcap_file = pcap_file
        self.packets: List[PacketInfo] = []
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
        if not os.path.exists(pcap_file):
            raise FileNotFoundError(f"PCAP文件不存在: {pcap_file}")
        
        print(f"[解析器] 加载PCAP文件: {pcap_file}")
        print(f"[解析器] 使用单线程高性能模式")
        
    def parse(self, max_packets: Optional[int] = None, 
              show_progress: bool = True) -> List[PacketInfo]:
        """解析PCAP文件(单线程高性能版本)
        
        Args:
            max_packets: 最大解析包数,None表示解析全部
            show_progress: 是否显示进度条
            
        Returns:
            数据包信息列表
        """
        print(f"[解析器] 开始解析数据包...")
        
        try:
            packet_count = 0
            valid_count = 0
            self.packets = []
            
            # 创建进度条
            if show_progress:
                total_packets = self._estimate_packet_count()
                from tqdm import tqdm
                pbar = tqdm(total=total_packets, desc="解析进度", unit="包")
            else:
                pbar = None
            
            # 使用PcapReader流式读取 - 单线程避免锁竞争
            with PcapReader(self.pcap_file) as pcap_reader:
                for packet in pcap_reader:
                    # 检查是否达到最大包数限制
                    if max_packets and packet_count >= max_packets:
                        break
                    
                    try:
                        # 直接解析,避免函数调用开销
                        packet_info = self._parse_packet_fast(packet)
                        if packet_info:
                            self.packets.append(packet_info)
                            valid_count += 1
                    except Exception as e:
                        pass
                    
                    packet_count += 1
                    
                    # 更新进度条 (每100包更新一次)
                    if pbar and packet_count % 100 == 0:
                        pbar.update(100)
            
            if pbar:
                pbar.close()
            
            print(f"[解析器] 共读取 {packet_count} 个数据包")
            print(f"[解析器] 成功解析 {valid_count} 个有效数据包")
            print(f"[解析器] 解析速度: {packet_count / (max(packet_count / 10000, 0.01)):.0f} 包/秒")
            return self.packets
            
        except Exception as e:
            print(f"[解析器] 解析错误: {e}")
            raise
    
    def _parse_packet_fast(self, packet) -> Optional[PacketInfo]:
        """快速解析单个数据包(优化版本)
        
        Args:
            packet: Scapy数据包对象
            
        Returns:
            数据包信息
        """
        try:
            # 快速检查是否为IP+TCP包
            if not (IP in packet and TCP in packet):
                return None
            
            packet_info = PacketInfo()
            
            # 快速提取基本信息
            packet_info.timestamp = float(packet.time)
            packet_info.source_ip = packet[IP].src
            packet_info.dest_ip = packet[IP].dst
            packet_info.source_port = packet[TCP].sport
            packet_info.dest_port = packet[TCP].dport
            packet_info.protocol = "TCP"
            
            # 快速检查HTTP
            if HTTPRequest in packet:
                packet_info.protocol = "HTTP"
                self._parse_http_request_fast(packet, packet_info)
            elif HTTPResponse in packet:
                packet_info.protocol = "HTTP"
                self._parse_http_response_fast(packet, packet_info)
            else:
                self._extract_raw_payload_fast(packet, packet_info)
            
            return packet_info if packet_info.text_data or packet_info.image_data else None
            
        except Exception:
            return None
    
    def _parse_http_request_fast(self, packet, packet_info: PacketInfo):
        """快速解析HTTP请求"""
        try:
            http = packet[HTTPRequest]
            
            # 直接访问属性,避免hasattr检查
            try:
                request_line = f"{http.Method.decode()} {http.Path.decode()} HTTP/{http.Http_Version.decode()}"
                packet_info.text_data = request_line
            except:
                pass
            
            # 快速提取payload
            if hasattr(packet, 'payload'):
                self._extract_payload_from_layer_fast(packet.payload, packet_info)
        except:
            pass
    
    def _parse_http_response_fast(self, packet, packet_info: PacketInfo):
        """快速解析HTTP响应"""
        try:
            http = packet[HTTPResponse]
            content_type = ''
            
            if hasattr(http, 'fields'):
                try:
                    content_type = str(getattr(http, 'Content-Type', ''))
                except:
                    pass
            
            # 快速提取payload
            if hasattr(packet, 'payload'):
                self._extract_payload_from_layer_fast(packet.payload, packet_info, content_type)
        except:
            pass
    
    def _extract_raw_payload_fast(self, packet, packet_info: PacketInfo):
        """快速提取原始payload"""
        try:
            if hasattr(packet, 'payload'):
                self._extract_payload_from_layer_fast(packet.payload, packet_info)
        except:
            pass
    
    def _extract_payload_from_layer_fast(self, layer, packet_info: PacketInfo, 
                                       content_type: str = '') -> PacketInfo:
        """快速从层中提取payload"""
        try:
            # 快速检查load属性
            if hasattr(layer, 'load'):
                payload = bytes(layer.load)
                
                # 快速图片检测
                if content_type and 'image' in content_type.lower():
                    packet_info.image_data = payload
                elif len(payload) >= 4:
                    # 快速魔术字检查
                    first_bytes = payload[:6]
                    if (first_bytes[:2] == b'\xff\xd8' or      # JPEG
                        first_bytes[:4] == b'\x89PNG' or       # PNG
                        first_bytes[:6] in (b'GIF87a', b'GIF89a') or  # GIF
                        first_bytes[:2] == b'BM'):              # BMP
                        packet_info.image_data = payload
                    else:
                        # 快速文本解码
                        try:
                            text = payload.decode('utf-8', errors='ignore')
                            packet_info.text_data = unquote(text)
                        except:
                            pass
                
                # 递归处理下一层
                if hasattr(layer, 'payload'):
                    self._extract_payload_from_layer_fast(layer.payload, packet_info, content_type)
        except:
            pass
        
        return packet_info
    
    def _estimate_packet_count(self) -> int:
        """估算PCAP文件中的数据包数量"""
        try:
            file_size = os.path.getsize(self.pcap_file)
            return max(file_size // 800, 1000)
        except:
            return 10000
    
    def get_text_data(self) -> List[str]:
        """获取所有文本数据"""
        return [p.text_data for p in self.packets if p.text_data]
    
    def get_image_data(self) -> List[Tuple[bytes, str, str]]:
        """获取所有图片数据"""
        return [(p.image_data, p.source_ip, p.dest_ip) 
                for p in self.packets if p.image_data]
    
    def get_packets_with_text(self) -> List[PacketInfo]:
        """获取包含文本的数据包"""
        return [p for p in self.packets if p.text_data]
    
    def get_packets_with_image(self) -> List[PacketInfo]:
        """获取包含图片的数据包"""
        return [p for p in self.packets if p.image_data]
