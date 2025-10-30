from app import db
from datetime import datetime
from sqlalchemy import JSON

class User(db.Model):
    """사용자 기본 정보 모델 (MVP에서는 세션 기반으로 사용하지 않지만 향후 확장용)"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    dietary_restrictions = db.relationship('DietaryRestriction', backref='user', cascade='all, delete-orphan')
    daily_intakes = db.relationship('DailyIntake', backref='user', cascade='all, delete-orphan')
    meal_logs = db.relationship('MealLog', backref='user', cascade='all, delete-orphan')
    recommendation_history = db.relationship('RecommendationHistory', backref='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

class UserProfile(db.Model):
    """사용자 프로필 정보 모델"""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 기본 신체 정보
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)  # cm
    weight = db.Column(db.Float, nullable=False)  # kg
    gender = db.Column(db.String(1), nullable=False)  # 'M' or 'F'
    
    # 활동 및 목표
    activity_level = db.Column(db.String(20), nullable=False)  # 'low', 'moderate', 'high'
    goal = db.Column(db.String(20), nullable=False)  # 'lose', 'maintain', 'gain'
    
    # 계산된 값들
    bmr = db.Column(db.Float, nullable=True)  # 기초대사율
    tdee = db.Column(db.Float, nullable=True)  # 총 일일 에너지 소비량
    
    # 일일 권장 영양소 (JSON으로 저장)
    daily_nutrition_targets = db.Column(JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserProfile user_id={self.user_id}>'

class DietaryRestriction(db.Model):
    """사용자 식단 제한사항 모델"""
    __tablename__ = 'dietary_restrictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    restriction_type = db.Column(db.String(50), nullable=False)  # 'allergy', 'preference', 'diet_type'
    value = db.Column(db.String(100), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DietaryRestriction {self.restriction_type}: {self.value}>'