from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)

# 설정
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///korean_food_recommendation.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 세션 설정
app.config['SESSION_COOKIE_SECURE'] = False  # 개발 환경에서는 False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24시간

# 확장 초기화
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app, 
     supports_credentials=True,
     origins=['http://localhost:3000', 'http://127.0.0.1:3000'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# 모델 임포트
from models import *

# 라우트 임포트
from routes.profile_routes import profile_bp
from routes.classification_routes import classification_bp
from routes.nutrition_routes import nutrition_bp
from routes.intake_routes import intake_bp
from routes.recommendation_routes import recommendation_bp

# 요청 로깅 미들웨어
@app.before_request
def log_request_info():
    import logging
    logging.info(f'요청: {request.method} {request.url}')
    if request.is_json:
        logging.info(f'요청 데이터: {request.get_json()}')
    logging.info(f'세션 키: {list(session.keys())}')

# 블루프린트 등록
app.register_blueprint(profile_bp, url_prefix='/api')
app.register_blueprint(classification_bp, url_prefix='/api')
app.register_blueprint(nutrition_bp, url_prefix='/api')
app.register_blueprint(intake_bp, url_prefix='/api')
app.register_blueprint(recommendation_bp, url_prefix='/api')

@app.route('/')
def index():
    return jsonify({
        'message': '밥메추 - 밥 메뉴 추천 시스템',
        'version': '1.0.5',
        'status': 'running'
    })

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/api/debug/session')
def debug_session():
    """세션 디버깅용 엔드포인트"""
    return jsonify({
        'session_keys': list(session.keys()),
        'has_daily_intake': 'daily_intake' in session,
        'daily_intake_keys': list(session.get('daily_intake', {}).keys()) if 'daily_intake' in session else [],
        'session_id': request.cookies.get('session')
    })

@app.route('/api/debug/reload-nutrition')
def reload_nutrition_data():
    """영양 데이터 다시 로드"""
    from services.nutrition_data_service import get_nutrition_data_service
    service = get_nutrition_data_service()
    success = service.reload_nutrition_data()
    cache_info = service.get_cache_info()
    
    return jsonify({
        'success': success,
        'cache_info': cache_info,
        'available_foods': service.get_available_foods()
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)