"""
PyTorch 기반 음식 분류 서비스 (레거시 호환)
"""
from services.pytorch_service import get_pytorch_service

class FoodClassificationService:
    """음식 분류 ML 서비스 (레거시 호환용 래퍼)"""
    
    def __init__(self, model_path: str = None, labels_path: str = None):
        """PyTorch 서비스로 위임"""
        self._service = get_pytorch_service()
    
    def preprocess_image(self, image_file):
        """이미지 전처리 (PyTorch 서비스로 위임)"""
        return self._service.preprocess_image(image_file)
    
    def classify_food(self, image_tensor):
        """음식 분류 (PyTorch 서비스로 위임)"""
        return self._service.classify_food(image_tensor)
    
    def get_supported_foods(self):
        """지원되는 음식 목록 (PyTorch 서비스로 위임)"""
        return self._service.get_supported_foods()
    
    def is_model_ready(self):
        """모델 준비 상태 (PyTorch 서비스로 위임)"""
        return self._service.is_model_ready()
    
    def get_confidence_threshold(self):
        """신뢰도 임계값 (PyTorch 서비스로 위임)"""
        return self._service.get_confidence_threshold()
    
    def get_model_info(self):
        """모델 정보 (PyTorch 서비스로 위임)"""
        return self._service.get_model_info()
    
    def is_using_real_model(self):
        """실제 모델을 사용 중인지 확인 (PyTorch 서비스로 위임)"""
        return self._service.is_model_ready()

# 전역 인스턴스 (싱글톤 패턴)
_classification_service = None

def get_classification_service() -> FoodClassificationService:
    """분류 서비스 인스턴스 반환"""
    global _classification_service
    if _classification_service is None:
        _classification_service = FoodClassificationService()
    return _classification_service