"""
PyTorch 기반 음식 분류 서비스
"""
import os
import numpy as np
from PIL import Image, ImageOps
from typing import List, Tuple, Optional
import logging

# PyTorch 사용
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torchvision import transforms
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logging.error("PyTorch가 설치되지 않았습니다. pip install torch torchvision")

class FoodClassifier(nn.Module):
    """음식 분류 모델 (실제 .pth 파일 구조에 맞춤 - BatchNorm 없음)"""
    
    def __init__(self, num_classes=11):
        super(FoodClassifier, self).__init__()
        
        # 컨볼루션 레이어 (BatchNorm 없음)
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        
        # 풀링 레이어
        self.pool = nn.MaxPool2d(2, 2)
        
        # 완전연결 레이어 (실제 모델은 dense1, dense2 사용)
        # 디버그 출력에서 확인된 실제 크기: dense1.weight: torch.Size([256, 10752])
        self.dense1 = nn.Linear(10752, 256)  # 실제 모델의 dense1
        self.dense2 = nn.Linear(256, num_classes)   # 실제 모델의 dense2
        
        # 드롭아웃
        self.dropout = nn.Dropout(0.5)
        
    def forward(self, x):
        # 컨볼루션 + 풀링 (BatchNorm 없음)
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = self.pool(F.relu(self.conv4(x)))
        
        # 평탄화
        x = x.view(x.size(0), -1)
        
        # 완전연결 레이어
        x = F.relu(self.dense1(x))
        x = self.dropout(x)
        x = self.dense2(x)
        
        return x

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
        
        # 이미지 전처리 변환 (실제 모델 훈련 방식과 동일)
        self.transform = transforms.Compose([
            transforms.Resize((100, 125)),  # HEIGHT=100, WIDTH=125
            transforms.ToTensor(),  # 0-1 스케일링만 (정규화 없음)
        ])
        
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
            
            # 실제 모델의 클래스 순서 (제공된 코드 기준)
            actual_class_names = [
                '10배추김치', '11콩나물국', '1감자탕', '2삼계탕', '3김치찌개', 
                '4갈치조림', '5곱창전골', '6김치볶음밥', '7잡곡밥', '8꿀떡', '9시금치나물'
            ]
            
            # 번호 제거하고 실제 음식명만 추출
            self.class_names = []
            for name in actual_class_names:
                # 숫자 접두사 제거
                clean_name = name[2:] if name[1:2].isdigit() else name[1:]
                self.class_names.append(clean_name)
            
            logging.info(f"실제 모델 클래스 순서: {self.class_names}")
            
            # 모델 가중치 먼저 로드하여 구조 파악
            checkpoint = torch.load(self.model_path, map_location=self.device)
            
            # state_dict 추출
            if isinstance(checkpoint, dict) and 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            elif isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            else:
                # 직접 state_dict인 경우
                state_dict = checkpoint
            
            # 실제 모델 구조로 생성
            self.model = FoodClassifier(num_classes=len(self.class_names))
            
            # 모델 가중치 로드
            self.model.load_state_dict(state_dict)
            
            self.model.to(self.device)
            self.model.eval()
            
            logging.info(f"PyTorch 모델이 성공적으로 로드되었습니다: {self.model_path}")
            logging.info(f"{len(self.class_names)}개의 클래스가 로드되었습니다.")
            logging.info(f"사용 디바이스: {self.device}")
            self.is_loaded = True
            
        except Exception as e:
            logging.error(f"PyTorch 모델 로딩 실패: {str(e)}")
            raise RuntimeError(f"PyTorch 모델 로딩에 실패했습니다: {str(e)}")
    
    def preprocess_image(self, image_file) -> Optional[torch.Tensor]:
        """
        이미지 전처리 (PyTorch 입력 형식에 맞춤: 100x125)
        Args:
            image_file: 업로드된 이미지 파일
        Returns:
            전처리된 이미지 텐서 또는 None
        """
        try:
            # PIL Image로 변환
            if isinstance(image_file, Image.Image):
                image = image_file.convert("RGB")
            else:
                image = Image.open(image_file).convert("RGB")
            
            # 100x125로 리사이즈 (HEIGHT=100, WIDTH=125)
            # PIL resize는 (width, height) 순서이므로 (125, 100)
            image = image.resize((125, 100), Image.Resampling.LANCZOS)
            
            # 변환 적용
            tensor = self.transform(image).unsqueeze(0)  # 배치 차원 추가
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
            raise RuntimeError("PyTorch 모델이 로드되지 않았습니다.")
        
        try:
            with torch.no_grad():
                # 모델 추론
                outputs = self.model(image_tensor)
                
                # 실제 모델과 동일한 소프트맥스 적용
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
_pytorch_service = None

def get_pytorch_service() -> PyTorchService:
    """PyTorch 서비스 인스턴스 반환"""
    global _pytorch_service
    if _pytorch_service is None:
        _pytorch_service = PyTorchService()
    return _pytorch_service