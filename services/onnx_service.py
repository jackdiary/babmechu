"""
ONNX/PyTorch 기반 음식 분류 서비스
"""
import os
import numpy as np
from PIL import Image, ImageOps
from typing import List, Tuple, Optional
import logging

# ONNX Runtime 사용
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logging.error("ONNX Runtime이 설치되지 않았습니다. pip install onnxruntime")

# PyTorch 사용
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.error("PyTorch가 설치되지 않았습니다. pip install torch")

class ONNXService:
    """ONNX 기반 음식 분류 서비스"""
    
    def __init__(self, model_path: str = None, labels_path: str = None):
        """
        Args:
            model_path: ONNX 모델 파일 경로
            labels_path: 라벨 파일 경로
        """
        self.model_path = model_path or 'models/ml_models/best_food_model_v2.onnx'
        self.labels_path = labels_path or 'models/ml_models/labels.txt'
        self.session = None
        self.class_names = []
        self.is_loaded = False
        
        # 모델 로딩
        self._load_model()
    
    def _load_model(self):
        """ONNX 모델과 라벨 로딩"""
        try:
            if not ONNX_AVAILABLE:
                logging.error("ONNX Runtime이 설치되지 않았습니다.")
                self.is_loaded = False
                return
            
            # ONNX 모델 파일 존재 확인
            if not os.path.exists(self.model_path):
                logging.error(f"ONNX 모델을 찾을 수 없습니다: {self.model_path}")
                self.is_loaded = False
                return
            
            # 라벨 파일 로딩
            if not os.path.exists(self.labels_path):
                logging.error(f"라벨 파일을 찾을 수 없습니다: {self.labels_path}")
                self.is_loaded = False
                return
            
            with open(self.labels_path, 'r', encoding='utf-8') as f:
                self.class_names = [line.strip() for line in f.readlines() if line.strip()]
            
            # ONNX 세션 생성
            self.session = ort.InferenceSession(self.model_path)
            
            logging.info(f"ONNX 모델이 성공적으로 로드되었습니다: {self.model_path}")
            logging.info(f"{len(self.class_names)}개의 클래스가 로드되었습니다.")
            self.is_loaded = True
            
        except Exception as e:
            logging.error(f"ONNX 모델 로딩 실패: {str(e)}")
            raise RuntimeError(f"ONNX 모델 로딩에 실패했습니다: {str(e)}")
    
    def preprocess_image(self, image_file) -> Optional[np.ndarray]:
        """
        이미지 전처리 (기존 ONNX 모델 형식에 맞춤: 100x125)
        Args:
            image_file: 업로드된 이미지 파일
        Returns:
            전처리된 이미지 배열 또는 None
        """
        try:
            # PIL Image로 변환
            image = Image.open(image_file).convert("RGB")
            
            # 100x125로 리사이즈 (기존 모델 형식)
            size = (100, 125)
            image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
            
            # numpy 배열로 변환
            image_array = np.asarray(image)
            
            # 정규화 (-1 ~ 1 범위로, Teachable Machine 방식)
            normalized_image_array = (image_array.astype(np.float32) / 255.0 - 0.5) / 0.5
            
            # CHW 형태로 변환 후 배치 차원 추가 (1, 3, 125, 100)
            data = np.transpose(normalized_image_array, (2, 0, 1))  # HWC -> CHW
            data = np.expand_dims(data, axis=0)  # 배치 차원 추가
            
            return data
            
        except Exception as e:
            logging.error(f"이미지 전처리 중 오류 발생: {str(e)}")
            return None
    
    def classify_food(self, image_array: np.ndarray) -> Optional[Tuple[str, float, List[Tuple[str, float]]]]:
        """
        ONNX 모델을 사용한 음식 분류
        Args:
            image_array: 전처리된 이미지 배열
        Returns:
            (예측된 음식명, 신뢰도, 상위 3개 예측) 또는 None
        """
        if not self.is_loaded:
            raise RuntimeError("ONNX 모델이 로드되지 않았습니다.")
        
        try:
            # ONNX 모델 추론
            input_name = self.session.get_inputs()[0].name
            output_name = self.session.get_outputs()[0].name
            
            # 모델 실행
            result = self.session.run([output_name], {input_name: image_array})
            prediction = result[0][0]  # 배치 차원 제거
            
            # 소프트맥스 적용 (Teachable Machine 모델은 보통 로짓 출력)
            exp_pred = np.exp(prediction - np.max(prediction))  # 수치 안정성
            prediction = exp_pred / np.sum(exp_pred)
            
            # 가장 높은 확률의 클래스 찾기
            predicted_index = np.argmax(prediction)
            confidence_score = float(prediction[predicted_index])
            
            # 클래스명 추출
            if predicted_index < len(self.class_names):
                food_name = self.class_names[predicted_index]
            else:
                raise IndexError(f"예측된 인덱스 {predicted_index}가 클래스 수 {len(self.class_names)}를 초과합니다.")
            
            # 상위 3개 예측 결과
            top_3_indices = np.argsort(prediction)[-3:][::-1]
            top_3_predictions = []
            
            for idx in top_3_indices:
                if idx < len(self.class_names):
                    class_food_name = self.class_names[idx]
                    confidence = float(prediction[idx])
                    top_3_predictions.append((class_food_name, confidence))
            
            logging.info(f"ONNX 예측: {food_name} (신뢰도: {confidence_score:.3f})")
            return food_name, confidence_score, top_3_predictions
                
        except Exception as e:
            logging.error(f"ONNX 분류 중 오류 발생: {str(e)}")
            raise RuntimeError(f"음식 분류에 실패했습니다: {str(e)}")
    
    def get_supported_foods(self) -> List[str]:
        """지원되는 음식 목록 반환"""
        return self.class_names.copy()
    
    def is_model_ready(self) -> bool:
        """모델 준비 상태 확인"""
        return self.is_loaded
    
    def get_confidence_threshold(self) -> float:
        """신뢰도 임계값 반환"""
        return 0.7
    
    def get_model_info(self) -> dict:
        """모델 정보 반환"""
        return {
            'model_type': 'ONNX',
            'model_path': self.model_path,
            'labels_path': self.labels_path,
            'num_classes': len(self.class_names),
            'is_loaded': self.is_loaded,
            'onnx_available': ONNX_AVAILABLE
        }

class PyTorchService:
    """PyTorch 기반 음식 분류 서비스"""
    
    def __init__(self, model_path: str = None, labels_path: str = None):
        """
        Args:
            model_path: PyTorch 모델 파일 경로
            labels_path: 라벨 파일 경로
        """
        self.model_path = model_path or 'models/ml_models/best_food_model.pth'
        self.labels_path = labels_path or 'models/ml_models/labels.txt'
        self.model = None
        self.class_names = []
        self.is_loaded = False
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 모델 로딩
        self._load_model()
    
    def _load_model(self):
        """PyTorch 모델과 라벨 로딩"""
        try:
            if not TORCH_AVAILABLE:
                raise RuntimeError("PyTorch가 설치되지 않았습니다.")
            
            # PyTorch 모델 파일 존재 확인
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"PyTorch 모델을 찾을 수 없습니다: {self.model_path}")
            
            # 라벨 파일 로딩
            if not os.path.exists(self.labels_path):
                raise FileNotFoundError(f"라벨 파일을 찾을 수 없습니다: {self.labels_path}")
            
            with open(self.labels_path, 'r', encoding='utf-8') as f:
                self.class_names = [line.strip() for line in f.readlines() if line.strip()]
            
            # PyTorch 모델 로딩
            self.model = torch.load(self.model_path, map_location=self.device)
            self.model.eval()
            
            logging.info(f"PyTorch 모델이 성공적으로 로드되었습니다: {self.model_path}")
            logging.info(f"{len(self.class_names)}개의 클래스가 로드되었습니다.")
            logging.info(f"사용 디바이스: {self.device}")
            self.is_loaded = True
            
        except Exception as e:
            logging.error(f"PyTorch 모델 로딩 실패: {str(e)}")
            raise RuntimeError(f"모델 로딩에 실패했습니다: {str(e)}")
    
    def preprocess_image(self, image_file) -> Optional[torch.Tensor]:
        """
        이미지 전처리 (PyTorch 입력 형식에 맞춤)
        Args:
            image_file: 업로드된 이미지 파일
        Returns:
            전처리된 이미지 텐서 또는 None
        """
        try:
            # PIL Image로 변환
            image = Image.open(image_file).convert("RGB")
            
            # 224x224로 리사이즈
            size = (224, 224)
            image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
            
            # numpy 배열로 변환
            image_array = np.asarray(image)
            
            # 정규화 (0-255 -> 0-1)
            normalized_image_array = image_array.astype(np.float32) / 255.0
            
            # PyTorch 텐서로 변환 (1, 3, 224, 224)
            tensor = torch.from_numpy(normalized_image_array).permute(2, 0, 1).unsqueeze(0)
            tensor = tensor.to(self.device)
            
            return tensor
            
        except Exception as e:
            logging.error(f"이미지 전처리 중 오류 발생: {str(e)}")
            return None
    
    def classify_food(self, image_tensor: torch.Tensor) -> Optional[Tuple[str, float, List[Tuple[str, float]]]]:
        """
        PyTorch 모델을 사용한 음식 분류
        Args:
            image_tensor: 전처리된 이미지 텐서
        Returns:
            (예측된 음식명, 신뢰도, 상위 3개 예측) 또는 None
        """
        if not self.is_loaded:
            raise RuntimeError("모델이 로드되지 않았습니다.")
        
        try:
            with torch.no_grad():
                # 모델 추론
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                prediction = probabilities.cpu().numpy()[0]
            
            # 가장 높은 확률의 클래스 찾기
            predicted_index = np.argmax(prediction)
            confidence_score = float(prediction[predicted_index])
            
            # 클래스명 추출
            if predicted_index < len(self.class_names):
                food_name = self.class_names[predicted_index]
            else:
                raise IndexError(f"예측된 인덱스 {predicted_index}가 클래스 수 {len(self.class_names)}를 초과합니다.")
            
            # 상위 3개 예측 결과
            top_3_indices = np.argsort(prediction)[-3:][::-1]
            top_3_predictions = []
            
            for idx in top_3_indices:
                if idx < len(self.class_names):
                    class_food_name = self.class_names[idx]
                    confidence = float(prediction[idx])
                    top_3_predictions.append((class_food_name, confidence))
            
            logging.info(f"PyTorch 예측: {food_name} (신뢰도: {confidence_score:.3f})")
            return food_name, confidence_score, top_3_predictions
                
        except Exception as e:
            logging.error(f"PyTorch 분류 중 오류 발생: {str(e)}")
            raise RuntimeError(f"음식 분류에 실패했습니다: {str(e)}")
    
    def get_supported_foods(self) -> List[str]:
        """지원되는 음식 목록 반환"""
        return self.class_names.copy()
    
    def is_model_ready(self) -> bool:
        """모델 준비 상태 확인"""
        return self.is_loaded
    
    def get_confidence_threshold(self) -> float:
        """신뢰도 임계값 반환"""
        return 0.7
    
    def get_model_info(self) -> dict:
        """모델 정보 반환"""
        return {
            'model_type': 'PyTorch',
            'model_path': self.model_path,
            'labels_path': self.labels_path,
            'num_classes': len(self.class_names),
            'is_loaded': self.is_loaded,
            'device': str(self.device),
            'torch_available': TORCH_AVAILABLE
        }



# 전역 인스턴스 (싱글톤 패턴)
_ml_service = None

def get_ml_service(use_pytorch: bool = False) -> ONNXService:
    """ML 서비스 인스턴스 반환"""
    global _ml_service
    if _ml_service is None:
        try:
            if use_pytorch and TORCH_AVAILABLE:
                _ml_service = PyTorchService()
            elif ONNX_AVAILABLE:
                _ml_service = ONNXService()
            else:
                raise RuntimeError("ONNX Runtime 또는 PyTorch가 설치되지 않았습니다.")
        except Exception as e:
            logging.error(f"ML 서비스 초기화 실패: {str(e)}")
            raise
    return _ml_service