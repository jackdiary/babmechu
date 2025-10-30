import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///korean_food_recommendation.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # ML 모델 설정
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/ml_models/keras_model.h5')
    LABELS_PATH = os.getenv('LABELS_PATH', 'models/ml_models/labels.txt')
    
    # 영양 데이터 설정
    NUTRITION_DATA_PATH = os.getenv('NUTRITION_DATA_PATH', 'data/nutrition')
    
    # 세션 설정
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}