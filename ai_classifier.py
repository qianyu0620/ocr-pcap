import requests
from typing import List, Dict, Optional
import json
from dataclasses import dataclass


@dataclass
class AIClassificationResult:
    """AI分类结果"""
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


class AIClassifier:
    """基于本地LM Studio的AI分类器"""
    
    def __init__(self, api_url: str = "http://localhost:1234/v1/chat/completions",
                 model_name: str = "qwen2.5", enable: bool = True):
        """初始化AI分类器
        
        Args:
            api_url: LM Studio API地址
            model_name: 模型名称
            enable: 是否启用AI分类
        """
        self.api_url = api_url
        self.model_name = model_name
        self.enable = enable
        
        if self.enable:
            print(f"[AI分类器] 启用LM Studio API")
            print(f"[AI分类器] API地址: {api_url}")
            print(f"[AI分类器] 模型: {model_name}")
            # 测试连接
            self._test_connection()
        else:
            print(f"[AI分类器] 已禁用")
    
    def _test_connection(self):
        """测试API连接"""
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": "测试"}],
                    "max_tokens": 10
                },
                timeout=5
            )
            if response.status_code == 200:
                print(f"[AI分类器] API连接成功")
                return True
            else:
                print(f"[AI分类器] API连接失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[AI分类器] API连接异常: {e}")
            print(f"[AI分类器] 请确保LM Studio已启动并运行在 {self.api_url}")
            return False
    
    def classify_with_ai(self, text: str, source_ip: str = "", 
                      dest_ip: str = "", timestamp: str = "") -> Optional[AIClassificationResult]:
        """使用AI分类文本
        
        Args:
            text: 待分类文本
            source_ip: 源IP
            dest_ip: 目标IP
            timestamp: 时间戳
            
        Returns:
            AI分类结果
        """
        if not self.enable:
            return None
        
        if not text or len(text.strip()) < 5:
            return None
        
        try:
            # 构建提示词
            prompt = f"""请分析以下文本,判断是否包含敏感信息。

文本内容: {text[:500]}

敏感信息类型包括:
1. 身份证号 (18位数字)
2. 银行卡号 (13-19位数字)
3. 手机号码 (11位1开头)
4. 邮箱地址
5. URL地址
6. IP地址

请以JSON格式返回分析结果,格式如下:
{{
    "is_sensitive": true/false,
    "data_type": "敏感数据类型",
    "content": "敏感内容",
    "confidence": 0.0-1.0
}}

如果文本不包含敏感信息,is_sensitive设为false。"""
            
            # 调用API
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200,
                    "temperature": 0.1,  # 低温度确保确定性
                    "timeout": 30
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return None
            
            # 解析响应
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 提取JSON
            try:
                # 查找JSON部分
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    ai_result = json.loads(json_str)
                    
                    if ai_result.get('is_sensitive', False):
                        return AIClassificationResult(
                            data_type=ai_result.get('data_type', 'AI识别'),
                            content=ai_result.get('content', text[:100]),
                            confidence=ai_result.get('confidence', 0.8),
                            source_ip=source_ip,
                            dest_ip=dest_ip,
                            timestamp=timestamp
                        )
            except Exception as e:
                pass
            
            return None
            
        except Exception as e:
            return None
    
    def classify_batch_with_ai(self, text_data_list: List[Dict], 
                               show_progress: bool = True) -> List[Dict]:
        """批量AI分类
        
        Args:
            text_data_list: 文本数据列表
            show_progress: 是否显示进度条
            
        Returns:
            AI分类结果列表
        """
        if not self.enable:
            return []
        
        results = []
        total = len(text_data_list)
        
        from tqdm import tqdm
        
        if show_progress:
            pbar = tqdm(total=total, desc="AI分类", unit="条")
        else:
            pbar = None
        
        # 只对较长的文本使用AI分类(提高效率)
        for idx, data in enumerate(text_data_list):
            try:
                text = data.get('text_data', '')
                
                # 只处理长度合适的文本
                if 10 <= len(text) <= 500:
                    ai_result = self.classify_with_ai(
                        text=text,
                        source_ip=data.get('source_ip', ''),
                        dest_ip=data.get('dest_ip', ''),
                        timestamp=data.get('timestamp', '')
                    )
                    
                    if ai_result:
                        results.append(ai_result.to_dict())
            except Exception:
                pass
            
            # 更新进度
            if pbar and idx % 10 == 0:
                pbar.update(10)
                pbar.set_postfix({'完成': idx, '识别': len(results)})
        
        if pbar:
            pbar.close()
        
        return results
