from app import db
from datetime import datetime, date
from sqlalchemy import JSON

class DailyIntake(db.Model):
    """일일 영양소 섭취량 추적 모델"""
    __tablename__ = 'daily_intakes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    
    # 9가지 핵심 영양소
    total_calories = db.Column(db.Float, default=0.0)
    total_carbs = db.Column(db.Float, default=0.0)
    total_sugars = db.Column(db.Float, default=0.0)
    total_protein = db.Column(db.Float, default=0.0)
    total_fat = db.Column(db.Float, default=0.0)
    total_saturated_fat = db.Column(db.Float, default=0.0)
    total_cholesterol = db.Column(db.Float, default=0.0)
    total_sodium = db.Column(db.Float, default=0.0)
    total_fiber = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 유니크 제약 조건: 사용자당 하루에 하나의 레코드만
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='unique_user_date'),)

    def __repr__(self):
        return f'<DailyIntake user_id={self.user_id} date={self.date}>'

class MealLog(db.Model):
    """개별 식사 기록 모델"""
    __tablename__ = 'meal_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 음식 정보
    food_name = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Float, nullable=True)  # ML 모델 신뢰도
    
    # 영양 정보 (JSON으로 저장)
    nutrition_data = db.Column(JSON, nullable=False)
    
    # 시간 정보
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.Date, nullable=False, default=date.today)

    def __repr__(self):
        return f'<MealLog {self.food_name} at {self.logged_at}>'

class RecommendationHistory(db.Model):
    """추천 이력 모델"""
    __tablename__ = 'recommendation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 추천 정보
    recommended_foods = db.Column(JSON, nullable=False)  # 추천된 음식 목록
    nutritional_reasoning = db.Column(db.Text, nullable=True)  # 추천 이유
    user_feedback = db.Column(db.String(20), nullable=True)  # 'liked', 'disliked', 'neutral'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RecommendationHistory user_id={self.user_id} at {self.created_at}>'