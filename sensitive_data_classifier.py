import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class SensitiveDataType(Enum):
    """敏感数据类型枚举"""
    ID_CARD = "身份证号"
    BANK_CARD = "银行卡号"
    PHONE = "手机号码"
    EMAIL = "邮箱地址"
    PASSPORT = "护照号码"
    DRIVING_LICENSE = "驾驶证号"
    SOCIAL_CREDIT = "统一社会信用代码"
    IP_ADDRESS = "IP地址"
    URL = "URL"
    OTHER = "其他敏感信息"


@dataclass
class SensitiveDataResult:
    """敏感数据识别结果"""
    data_type: str
    content: str
    confidence: float
    source_ip: str = ""
    dest_ip: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'data_type': self.data_type,
            'content': self.content,
            'confidence': self.confidence,
            'source_ip': self.source_ip,
            'dest_ip': self.dest_ip,
            'timestamp': self.timestamp
        }


class SensitiveDataClassifier:
    """敏感数据分类器(单线程高性能版本)"""
    
    def __init__(self):
        """初始化分类器"""
        self.patterns = self._init_patterns()
        print(f"[分类器] 已初始化 {len(self.patterns)} 种敏感数据识别规则")
        print(f"[分类器] 使用单线程高性能模式")
        
    def _init_patterns(self) -> Dict[SensitiveDataType, Tuple[str, str]]:
        """初始化正则表达式模式"""
        patterns = {
            SensitiveDataType.ID_CARD: (
                r'\b[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]\b',
                '18位身份证号'
            ),
            SensitiveDataType.BANK_CARD: (
                r'\b(?:\d[ -]*?){13,19}\b',
                '13-19位银行卡号'
            ),
            SensitiveDataType.PHONE: (
                r'\b(1[3-9]\d{9})\b',
                '11位手机号码'
            ),
            SensitiveDataType.EMAIL: (
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                '邮箱地址'
            ),
            SensitiveDataType.PASSPORT: (
                r'\b[EPG][0-9]{8}\b',
                '护照号码'
            ),
            SensitiveDataType.DRIVING_LICENSE: (
                r'\b[0-9A-Za-z]{12}\b',
                '驾驶证号'
            ),
            SensitiveDataType.SOCIAL_CREDIT: (
                r'\b[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}\b',
                '统一社会信用代码'
            ),
            SensitiveDataType.IP_ADDRESS: (
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                'IPv4地址'
            ),
            SensitiveDataType.URL: (
                r'https?://[^\s<>"]+|www\.[^\s<>"]+',
                'URL地址'
            )
        }
        return patterns
    
    def classify(self, text: str, source_ip: str = "", dest_ip: str = "", timestamp: str = "") -> List[SensitiveDataResult]:
        """分类文本中的敏感数据(快速版本)"""
        results = []
        
        # 遍历所有模式
        for data_type, (pattern, desc) in self.patterns.items():
            try:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    content = match.group().strip()
                    
                    # 银行卡号处理
                    if data_type == SensitiveDataType.BANK_CARD:
                        content = re.sub(r'[ -]', '', content)
                    
                    # 计算置信度
                    confidence = self._calculate_confidence_fast(data_type, content)
                    
                    results.append(SensitiveDataResult(
                        data_type=data_type.value,
                        content=content,
                        confidence=confidence,
                        source_ip=source_ip,
                        dest_ip=dest_ip,
                        timestamp=timestamp
                    ))
            except Exception:
                continue
        
        return results
    
    def classify_batch(self, text_data_list: List[Dict], 
                      show_progress: bool = True) -> List[dict]:
        """批量分类文本(单线程高性能版本)
        
        Args:
            text_data_list: 文本数据列表
            show_progress: 是否显示进度条
            
        Returns:
            识别结果列表
        """
        all_results = []
        total = len(text_data_list)
        
        from tqdm import tqdm
        
        if show_progress:
            pbar = tqdm(total=total, desc="数据分类", unit="条")
        else:
            pbar = None
        
        # 单线程处理,避免锁竞争
        for idx, data in enumerate(text_data_list):
            try:
                results = self.classify(
                    text=data['text_data'],
                    source_ip=data.get('source_ip', ''),
                    dest_ip=data.get('dest_ip', ''),
                    timestamp=data.get('timestamp', '')
                )
                all_results.extend([r.to_dict() for r in results])
            except Exception:
                pass
            
            # 更新进度
            if pbar and idx % 100 == 0:
                pbar.update(100)
                pbar.set_postfix({'完成': idx, '结果': len(all_results)})
        
        if pbar:
            pbar.close()
        
        return all_results
    
    def _calculate_confidence_fast(self, data_type: SensitiveDataType, content: str) -> float:
        """快速计算识别置信度"""
        try:
            base_confidence = 0.95
            
            # 快速置信度计算
            if data_type == SensitiveDataType.ID_CARD:
                # 身份证号校验
                if len(content) == 18 and self._validate_id_card_fast(content):
                    base_confidence = 0.99
                else:
                    base_confidence = 0.85
                    
            elif data_type == SensitiveDataType.PHONE:
                # 手机号校验
                if content.startswith(('13', '14', '15', '16', '17', '18', '19')):
                    base_confidence = 0.99
                else:
                    base_confidence = 0.80
                    
            elif data_type == SensitiveDataType.EMAIL:
                # 邮箱校验
                if '@' in content and '.' in content.split('@')[1]:
                    base_confidence = 0.98
            
            return base_confidence
        except:
            return 0.95
    
    def _validate_id_card_fast(self, id_card: str) -> bool:
        """快速验证身份证号校验位"""
        try:
            if len(id_card) != 18:
                return False
            
            # 权重因子
            weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
            # 校验码对应值
            check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
            
            total = 0
            for i in range(17):
                total += int(id_card[i]) * weights[i]
            
            return id_card[-1].upper() == check_codes[total % 11]
        except:
            return False
    
    def deduplicate_results(self, results: List[SensitiveDataResult]) -> List[SensitiveDataResult]:
        """去重识别结果"""
        seen = set()
        deduplicated = []
        
        for result in results:
            key = (result.data_type, result.content, result.source_ip, result.dest_ip)
            if key not in seen:
                seen.add(key)
                deduplicated.append(result)
        
        return deduplicated
