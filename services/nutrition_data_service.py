"""
영양 데이터 로딩 및 관리 서비스
"""

import os
import json
import logging
from typing import Dict, Optional, List
from utils.nutrition_utils import validate_nutrition_data, normalize_nutrition_data

class NutritionDataService:
    """영양 데이터 관리 서비스"""
    
    def __init__(self, data_directory: str = 'data/nutrition'):
        """
        Args:
            data_directory: 영양 데이터 JSON 파일들이 저장된 디렉토리
        """
        self.data_directory = data_directory
        self.nutrition_cache = {}  # 메모리 캐시
        self.last_loaded = None
        
        # 초기 데이터 로딩
        self.reload_nutrition_data()
    
    def reload_nutrition_data(self) -> bool:
        """
        영양 데이터 파일들을 다시 로딩
        
        Returns:
            로딩 성공 여부
        """
        try:
            if not os.path.exists(self.data_directory):
                logging.warning(f"영양 데이터 디렉토리가 존재하지 않습니다: {self.data_directory}")
                return False
            
            loaded_count = 0
            error_count = 0
            
            # 디렉토리 내 모든 JSON 파일 스캔
            for filename in os.listdir(self.data_directory):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.data_directory, filename)
                    food_name = os.path.splitext(filename)[0]  # 확장자 제거
                    
                    try:
                        nutrition_data = self._load_single_file(file_path)
                        if nutrition_data:
                            self.nutrition_cache[food_name] = nutrition_data
                            loaded_count += 1
                        else:
                            error_count += 1
                            
                    except Exception as e:
                        logging.error(f"파일 로딩 실패 {filename}: {str(e)}")
                        error_count += 1
            
            logging.info(f"영양 데이터 로딩 완료: {loaded_count}개 성공, {error_count}개 실패")
            
            from datetime import datetime
            self.last_loaded = datetime.now()
            
            return loaded_count > 0
            
        except Exception as e:
            logging.error(f"영양 데이터 로딩 중 오류 발생: {str(e)}")
            return False
    
    def _load_single_file(self, file_path: str) -> Optional[Dict]:
        """
        단일 JSON 파일 로딩
        
        Args:
            file_path: JSON 파일 경로
            
        Returns:
            정규화된 영양 데이터 또는 None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # JSON 구조 검증
            if 'data' not in raw_data or 'food_info' not in raw_data['data']:
                logging.error(f"잘못된 JSON 구조: {file_path}")
                return None
            
            food_info = raw_data['data']['food_info']
            
            if 'nutrition' not in food_info:
                logging.error(f"영양 정보가 없습니다: {file_path}")
                return None
            
            raw_nutrition = food_info['nutrition']
            
            # 영양 데이터 유효성 검증
            if not validate_nutrition_data(raw_nutrition):
                from utils.error_handler import get_error_handler
                error_handler = get_error_handler()
                food_name = os.path.splitext(os.path.basename(file_path))[0]
                result = error_handler.handle_validation_error(food_name, ["필수 영양소 필드 누락"])
                return result['data']
            
            # 데이터 정규화
            normalized_nutrition = normalize_nutrition_data(raw_nutrition)
            
            # 추가 메타데이터 포함
            result = {
                'name': food_info.get('name', ''),
                'serving_size': raw_nutrition.get('g', 100),  # 1회 제공량 (g)
                'nutrition': normalized_nutrition
            }
            
            return result
            
        except json.JSONDecodeError as e:
            from utils.error_handler import get_error_handler
            error_handler = get_error_handler()
            result = error_handler.handle_parsing_error(file_path, e)
            return result['data'] if result else None
        except Exception as e:
            from utils.error_handler import get_error_handler
            error_handler = get_error_handler()
            result = error_handler.handle_parsing_error(file_path, e)
            return result['data'] if result else None
    
    def get_nutrition_data(self, food_name: str) -> Optional[Dict]:
        """
        특정 음식의 영양 데이터 조회
        
        Args:
            food_name: 음식명
            
        Returns:
            영양 데이터 또는 None
        """
        # 캐시에서 먼저 확인
        if food_name in self.nutrition_cache:
            return self.nutrition_cache[food_name].copy()
        
        # 파일명 매칭 시도 (대소문자 무시, 공백 처리)
        normalized_name = food_name.strip()
        
        for cached_name, data in self.nutrition_cache.items():
            if cached_name.strip().lower() == normalized_name.lower():
                return data.copy()
        
        # 파일이 존재하는지 확인하고 동적 로딩 시도
        potential_filename = f"{food_name}.json"
        file_path = os.path.join(self.data_directory, potential_filename)
        
        if os.path.exists(file_path):
            logging.info(f"동적 로딩 시도: {food_name}")
            nutrition_data = self._load_single_file(file_path)
            if nutrition_data:
                self.nutrition_cache[food_name] = nutrition_data
                return nutrition_data.copy()
        
        # 오류 처리기를 통해 누락 데이터 처리
        from utils.error_handler import get_error_handler
        error_handler = get_error_handler()
        result = error_handler.handle_missing_data(food_name)
        return result['data']
    
    def get_available_foods(self) -> List[str]:
        """
        사용 가능한 음식 목록 반환
        
        Returns:
            음식명 리스트
        """
        return list(self.nutrition_cache.keys())
    
    def get_cache_info(self) -> Dict:
        """
        캐시 정보 반환
        
        Returns:
            캐시 정보 딕셔너리
        """
        return {
            'cached_foods_count': len(self.nutrition_cache),
            'last_loaded': self.last_loaded.isoformat() if self.last_loaded else None,
            'data_directory': self.data_directory
        }
    
    def add_nutrition_data(self, food_name: str, nutrition_data: Dict) -> bool:
        """
        새로운 영양 데이터 추가 (런타임)
        
        Args:
            food_name: 음식명
            nutrition_data: 영양 데이터
            
        Returns:
            추가 성공 여부
        """
        try:
            # 데이터 유효성 검증
            if 'nutrition' not in nutrition_data:
                return False
            
            if not validate_nutrition_data(nutrition_data['nutrition']):
                return False
            
            # 캐시에 추가
            self.nutrition_cache[food_name] = nutrition_data.copy()
            
            logging.info(f"영양 데이터 추가됨: {food_name}")
            return True
            
        except Exception as e:
            logging.error(f"영양 데이터 추가 실패 {food_name}: {str(e)}")
            return False
    
    def get_fallback_nutrition_data(self, food_name: str) -> Dict:
        """
        대체 영양 데이터 생성 (데이터가 없을 때)
        
        Args:
            food_name: 음식명
            
        Returns:
            기본 영양 데이터
        """
        logging.warning(f"대체 영양 데이터 사용: {food_name}")
        
        return {
            'name': food_name,
            'serving_size': 100,
            'nutrition': {
                'calories': 200.0,
                'carbohydrates': 30.0,
                'sugars': 5.0,
                'protein': 10.0,
                'fat': 8.0,
                'saturated_fat': 2.0,
                'cholesterol': 20.0,
                'sodium': 500.0,
                'fiber': 3.0
            },
            'is_fallback': True
        }

# 전역 인스턴스 (싱글톤 패턴)
_nutrition_data_service = None

def get_nutrition_data_service() -> NutritionDataService:
    """영양 데이터 서비스 인스턴스 반환"""
    global _nutrition_data_service
    if _nutrition_data_service is None:
        _nutrition_data_service = NutritionDataService()
    return _nutrition_data_service