"""
개인 맞춤형 추천 서비스
"""

from typing import Dict, List, Tuple, Optional
from services.nutrition_service import NutritionCalculatorService
from services.nutrition_data_service import get_nutrition_data_service
from services.intake_service import SessionIntakeService
from services.profile_service import SessionProfileService
import logging

class RecommendationEngine:
    """추천 엔진"""
    
    def __init__(self):
        self.nutrition_calculator = NutritionCalculatorService()
        self.nutrition_data_service = get_nutrition_data_service()
    
    def analyze_nutritional_gaps(self, user_profile: Dict = None) -> Dict:
        """
        영양 부족분 분석
        
        Args:
            user_profile: 사용자 프로필 (None이면 세션에서 조회)
            
        Returns:
            영양 분석 결과
        """
        try:
            # 사용자 프로필 확인
            if user_profile is None:
                user_profile = SessionProfileService.get_profile()
            
            if not user_profile or 'nutrition_targets' not in user_profile:
                raise ValueError("사용자 프로필이 설정되지 않았습니다.")
            
            # 현재 섭취량 조회
            current_intake = SessionIntakeService.get_current_totals()
            targets = user_profile['nutrition_targets']
            
            # 부족분과 과잉분 계산
            deficient, excess = self.nutrition_calculator.identify_nutritional_gaps(
                current_intake, targets
            )
            
            # 백분율 계산
            percentages = self.nutrition_calculator.calculate_nutrition_percentage(
                current_intake, targets
            )
            
            # 남은 허용량 계산
            remaining = self.nutrition_calculator.get_remaining_allowance(
                current_intake, targets
            )
            
            # 우선순위 영양소 식별
            priority_nutrients = self._identify_priority_nutrients(
                deficient, excess, percentages
            )
            
            return {
                'current_intake': current_intake,
                'targets': targets,
                'deficient_nutrients': deficient,
                'excess_nutrients': excess,
                'percentages': percentages,
                'remaining_allowance': remaining,
                'priority_nutrients': priority_nutrients,
                'analysis_summary': self._generate_analysis_summary(
                    deficient, excess, percentages
                )
            }
            
        except Exception as e:
            logging.error(f"영양 부족분 분석 중 오류: {str(e)}")
            raise
    
    def _identify_priority_nutrients(self, deficient: Dict, excess: Dict, 
                                   percentages: Dict) -> Dict:
        """
        우선순위 영양소 식별
        
        Args:
            deficient: 부족한 영양소
            excess: 과잉 영양소
            percentages: 현재 섭취 백분율
            
        Returns:
            우선순위 영양소 정보
        """
        priority = {
            'high_priority_deficient': [],  # 심각하게 부족한 영양소
            'moderate_priority_deficient': [],  # 보통 부족한 영양소
            'excess_warning': [],  # 과잉 주의 영양소
            'balanced': []  # 균형 잡힌 영양소
        }
        
        for nutrient, percentage in percentages.items():
            if percentage < 50:  # 50% 미만
                priority['high_priority_deficient'].append({
                    'nutrient': nutrient,
                    'percentage': percentage,
                    'deficiency': deficient.get(nutrient, 0)
                })
            elif percentage < 80:  # 50-80%
                priority['moderate_priority_deficient'].append({
                    'nutrient': nutrient,
                    'percentage': percentage,
                    'deficiency': deficient.get(nutrient, 0)
                })
            elif percentage > 120:  # 120% 초과
                priority['excess_warning'].append({
                    'nutrient': nutrient,
                    'percentage': percentage,
                    'excess': excess.get(nutrient, 0)
                })
            else:  # 80-120%
                priority['balanced'].append({
                    'nutrient': nutrient,
                    'percentage': percentage
                })
        
        return priority
    
    def _generate_analysis_summary(self, deficient: Dict, excess: Dict, 
                                 percentages: Dict) -> Dict:
        """
        분석 요약 생성
        
        Args:
            deficient: 부족한 영양소
            excess: 과잉 영양소
            percentages: 현재 섭취 백분율
            
        Returns:
            분석 요약
        """
        total_nutrients = len(percentages)
        balanced_count = sum(1 for p in percentages.values() if 80 <= p <= 120)
        deficient_count = len(deficient)
        excess_count = len(excess)
        
        # 전체 영양 점수 계산
        from utils.nutrition_utils import calculate_nutrition_score
        profile = SessionProfileService.get_profile()
        current_intake = SessionIntakeService.get_current_totals()
        
        nutrition_score = 0
        if profile and 'nutrition_targets' in profile:
            nutrition_score = calculate_nutrition_score(
                current_intake, profile['nutrition_targets']
            )
        
        return {
            'total_nutrients': total_nutrients,
            'balanced_nutrients': balanced_count,
            'deficient_nutrients': deficient_count,
            'excess_nutrients': excess_count,
            'balance_percentage': round((balanced_count / total_nutrients) * 100, 1),
            'nutrition_score': nutrition_score,
            'overall_status': self._get_overall_status(nutrition_score),
            'recommendations': self._get_general_recommendations(
                deficient_count, excess_count, nutrition_score
            )
        }
    
    def _get_overall_status(self, nutrition_score: float) -> str:
        """전체 영양 상태 평가"""
        if nutrition_score >= 85:
            return 'excellent'
        elif nutrition_score >= 70:
            return 'good'
        elif nutrition_score >= 50:
            return 'fair'
        else:
            return 'needs_improvement'
    
    def _get_general_recommendations(self, deficient_count: int, 
                                   excess_count: int, nutrition_score: float) -> List[str]:
        """일반적인 권장사항 생성"""
        recommendations = []
        
        if deficient_count > 3:
            recommendations.append("여러 영양소가 부족합니다. 다양한 음식을 섭취해보세요.")
        elif deficient_count > 0:
            recommendations.append("일부 영양소가 부족합니다. 균형 잡힌 식단을 권장합니다.")
        
        if excess_count > 2:
            recommendations.append("일부 영양소 섭취가 과도합니다. 섭취량을 조절해보세요.")
        
        if nutrition_score < 50:
            recommendations.append("전반적인 영양 균형 개선이 필요합니다.")
        elif nutrition_score >= 85:
            recommendations.append("훌륭한 영양 균형을 유지하고 있습니다!")
        
        if not recommendations:
            recommendations.append("현재 영양 상태가 양호합니다. 이 상태를 유지해보세요.")
        
        return recommendations

class MenuRecommendationEngine:
    """메뉴 추천 엔진"""
    
    def __init__(self):
        self.nutrition_calculator = NutritionCalculatorService()
        self.nutrition_data_service = get_nutrition_data_service()
    
    def generate_recommendations(self, max_recommendations: int = 3) -> List[Dict]:
        """
        메뉴 추천 생성
        
        Args:
            max_recommendations: 최대 추천 개수
            
        Returns:
            추천 메뉴 리스트
        """
        try:
            # 영양 분석 수행
            analyzer = NutritionalGapAnalyzer()
            analysis = analyzer.get_detailed_analysis()
            
            if not analysis['deficient_nutrients']:
                return self._get_balanced_recommendations(max_recommendations)
            
            # 사용 가능한 음식 목록 조회
            available_foods = self.nutrition_data_service.get_available_foods()
            
            if not available_foods:
                return []
            
            # 최근 식사 기록에서 먹은 음식 제외
            recent_foods = self._get_recent_eaten_foods()
            available_foods = [food for food in available_foods if food not in recent_foods]
            
            if not available_foods:
                return []
            
            # 각 음식에 대해 점수 계산
            food_scores = []
            
            for food_name in available_foods:
                nutrition_data = self.nutrition_data_service.get_nutrition_data(food_name)
                if nutrition_data:
                    score = self._calculate_recommendation_score(
                        nutrition_data['nutrition'],
                        analysis['deficient_nutrients'],
                        analysis['excess_nutrients'],
                        analysis['remaining_allowance']
                    )
                    
                    if score > 0:  # 점수가 있는 음식만 포함
                        food_scores.append({
                            'food_name': food_name,
                            'nutrition_data': nutrition_data,
                            'score': score,
                            'reasoning': self._generate_reasoning(
                                nutrition_data['nutrition'],
                                analysis['deficient_nutrients']
                            )
                        })
            
            # 점수순으로 정렬
            food_scores.sort(key=lambda x: x['score'], reverse=True)
            
            # 상위 추천 메뉴 반환
            recommendations = food_scores[:max_recommendations]
            
            # 추천 이유 보강
            for rec in recommendations:
                rec['benefits'] = self._identify_nutritional_benefits(
                    rec['nutrition_data']['nutrition'],
                    analysis['deficient_nutrients']
                )
            
            return recommendations
            
        except Exception as e:
            logging.error(f"메뉴 추천 생성 중 오류: {str(e)}")
            return []
    
    def _calculate_recommendation_score(self, food_nutrition: Dict, 
                                     deficient: Dict, excess: Dict, 
                                     remaining: Dict) -> float:
        """
        추천 점수 계산
        
        Args:
            food_nutrition: 음식의 영양소 정보
            deficient: 부족한 영양소
            excess: 과잉 영양소
            remaining: 남은 허용량
            
        Returns:
            추천 점수 (0-100)
        """
        score = 0
        
        # 부족한 영양소 보충 점수
        for nutrient, deficiency in deficient.items():
            food_value = food_nutrition.get(nutrient, 0)
            if food_value > 0:
                # 부족분 대비 음식의 영양소 비율
                contribution_ratio = min(food_value / deficiency, 1.0)
                score += contribution_ratio * 30  # 최대 30점
        
        # 과잉 영양소 페널티
        for nutrient, excess_amount in excess.items():
            food_value = food_nutrition.get(nutrient, 0)
            if food_value > 0:
                # 과잉 영양소가 많은 음식은 점수 차감
                penalty_ratio = min(food_value / excess_amount, 1.0)
                score -= penalty_ratio * 20  # 최대 -20점
        
        # 남은 허용량 내에서의 적절성 점수
        appropriateness_score = 0
        valid_nutrients = 0
        
        for nutrient, remaining_amount in remaining.items():
            food_value = food_nutrition.get(nutrient, 0)
            if remaining_amount > 0:
                # 남은 허용량의 10-50% 범위가 이상적
                ratio = food_value / remaining_amount
                if 0.1 <= ratio <= 0.5:
                    appropriateness_score += 10
                elif 0.05 <= ratio <= 0.8:
                    appropriateness_score += 5
                valid_nutrients += 1
        
        if valid_nutrients > 0:
            score += appropriateness_score / valid_nutrients
        
        # 전체 영양 균형 점수
        from utils.nutrition_utils import calculate_nutrition_score
        profile = SessionProfileService.get_profile()
        if profile and 'nutrition_targets' in profile:
            current_intake = SessionIntakeService.get_current_totals()
            
            # 이 음식을 먹었을 때의 예상 영양 상태
            projected_intake = current_intake.copy()
            for nutrient, value in food_nutrition.items():
                projected_intake[nutrient] = projected_intake.get(nutrient, 0) + value
            
            projected_score = calculate_nutrition_score(
                projected_intake, profile['nutrition_targets']
            )
            current_score = calculate_nutrition_score(
                current_intake, profile['nutrition_targets']
            )
            
            # 영양 점수 개선도
            improvement = projected_score - current_score
            score += improvement * 0.5  # 개선도에 따른 보너스
        
        return max(0, score)  # 음수 점수 방지
    
    def _generate_reasoning(self, food_nutrition: Dict, deficient: Dict) -> str:
        """추천 이유 생성"""
        reasons = []
        
        # 부족한 영양소 중 이 음식이 보충할 수 있는 것들
        for nutrient, deficiency in deficient.items():
            food_value = food_nutrition.get(nutrient, 0)
            if food_value > deficiency * 0.1:  # 부족분의 10% 이상 보충
                from utils.nutrition_utils import get_nutrition_display_names
                display_names = get_nutrition_display_names()
                nutrient_name = display_names.get(nutrient, nutrient)
                reasons.append(f"{nutrient_name} 보충")
        
        if not reasons:
            reasons.append("균형 잡힌 영양소 제공")
        
        return ", ".join(reasons[:3])  # 최대 3개 이유
    
    def _identify_nutritional_benefits(self, food_nutrition: Dict, 
                                     deficient: Dict) -> List[str]:
        """영양상 이점 식별"""
        benefits = []
        
        from utils.nutrition_utils import get_nutrition_display_names
        display_names = get_nutrition_display_names()
        
        # 주요 영양소별 이점
        nutrient_benefits = {
            'protein': '근육 건강과 포만감 증진',
            'fiber': '소화 건강과 포만감 증진',
            'calories': '에너지 공급',
            'carbohydrates': '즉각적인 에너지 공급',
            'fat': '필수 지방산 공급'
        }
        
        # 부족한 영양소 중 이 음식이 제공하는 것들
        for nutrient, deficiency in deficient.items():
            food_value = food_nutrition.get(nutrient, 0)
            if food_value > deficiency * 0.15:  # 부족분의 15% 이상
                benefit = nutrient_benefits.get(nutrient)
                if benefit:
                    benefits.append(benefit)
        
        # 특별히 높은 영양소
        for nutrient, value in food_nutrition.items():
            if value > 0:
                if nutrient == 'protein' and value > 15:
                    benefits.append('고단백 식품')
                elif nutrient == 'fiber' and value > 5:
                    benefits.append('식이섬유 풍부')
                elif nutrient == 'calories' and value < 200:
                    benefits.append('저칼로리 식품')
        
        return list(set(benefits))  # 중복 제거
    
    def _get_recent_eaten_foods(self, days: int = 1) -> List[str]:
        """
        최근 먹은 음식 목록 조회
        
        Args:
            days: 조회할 일수 (기본 1일)
            
        Returns:
            최근 먹은 음식명 리스트
        """
        recent_foods = []
        
        try:
            # 최근 식사 기록 조회
            meals = SessionIntakeService.get_meal_history(limit=20)  # 최근 20개 식사
            
            # 음식명만 추출 (중복 제거)
            for meal in meals:
                food_name = meal.get('food_name')
                if food_name and food_name not in recent_foods:
                    recent_foods.append(food_name)
            
            logging.info(f"최근 먹은 음식 {len(recent_foods)}개 제외: {recent_foods}")
            
        except Exception as e:
            logging.error(f"최근 식사 기록 조회 중 오류: {str(e)}")
        
        return recent_foods
    
    def _get_balanced_recommendations(self, max_recommendations: int) -> List[Dict]:
        """균형 잡힌 추천 (부족한 영양소가 없을 때)"""
        available_foods = self.nutrition_data_service.get_available_foods()
        
        if not available_foods:
            return []
        
        # 최근 먹은 음식 제외
        recent_foods = self._get_recent_eaten_foods()
        available_foods = [food for food in available_foods if food not in recent_foods]
        
        if not available_foods:
            return []
        
        # 다양한 영양소를 제공하는 음식들 선택
        recommendations = []
        
        for food_name in available_foods[:max_recommendations]:
            nutrition_data = self.nutrition_data_service.get_nutrition_data(food_name)
            if nutrition_data:
                recommendations.append({
                    'food_name': food_name,
                    'nutrition_data': nutrition_data,
                    'score': 70,  # 기본 점수
                    'reasoning': '균형 잡힌 영양소 제공',
                    'benefits': ['다양한 영양소 공급', '식단 다양성 증진']
                })
        
        return recommendations

class NutritionalGapAnalyzer:
    """영양 부족분 분석기"""
    
    def __init__(self):
        self.recommendation_engine = RecommendationEngine()
    
    def get_detailed_analysis(self) -> Dict:
        """상세 영양 분석 수행"""
        try:
            return self.recommendation_engine.analyze_nutritional_gaps()
        except Exception as e:
            logging.error(f"상세 영양 분석 중 오류: {str(e)}")
            return self._get_default_analysis()
    
    def get_nutrient_priorities(self) -> List[Dict]:
        """영양소 우선순위 목록 반환"""
        try:
            analysis = self.recommendation_engine.analyze_nutritional_gaps()
            priorities = analysis['priority_nutrients']
            
            # 우선순위 순으로 정렬된 리스트 생성
            priority_list = []
            
            # 1. 심각하게 부족한 영양소
            for item in priorities['high_priority_deficient']:
                priority_list.append({
                    'nutrient': item['nutrient'],
                    'priority': 'high',
                    'type': 'deficient',
                    'percentage': item['percentage'],
                    'value': item['deficiency']
                })
            
            # 2. 보통 부족한 영양소
            for item in priorities['moderate_priority_deficient']:
                priority_list.append({
                    'nutrient': item['nutrient'],
                    'priority': 'moderate',
                    'type': 'deficient',
                    'percentage': item['percentage'],
                    'value': item['deficiency']
                })
            
            # 3. 과잉 주의 영양소
            for item in priorities['excess_warning']:
                priority_list.append({
                    'nutrient': item['nutrient'],
                    'priority': 'warning',
                    'type': 'excess',
                    'percentage': item['percentage'],
                    'value': item['excess']
                })
            
            return priority_list
            
        except Exception as e:
            logging.error(f"영양소 우선순위 분석 중 오류: {str(e)}")
            return []
    
    def _get_default_analysis(self) -> Dict:
        """기본 분석 결과 반환 (오류 시)"""
        return {
            'current_intake': {},
            'targets': {},
            'deficient_nutrients': {},
            'excess_nutrients': {},
            'percentages': {},
            'remaining_allowance': {},
            'priority_nutrients': {
                'high_priority_deficient': [],
                'moderate_priority_deficient': [],
                'excess_warning': [],
                'balanced': []
            },
            'analysis_summary': {
                'total_nutrients': 0,
                'balanced_nutrients': 0,
                'deficient_nutrients': 0,
                'excess_nutrients': 0,
                'balance_percentage': 0,
                'nutrition_score': 0,
                'overall_status': 'unknown',
                'recommendations': ['프로필을 설정하고 식사를 기록해주세요.']
            }
        }