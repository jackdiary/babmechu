"""
영양소 계산 및 관리 서비스
"""

import math
from typing import Dict, Tuple

class NutritionCalculatorService:
    """영양소 계산 서비스"""
    
    # 활동 수준별 계수
    ACTIVITY_MULTIPLIERS = {
        'low': 1.2,      # 저활동 (사무직, 운동 거의 안함)
        'moderate': 1.55, # 보통활동 (주 3-5회 운동)
        'high': 1.725    # 고활동 (주 6-7회 운동 또는 육체노동)
    }
    
    # 목표별 칼로리 조정
    GOAL_ADJUSTMENTS = {
        'lose': -500,    # 체중 감량: -500kcal
        'maintain': 0,   # 체중 유지: 변화 없음
        'gain': 300      # 체중 증량: +300kcal
    }
    
    def calculate_bmr(self, age: int, height: float, weight: float, gender: str) -> float:
        """
        기초대사율(BMR) 계산 - Harris-Benedict 공식 사용
        
        Args:
            age: 나이
            height: 키 (cm)
            weight: 몸무게 (kg)
            gender: 성별 ('M' 또는 'F')
            
        Returns:
            BMR (kcal/day)
        """
        if gender.upper() == 'M':
            # 남성: BMR = 88.362 + (13.397 × 체중) + (4.799 × 키) - (5.677 × 나이)
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            # 여성: BMR = 447.593 + (9.247 × 체중) + (3.098 × 키) - (4.330 × 나이)
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        return round(bmr, 1)
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """
        총 일일 에너지 소비량(TDEE) 계산
        
        Args:
            bmr: 기초대사율
            activity_level: 활동 수준 ('low', 'moderate', 'high')
            
        Returns:
            TDEE (kcal/day)
        """
        multiplier = self.ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
        tdee = bmr * multiplier
        return round(tdee, 1)
    
    def calculate_daily_nutrition_targets(self, tdee: float, goal: str) -> Dict[str, float]:
        """
        일일 영양소 목표량 계산
        
        Args:
            tdee: 총 일일 에너지 소비량
            goal: 목표 ('lose', 'maintain', 'gain')
            
        Returns:
            9가지 핵심 영양소 목표량 딕셔너리
        """
        # 목표에 따른 칼로리 조정
        adjustment = self.GOAL_ADJUSTMENTS.get(goal, 0)
        target_calories = tdee + adjustment
        
        # 매크로 영양소 비율 (일반적인 권장 비율)
        carb_ratio = 0.50      # 탄수화물 50%
        protein_ratio = 0.20   # 단백질 20%
        fat_ratio = 0.30       # 지방 30%
        
        # 매크로 영양소 계산 (g)
        carbs_g = (target_calories * carb_ratio) / 4  # 탄수화물 1g = 4kcal
        protein_g = (target_calories * protein_ratio) / 4  # 단백질 1g = 4kcal
        fat_g = (target_calories * fat_ratio) / 9  # 지방 1g = 9kcal
        
        # 기타 영양소 권장량 (한국인 영양소 섭취기준 참고)
        return {
            'calories': round(target_calories, 1),
            'carbohydrates': round(carbs_g, 1),
            'sugars': round(carbs_g * 0.1, 1),  # 총 탄수화물의 10% 이하
            'protein': round(protein_g, 1),
            'fat': round(fat_g, 1),
            'saturated_fat': round(fat_g * 0.33, 1),  # 총 지방의 1/3 이하
            'cholesterol': 300.0,  # mg
            'sodium': 2300.0,  # mg (WHO 권장)
            'fiber': 25.0 if goal != 'lose' else 30.0  # g (체중감량시 더 많이)
        }
    
    def calculate_nutrition_percentage(self, current: Dict[str, float], 
                                    targets: Dict[str, float]) -> Dict[str, float]:
        """
        현재 섭취량의 목표 대비 백분율 계산
        
        Args:
            current: 현재 섭취량
            targets: 목표 섭취량
            
        Returns:
            백분율 딕셔너리
        """
        percentages = {}
        
        for nutrient in targets.keys():
            current_value = current.get(nutrient, 0)
            target_value = targets.get(nutrient, 1)  # 0으로 나누기 방지
            
            if target_value > 0:
                percentage = (current_value / target_value) * 100
                percentages[nutrient] = round(percentage, 1)
            else:
                percentages[nutrient] = 0.0
        
        return percentages
    
    def get_remaining_allowance(self, current: Dict[str, float], 
                              targets: Dict[str, float]) -> Dict[str, float]:
        """
        남은 일일 허용량 계산
        
        Args:
            current: 현재 섭취량
            targets: 목표 섭취량
            
        Returns:
            남은 허용량 딕셔너리
        """
        remaining = {}
        
        for nutrient in targets.keys():
            current_value = current.get(nutrient, 0)
            target_value = targets.get(nutrient, 0)
            
            remaining_value = target_value - current_value
            remaining[nutrient] = round(max(0, remaining_value), 1)
        
        return remaining
    
    def identify_nutritional_gaps(self, current: Dict[str, float], 
                                targets: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        영양소 부족분과 과잉분 식별
        
        Args:
            current: 현재 섭취량
            targets: 목표 섭취량
            
        Returns:
            (부족분, 과잉분) 튜플
        """
        deficient = {}
        excess = {}
        
        for nutrient in targets.keys():
            current_value = current.get(nutrient, 0)
            target_value = targets.get(nutrient, 0)
            
            difference = current_value - target_value
            
            if difference < 0:
                # 부족분 (음수를 양수로 변환)
                deficient[nutrient] = round(abs(difference), 1)
            elif difference > target_value * 0.1:  # 목표의 10% 초과시 과잉으로 간주
                excess[nutrient] = round(difference, 1)
        
        return deficient, excess