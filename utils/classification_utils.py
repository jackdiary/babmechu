"""
이미지 분류 관련 유틸리티
"""

from typing import Dict, List, Tuple, Optional
import logging

class ClassificationErrorHandler:
    """이미지 분류 오류 처리기"""
    
    @staticmethod
    def handle_low_confidence(predictions: List[Tuple[str, float]], 
                            threshold: float = 0.7) -> Dict:
        """
        낮은 신뢰도 처리
        
        Args:
            predictions: [(음식명, 신뢰도)] 리스트
            threshold: 신뢰도 임계값
            
        Returns:
            처리 결과
        """
        if not predictions:
            return {
                'status': 'no_predictions',
                'message': '분류 결과가 없습니다.',
                'suggestions': ['다른 이미지를 업로드해보세요']
            }
        
        top_prediction = predictions[0]
        top_confidence = top_prediction[1]
        
        if top_confidence >= threshold:
            return {
                'status': 'confident',
                'predicted_food': top_prediction[0],
                'confidence': top_confidence,
                'message': '높은 신뢰도로 분류되었습니다.'
            }
        
        # 낮은 신뢰도 처리
        return {
            'status': 'low_confidence',
            'top_predictions': predictions[:3],
            'message': '분류 결과의 신뢰도가 낮습니다. 아래 옵션 중에서 선택해주세요.',
            'suggestions': [
                '더 선명한 이미지로 다시 시도해보세요',
                '음식이 화면 중앙에 오도록 촬영해보세요',
                '조명이 충분한 곳에서 촬영해보세요'
            ],
            'manual_selection_required': True
        }
    
    @staticmethod
    def generate_photography_tips(error_type: str = 'general') -> List[str]:
        """
        촬영 팁 생성
        
        Args:
            error_type: 오류 유형
            
        Returns:
            촬영 팁 리스트
        """
        general_tips = [
            '음식이 화면 중앙에 위치하도록 촬영하세요',
            '충분한 조명 아래에서 촬영하세요',
            '음식에 초점을 맞춰 선명하게 촬영하세요',
            '배경은 단순할수록 좋습니다',
            '음식 전체가 프레임 안에 들어오도록 하세요'
        ]
        
        specific_tips = {
            'blurry': [
                '카메라를 안정적으로 잡고 촬영하세요',
                '자동 초점이 음식에 맞춰지도록 화면을 터치하세요',
                '충분한 거리를 두고 촬영하세요'
            ],
            'dark': [
                '자연광이나 밝은 조명 아래에서 촬영하세요',
                '플래시 사용을 고려해보세요',
                '창가 근처에서 촬영해보세요'
            ],
            'cluttered': [
                '음식만 보이도록 배경을 정리하세요',
                '단색 배경을 사용하세요',
                '다른 물건들을 치워주세요'
            ],
            'partial': [
                '음식 전체가 보이도록 거리를 조절하세요',
                '세로/가로 방향을 바꿔서 촬영해보세요',
                '음식이 잘리지 않도록 주의하세요'
            ]
        }
        
        if error_type in specific_tips:
            return specific_tips[error_type] + general_tips[:2]
        
        return general_tips
    
    @staticmethod
    def suggest_alternative_foods(failed_food: str, 
                                available_foods: List[str]) -> List[str]:
        """
        대안 음식 제안
        
        Args:
            failed_food: 인식 실패한 음식
            available_foods: 사용 가능한 음식 목록
            
        Returns:
            유사한 음식 목록
        """
        if not available_foods:
            return []
        
        # 간단한 유사도 매칭 (실제로는 더 정교한 알고리즘 사용 가능)
        similar_foods = []
        
        # 카테고리별 그룹핑
        categories = {
            "감자탕", "김치찌개", "갈치조림", "곱창전골", "김치볶음밥", "잡곡밥", "꿀떡", "시금치나물", "배추김치", "콩나물국", "삼계탕"
        
    
        }
        
        # 실패한 음식과 같은 카테고리 찾기
        target_category = None
        for category, foods in categories.items():
            if any(food in failed_food for food in foods):
                target_category = category
                break
        
        if target_category:
            # 같은 카테고리의 다른 음식들 제안
            category_foods = categories[target_category]
            similar_foods = [food for food in category_foods 
                           if food in available_foods and food != failed_food]
        
        # 카테고리를 찾지 못했거나 유사한 음식이 없으면 인기 음식 제안
        if not similar_foods:
            popular_foods = ['감자탕', '삼계탕', '김치찌개', '갈치조림', '곱창전골']
            similar_foods = [food for food in popular_foods 
                           if food in available_foods]
        
        return similar_foods[:5]  # 최대 5개

class ClassificationGuideGenerator:
    """분류 가이드 생성기"""
    
    @staticmethod
    def get_supported_foods_guide() -> Dict:
        """지원되는 음식 가이드"""
        return {
            '국/찌개류': {
                'foods': ['감자탕', '삼계탕', '김치찌개', '콩나물국'],
                'tips': [
                    '국물이 잘 보이도록 촬영하세요',
                    '건더기가 보이도록 각도를 조절하세요'
                ]
            },
            '조림류': {
                'foods': ['갈치조림'],
                'tips': [
                    '양념이 잘 보이도록 촬영하세요',
                    '생선의 형태가 선명하게 나오도록 하세요'
                ]
            },
            '전골류': {
                'foods': ['곱창전골'],
                'tips': [
                    '다양한 재료가 보이도록 촬영하세요',
                    '국물과 건더기가 함께 보이도록 하세요'
                ]
            },
            '밥류': {
                'foods': ['김치볶음밥', '잡곡밥'],
                'tips': [
                    '밥의 질감과 색깔이 보이도록 촬영하세요',
                    '함께 들어간 재료들이 보이도록 하세요'
                ]
            },
            '떡류': {
                'foods': ['꿀떡'],
                'tips': [
                    '떡의 모양과 색깔이 선명하게 보이도록 촬영하세요',
                    '꿀이나 시럽이 있다면 함께 보이도록 하세요'
                ]
            },
            '나물/반찬류': {
                'foods': ['시금치나물', '배추김치'],
                'tips': [
                    '나물의 색깔과 질감이 보이도록 촬영하세요',
                    '양념이 잘 보이도록 하세요'
                ]
            }
        }
    
    @staticmethod
    def get_troubleshooting_guide() -> Dict:
        """문제 해결 가이드"""
        return {
            'common_issues': {
                '음식이 인식되지 않아요': [
                    '지원되는 11가지 한식인지 확인해보세요',
                    '음식이 선명하게 보이는지 확인하세요',
                    '다른 각도에서 촬영해보세요'
                ],
                '신뢰도가 낮아요': [
                    '조명을 개선해보세요',
                    '배경을 단순하게 만들어보세요',
                    '음식에 더 가까이 다가가서 촬영해보세요'
                ],
                '잘못된 음식으로 인식돼요': [
                    '비슷한 모양의 다른 음식일 수 있습니다',
                    '수동으로 올바른 음식을 선택해주세요',
                    '더 특징적인 부분이 보이도록 촬영해보세요'
                ]
            },
            'best_practices': [
                '자연광 아래에서 촬영하세요',
                '음식을 중앙에 배치하세요',
                '45도 각도에서 촬영하면 좋습니다',
                '배경은 흰색이나 단색으로 하세요',
                '음식의 특징적인 부분이 잘 보이도록 하세요'
            ]
        }

def get_classification_help() -> Dict:
    """분류 도움말 전체 반환"""
    guide_generator = ClassificationGuideGenerator()
    
    return {
        'supported_foods': guide_generator.get_supported_foods_guide(),
        'troubleshooting': guide_generator.get_troubleshooting_guide(),
        'photography_tips': ClassificationErrorHandler.generate_photography_tips(),
        'contact_info': {
            'message': '계속 문제가 발생하면 수동으로 음식을 선택해주세요.',
            'fallback_action': 'manual_selection'
        }
    }