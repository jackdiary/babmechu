"""
영양소 관련 유틸리티 함수들
"""

from typing import Dict, List

def validate_nutrition_data(nutrition_data: Dict) -> bool:
    """
    영양소 데이터 유효성 검증
    
    Args:
        nutrition_data: 영양소 데이터 딕셔너리
        
    Returns:
        유효성 여부
    """
    required_fields = [
        'e',  # 칼로리
        'cal',  # 탄수화물
        'sug',  # 당류
        'pro',  # 단백질
        'fat',  # 지방
        'total_sfa',  # 포화지방
        'chol',  # 콜레스테롤
        'na',  # 나트륨
        'total_tfa'  # 식이섬유 (trans fat으로 표기되어 있지만 실제로는 fiber)
    ]
    
    for field in required_fields:
        if field not in nutrition_data:
            return False
        
        # 숫자 타입 확인
        try:
            float(nutrition_data[field])
        except (ValueError, TypeError):
            return False
    
    return True

def normalize_nutrition_data(raw_nutrition: Dict) -> Dict[str, float]:
    """
    JSON에서 읽은 영양소 데이터를 표준 형식으로 변환
    
    Args:
        raw_nutrition: JSON에서 읽은 원시 영양소 데이터
        
    Returns:
        표준화된 영양소 데이터
    """
    return {
        'calories': float(raw_nutrition.get('e', 0)),
        'carbohydrates': float(raw_nutrition.get('cal', 0)),
        'sugars': float(raw_nutrition.get('sug', 0)),
        'protein': float(raw_nutrition.get('pro', 0)),
        'fat': float(raw_nutrition.get('fat', 0)),
        'saturated_fat': float(raw_nutrition.get('total_sfa', 0)),
        'cholesterol': float(raw_nutrition.get('chol', 0)),
        'sodium': float(raw_nutrition.get('na', 0)),
        'fiber': float(raw_nutrition.get('total_tfa', 0))  # 실제로는 식이섬유
    }

def get_nutrition_display_names() -> Dict[str, str]:
    """
    영양소 표시명 딕셔너리 반환
    
    Returns:
        영양소 키와 한글 표시명 매핑
    """
    return {
        'calories': '칼로리 (kcal)',
        'carbohydrates': '탄수화물 (g)',
        'sugars': '당류 (g)',
        'protein': '단백질 (g)',
        'fat': '지방 (g)',
        'saturated_fat': '포화지방 (g)',
        'cholesterol': '콜레스테롤 (mg)',
        'sodium': '나트륨 (mg)',
        'fiber': '식이섬유 (g)'
    }

def get_nutrition_units() -> Dict[str, str]:
    """
    영양소 단위 딕셔너리 반환
    
    Returns:
        영양소 키와 단위 매핑
    """
    return {
        'calories': 'kcal',
        'carbohydrates': 'g',
        'sugars': 'g',
        'protein': 'g',
        'fat': 'g',
        'saturated_fat': 'g',
        'cholesterol': 'mg',
        'sodium': 'mg',
        'fiber': 'g'
    }

def format_nutrition_value(nutrient: str, value: float) -> str:
    """
    영양소 값을 적절한 형식으로 포맷팅
    
    Args:
        nutrient: 영양소 키
        value: 영양소 값
        
    Returns:
        포맷팅된 문자열
    """
    units = get_nutrition_units()
    unit = units.get(nutrient, '')
    
    # 소수점 처리
    if value == int(value):
        return f"{int(value)}{unit}"
    else:
        return f"{value:.1f}{unit}"

def calculate_nutrition_score(nutrition_data: Dict[str, float], 
                            targets: Dict[str, float]) -> float:
    """
    영양소 균형 점수 계산 (0-100점)
    
    Args:
        nutrition_data: 현재 영양소 데이터
        targets: 목표 영양소 데이터
        
    Returns:
        영양소 균형 점수
    """
    total_score = 0
    nutrient_count = 0
    
    for nutrient, target in targets.items():
        if target > 0:
            current = nutrition_data.get(nutrient, 0)
            ratio = current / target
            
            # 최적 비율 (80-120%)에서 최고점
            if 0.8 <= ratio <= 1.2:
                score = 100
            elif 0.5 <= ratio < 0.8 or 1.2 < ratio <= 1.5:
                score = 70
            elif 0.3 <= ratio < 0.5 or 1.5 < ratio <= 2.0:
                score = 40
            else:
                score = 10
            
            total_score += score
            nutrient_count += 1
    
    return round(total_score / nutrient_count if nutrient_count > 0 else 0, 1)