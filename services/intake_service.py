"""
세션 기반 섭취량 추적 서비스 (MVP)
"""

from flask import session
from typing import Dict, List, Optional
from datetime import datetime, date
import json

class SessionIntakeService:
    """세션 기반 섭취량 추적 서비스"""
    
    @staticmethod
    def get_today_key() -> str:
        """오늘 날짜 키 생성"""
        return date.today().isoformat()
    
    @staticmethod
    def initialize_daily_intake():
        """일일 섭취량 초기화"""
        today_key = SessionIntakeService.get_today_key()
        
        if 'daily_intake' not in session:
            session['daily_intake'] = {}
            session.modified = True
        
        if today_key not in session['daily_intake']:
            session['daily_intake'][today_key] = {
                'date': today_key,
                'total_nutrition': {
                    'calories': 0.0,
                    'carbohydrates': 0.0,
                    'sugars': 0.0,
                    'protein': 0.0,
                    'fat': 0.0,
                    'saturated_fat': 0.0,
                    'cholesterol': 0.0,
                    'sodium': 0.0,
                    'fiber': 0.0
                },
                'meals': [],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            session.modified = True
            
        import logging
        logging.info(f"일일 섭취량 초기화 완료: {today_key}, 현재 식사 수: {len(session['daily_intake'][today_key]['meals'])}")
    
    @staticmethod
    def log_meal(food_name: str, nutrition_data: Dict, confidence_score: float = None) -> Dict:
        """
        식사 기록
        
        Args:
            food_name: 음식명
            nutrition_data: 영양 데이터
            confidence_score: ML 모델 신뢰도 (선택사항)
            
        Returns:
            기록된 식사 정보
        """
        try:
            if not food_name or not isinstance(food_name, str):
                raise ValueError("유효한 음식명이 필요합니다.")
            
            if not nutrition_data or not isinstance(nutrition_data, dict):
                raise ValueError("유효한 영양 데이터가 필요합니다.")
            
            SessionIntakeService.initialize_daily_intake()
            today_key = SessionIntakeService.get_today_key()
            
            # 현재 식사 개수 확인
            current_meals = session['daily_intake'][today_key]['meals']
            meal_id = len(current_meals) + 1
            
            # 식사 로그 생성
            meal_log = {
                'id': meal_id,
                'food_name': food_name.strip(),
                'nutrition_data': nutrition_data.copy(),
                'confidence_score': confidence_score,
                'logged_at': datetime.now().isoformat()
            }
            
            # 식사 목록에 추가
            session['daily_intake'][today_key]['meals'].append(meal_log)
            
            # 총 영양소 누적
            total_nutrition = session['daily_intake'][today_key]['total_nutrition']
            
            for nutrient, value in nutrition_data.items():
                if nutrient in total_nutrition and isinstance(value, (int, float)):
                    total_nutrition[nutrient] += value
                elif nutrient not in total_nutrition:
                    # 새로운 영양소가 있다면 추가
                    total_nutrition[nutrient] = value if isinstance(value, (int, float)) else 0
            
            # 업데이트 시간 갱신
            session['daily_intake'][today_key]['updated_at'] = datetime.now().isoformat()
            
            # 세션 수정 플래그 설정
            session.modified = True
            
            return meal_log
            
        except Exception as e:
            import logging
            logging.error(f"식사 기록 중 오류: {str(e)}")
            raise
    
    @staticmethod
    def get_daily_intake(target_date: str = None) -> Optional[Dict]:
        """
        일일 섭취량 조회
        
        Args:
            target_date: 조회할 날짜 (YYYY-MM-DD), None이면 오늘
            
        Returns:
            일일 섭취량 데이터 또는 None
        """
        if target_date is None:
            target_date = SessionIntakeService.get_today_key()
        
        if 'daily_intake' not in session:
            return None
        
        return session['daily_intake'].get(target_date)
    
    @staticmethod
    def get_current_totals() -> Dict:
        """현재 일일 총 섭취량 반환"""
        SessionIntakeService.initialize_daily_intake()
        today_key = SessionIntakeService.get_today_key()
        
        return session['daily_intake'][today_key]['total_nutrition'].copy()
    
    @staticmethod
    def get_meal_history(limit: int = 10) -> List[Dict]:
        """
        최근 식사 기록 조회
        
        Args:
            limit: 조회할 최대 개수
            
        Returns:
            식사 기록 리스트
        """
        today_key = SessionIntakeService.get_today_key()
        daily_data = SessionIntakeService.get_daily_intake(today_key)
        
        if not daily_data or 'meals' not in daily_data:
            return []
        
        # 최신순으로 정렬하여 반환
        meals = daily_data['meals']
        return sorted(meals, key=lambda x: x['logged_at'], reverse=True)[:limit]
    
    @staticmethod
    def delete_meal(meal_id: int) -> bool:
        """
        식사 기록 삭제
        
        Args:
            meal_id: 삭제할 식사 ID
            
        Returns:
            삭제 성공 여부
        """
        today_key = SessionIntakeService.get_today_key()
        daily_data = SessionIntakeService.get_daily_intake(today_key)
        
        if not daily_data or 'meals' not in daily_data:
            return False
        
        # 해당 ID의 식사 찾기
        meal_to_delete = None
        for i, meal in enumerate(daily_data['meals']):
            if meal['id'] == meal_id:
                meal_to_delete = daily_data['meals'].pop(i)
                break
        
        if not meal_to_delete:
            return False
        
        # 총 영양소에서 해당 식사 영양소 차감
        total_nutrition = daily_data['total_nutrition']
        meal_nutrition = meal_to_delete['nutrition_data']
        
        for nutrient, value in meal_nutrition.items():
            if nutrient in total_nutrition:
                total_nutrition[nutrient] = max(0, total_nutrition[nutrient] - value)
        
        # 업데이트 시간 갱신
        daily_data['updated_at'] = datetime.now().isoformat()
        session.modified = True
        
        return True
    
    @staticmethod
    def reset_daily_intake(target_date: str = None):
        """
        일일 섭취량 리셋
        
        Args:
            target_date: 리셋할 날짜, None이면 오늘
        """
        if target_date is None:
            target_date = SessionIntakeService.get_today_key()
        
        if 'daily_intake' in session and target_date in session['daily_intake']:
            del session['daily_intake'][target_date]
            session.modified = True
    
    @staticmethod
    def get_intake_summary() -> Dict:
        """섭취량 요약 정보 반환"""
        today_key = SessionIntakeService.get_today_key()
        daily_data = SessionIntakeService.get_daily_intake(today_key)
        
        if not daily_data:
            return {
                'date': today_key,
                'total_meals': 0,
                'total_nutrition': SessionIntakeService._get_empty_nutrition(),
                'last_meal_time': None
            }
        
        meals = daily_data.get('meals', [])
        last_meal_time = None
        
        if meals:
            # 가장 최근 식사 시간
            last_meal_time = max(meal['logged_at'] for meal in meals)
        
        return {
            'date': today_key,
            'total_meals': len(meals),
            'total_nutrition': daily_data['total_nutrition'].copy(),
            'last_meal_time': last_meal_time,
            'created_at': daily_data.get('created_at'),
            'updated_at': daily_data.get('updated_at')
        }
    
    @staticmethod
    def _get_empty_nutrition() -> Dict:
        """빈 영양소 딕셔너리 반환"""
        return {
            'calories': 0.0,
            'carbohydrates': 0.0,
            'sugars': 0.0,
            'protein': 0.0,
            'fat': 0.0,
            'saturated_fat': 0.0,
            'cholesterol': 0.0,
            'sodium': 0.0,
            'fiber': 0.0
        }
    
    @staticmethod
    def cleanup_old_data(days_to_keep: int = 7):
        """
        오래된 섭취 데이터 정리
        
        Args:
            days_to_keep: 보관할 일수
        """
        if 'daily_intake' not in session:
            return
        
        from datetime import timedelta
        cutoff_date = date.today() - timedelta(days=days_to_keep)
        
        dates_to_remove = []
        for date_key in session['daily_intake'].keys():
            try:
                intake_date = date.fromisoformat(date_key)
                if intake_date < cutoff_date:
                    dates_to_remove.append(date_key)
            except ValueError:
                # 잘못된 날짜 형식도 제거
                dates_to_remove.append(date_key)
        
        for date_key in dates_to_remove:
            del session['daily_intake'][date_key]
        
        if dates_to_remove:
            session.modified = True