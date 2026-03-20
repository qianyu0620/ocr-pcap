import cv2
import numpy as np
from paddleocr import PaddleOCR
from typing import List, Dict, Optional, Tuple
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# GPU监控(可选)
try:
    import pynvml
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


class OCRRecognizer:
    """OCR识别器(极致GPU加速版本)"""
    
    def __init__(self, use_angle_cls: bool = True, lang: str = 'ch', 
                 use_gpu: bool = True, batch_size: int = 16):
        """初始化OCR识别器
        
        Args:
            use_angle_cls: 是否使用方向分类器
            lang: 语言 (ch=中文, en=英文)
            use_gpu: 是否使用GPU
            batch_size: 批处理大小
        """
        self.use_angle_cls = use_angle_cls
        self.lang = lang
        self.ocr: Optional[PaddleOCR] = None
        self._initialized = False
        self.use_gpu = use_gpu
        self.batch_size = batch_size
        
        # 检测GPU信息
        self.gpu_info = self._detect_gpu()
        
    def _detect_gpu(self) -> Dict:
        """检测GPU信息"""
        gpu_info = {'available': False, 'name': '', 'memory': 0}
        
        if not self.use_gpu or not GPU_AVAILABLE:
            return gpu_info
        
        try:
            # 尝试直接使用nvidia-ml-py的API
            from nvidia_ml_py import nvmlDeviceGetHandle, nvmlDeviceGetName, nvmlDeviceGetMemoryInfo, nvmlInit, nvmlShutdown
            
            nvmlInit()
            handle = nvmlDeviceGetHandle(0)
            name = nvmlDeviceGetName(handle)
            info = nvmlDeviceGetMemoryInfo(handle)
            total_memory = info.total // (1024**3)  # GB
            
            gpu_info = {
                'available': True,
                'name': name.decode('utf-8') if isinstance(name, bytes) else str(name),
                'memory': total_memory
            }
            
            print(f"[GPU] 检测到NVIDIA GPU: {gpu_info['name']}")
            print(f"[GPU] 显存: {total_memory} GB")
            
            nvmlShutdown()
        except Exception as e:
            print(f"[GPU] 未检测到NVIDIA GPU: {e}")
            gpu_info['available'] = False
        
        return gpu_info
    
    def initialize(self):
        """初始化PaddleOCR模型(极致GPU优化版)"""
        try:
            print(f"[OCR] 正在初始化PaddleOCR模型...")
            
            # 检查PaddlePaddle GPU支持
            import paddle
            paddle_gpu_available = paddle.is_compiled_with_cuda()
            
            if not paddle_gpu_available and self.use_gpu:
                print(f"[警告] PaddlePaddle未编译GPU支持")
                print(f"[警告] 当前PaddlePaddle版本: {paddle.__version__}")
                print(f"[提示] 请安装: pip install paddlepaddle-gpu")
                print(f"[警告] 将使用CPU模式")
                self.use_gpu = False
                use_gpu = False
            else:
                use_gpu = self.use_gpu
            
            # GPU优化参数
            use_gpu = use_gpu and self.gpu_info['available']
            
            # 根据GPU内存动态调整批处理大小
            if use_gpu and self.gpu_info['memory'] >= 8:
                optimal_batch = min(32, self.batch_size)
                det_batch = optimal_batch
                rec_batch = optimal_batch
            elif use_gpu and self.gpu_info['memory'] >= 4:
                optimal_batch = min(16, self.batch_size)
                det_batch = optimal_batch
                rec_batch = optimal_batch
            else:
                optimal_batch = 8
                det_batch = optimal_batch
                rec_batch = optimal_batch
            
            print(f"[OCR] 批处理大小: {optimal_batch}")
            print(f"[OCR] 检测批处理: {det_batch}")
            print(f"[OCR] 识别批处理: {rec_batch}")
            
            # 极致GPU优化配置
            self.ocr = PaddleOCR(
                use_angle_cls=self.use_angle_cls,
                lang=self.lang,
                show_log=False,
                use_gpu=use_gpu,
                gpu_mem=self.gpu_info['memory'] * 1024 if use_gpu else 8000,
                
                # GPU性能优化
                det_db_batch_size=det_batch,
                rec_batch_num=rec_batch,
                
                # 极致优化参数
                enable_mkldnn=not use_gpu,  # CPU模式启用MKL-DNN
                use_tensorrt=False,         # TensorRT可能导致兼容性问题
                precision='fp32',           # 使用FP32确保稳定性
                
                # 多流并行
                max_batch_size=optimal_batch,
                drop_score=0.3,             # 降低阈值提高召回率
                
                # 优化推理
                inference_model_dir=None,
                benchmark=False,
            )
            
            self._initialized = True
            print(f"[OCR] PaddleOCR初始化成功")
            print(f"[OCR] 加速模式: {'GPU' if use_gpu else 'CPU MKL-DNN'}")
            
        except Exception as e:
            print(f"[OCR] 初始化失败: {e}")
            raise
    
    def recognize_image(self, image_path: str) -> List[Dict]:
        """识别图片中的文字
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            识别结果列表
        """
        if not self._initialized:
            self.initialize()
        
        if not os.path.exists(image_path):
            return []
        
        try:
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            result = self.ocr.ocr(img, cls=True)
            
            if not result or not result[0]:
                return []
            
            ocr_results = []
            for line in result[0]:
                try:
                    text, confidence = line[1]
                    ocr_results.append({
                        'text': text.strip(),
                        'confidence': float(confidence),
                        'box': line[0]
                    })
                except:
                    continue
            
            return ocr_results
            
        except Exception:
            return []
    
    def recognize_from_bytes(self, image_bytes: bytes) -> List[Dict]:
        """从字节数据中识别文字
        
        Args:
            image_bytes: 图片字节数据
            
        Returns:
            识别结果列表
        """
        if not self._initialized:
            self.initialize()
        
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return []
            
            result = self.ocr.ocr(img, cls=True)
            
            if not result or not result[0]:
                return []
            
            ocr_results = []
            for line in result[0]:
                try:
                    text, confidence = line[1]
                    ocr_results.append({
                        'text': text.strip(),
                        'confidence': float(confidence),
                        'box': line[0]
                    })
                except:
                    continue
            
            return ocr_results
            
        except Exception:
            return []
    
    def recognize_batch_from_bytes(self, image_data_list: List[Tuple[bytes, str, str]],
                                   show_progress: bool = True) -> List[Dict]:
        """批量识别图片字节数据(GPU多流并行版本)
        
        Args:
            image_data_list: 图片数据列表
            show_progress: 是否显示进度条
            
        Returns:
            识别结果列表
        """
        results = []
        total = len(image_data_list)
        
        if total == 0:
            return results
        
        from tqdm import tqdm
        
        if show_progress:
            pbar = tqdm(total=total, desc="OCR识别", unit="图")
        else:
            pbar = None
        
        # GPU多流并行处理
        if self.use_gpu and total > 100:
            # 大数据集使用多线程并行
            workers = min(4, os.cpu_count())
            batch_size = self.batch_size
            
            with ThreadPoolExecutor(max_workers=workers) as executor:
                # 分批处理
                futures = []
                for i in range(0, len(image_data_list), batch_size):
                    batch = image_data_list[i:i+batch_size]
                    future = executor.submit(self._process_batch, batch)
                    futures.append(future)
                
                # 收集结果
                for future in as_completed(futures):
                    try:
                        batch_results = future.result(timeout=60)
                        results.extend(batch_results)
                    except Exception:
                        pass
                    
                    if pbar:
                        pbar.update(1)
        else:
            # 小数据集单线程处理
            for idx, (image_bytes, src_ip, dest_ip) in enumerate(image_data_list):
                try:
                    ocr_results = self.recognize_from_bytes(image_bytes)
                    
                    if ocr_results:
                        all_text = ' '.join([r['text'] for r in ocr_results])
                        if all_text:
                            results.append({
                                'text_data': all_text,
                                'source_ip': src_ip,
                                'dest_ip': dest_ip,
                                'timestamp': ''
                            })
                except Exception:
                    pass
                
                if pbar and idx % 5 == 0:
                    pbar.update(5)
                    pbar.set_postfix({'完成': idx, '有效': len(results)})
        
        if pbar:
            pbar.close()
        
        return results
    
    def _process_batch(self, batch: List[Tuple[bytes, str, str]]) -> List[Dict]:
        """处理一批图片数据
        
        Args:
            batch: 图片数据列表
            
        Returns:
            识别结果列表
        """
        results = []
        
        for image_bytes, src_ip, dest_ip in batch:
            try:
                ocr_results = self.recognize_from_bytes(image_bytes)
                
                if ocr_results:
                    all_text = ' '.join([r['text'] for r in ocr_results])
                    if all_text:
                        results.append({
                            'text_data': all_text,
                            'source_ip': src_ip,
                            'dest_ip': dest_ip,
                            'timestamp': ''
                        })
            except Exception:
                pass
        
        return results
    
    def save_image_from_bytes(self, image_bytes: bytes, output_path: str) -> bool:
        """将字节数据保存为图片文件"""
        try:
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            return True
        except Exception:
            return False
    
    def get_all_text(self, image_path: str) -> str:
        """获取图片中的所有文本"""
        results = self.recognize_image(image_path)
        return ' '.join([r['text'] for r in results])
