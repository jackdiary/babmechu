"""
세션 기반 사용자 프로필 관리 서비스 (MVP)
"""

from flask import session
from typing import Dict, Optional
import uuid

class SessionProfileService:
    """세션 기반 사용자 프로필 관리"""
    
    @staticmethod
    def get_session_id() -> str:
        """세션 ID 생성 또는 조회"""
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        return session['session_id']
    
    @staticmethod
    def create_profile(profile_data: Dict) -> Dict:
        """프로필 생성"""
        session_id = SessionProfileService.get_session_id()
        
        # 필수 필드 검증
        required_fields = ['age', 'height', 'weight', 'gender', 'activity_level']
        for field in required_fields:
            if field not in profile_data:
                raise ValueError(f"필수 필드가 누락되었습니다: {field}")
        
        # 프로필 데이터 세션에 저장
        session['profile'] = {
            'age': int(profile_data['age']),
            'height': float(profile_data['height']),
            'weight': float(profile_data['weight']),
            'gender': profile_data['gender'],
            'activity_level': profile_data['activity_level'],
            'goal': profile_data.get('goal', 'maintain'),
            'dietary_restrictions': profile_data.get('dietary_restrictions', [])
        }
        
        # BMR/TDEE 계산
        from services.nutrition_service import NutritionCalculatorService
        calculator = NutritionCalculatorService()
        
        bmr = calculator.calculate_bmr(
            session['profile']['age'],
            session['profile']['height'],
            session['profile']['weight'],
            session['profile']['gender']
        )
        
        tdee = calculator.calculate_tdee(bmr, session['profile']['activity_level'])
        
        # 일일 영양소 목표 계산
        nutrition_targets = calculator.calculate_daily_nutrition_targets(
            tdee, session['profile']['goal']
        )
        
        session['profile']['bmr'] = bmr
        session['profile']['tdee'] = tdee
        session['profile']['nutrition_targets'] = nutrition_targets
        
        return session['profile']
    
    @staticmethod
    def get_profile() -> Optional[Dict]:
        """프로필 조회"""
        return session.get('profile')
    
    @staticmethod
    def update_profile(profile_data: Dict) -> Dict:
        """프로필 업데이트"""
        current_profile = SessionProfileService.get_profile()
        if not current_profile:
            raise ValueError("프로필이 존재하지 않습니다. 먼저 프로필을 생성해주세요.")
        
        # 업데이트할 필드들 적용
        for key, value in profile_data.items():
            if key in ['age', 'height', 'weight', 'gender', 'activity_level', 'goal']:
                current_profile[key] = value
        
        # BMR/TDEE 재계산
        from services.nutrition_service import NutritionCalculatorService
        calculator = NutritionCalculatorService()
        
        bmr = calculator.calculate_bmr(
            current_profile['age'],
            current_profile['height'],
            current_profile['weight'],
            current_profile['gender']
        )
        
        tdee = calculator.calculate_tdee(bmr, current_profile['activity_level'])
        
        nutrition_targets = calculator.calculate_daily_nutrition_targets(
            tdee, current_profile['goal']
        )
        
        current_profile['bmr'] = bmr
        current_profile['tdee'] = tdee
        current_profile['nutrition_targets'] = nutrition_targets
        
        session['profile'] = current_profile
        return current_profile
    
    @staticmethod
    def has_profile() -> bool:
        """프로필 존재 여부 확인"""
        return 'profile' in session and session['profile'] is not None
    
    @staticmethod
    def clear_profile():
        """프로필 삭제"""
        if 'profile' in session:
            del session['profile']
        if 'daily_intake' in session:
            del session['daily_intake']