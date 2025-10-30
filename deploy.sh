#!/bin/bash

# 밥메추 AWS 배포 스크립트
# 사용법: ./deploy.sh [production|staging]

set -e

ENVIRONMENT=${1:-production}
DOMAIN="jacktest.shop"

echo "🚀 밥메추 배포 시작 - 환경: $ENVIRONMENT"

# 1. Frontend 빌드
echo "📦 Frontend 빌드 중..."
cd frontend
npm ci
npm run build
cd ..

# 2. Backend 의존성 설치
echo "🐍 Backend 의존성 설치 중..."
pip install -r requirements.txt

# 3. 데이터베이스 마이그레이션
echo "🗄️ 데이터베이스 초기화 중..."
python init_db.py

# 4. 환경 변수 설정
echo "⚙️ 환경 변수 설정 중..."
export FLASK_ENV=$ENVIRONMENT
export FLASK_DEBUG=false

if [ "$ENVIRONMENT" = "production" ]; then
    export DATABASE_URL="sqlite:///korean_food_recommendation.db"
    export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
fi

# 5. 정적 파일 복사
echo "📁 정적 파일 복사 중..."
mkdir -p static
cp -r frontend/build/* static/

# 6. 서비스 시작
echo "🔄 서비스 시작 중..."
if [ "$ENVIRONMENT" = "production" ]; then
    # 프로덕션 환경: Gunicorn 사용
    gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app &
else
    # 개발 환경: Flask 개발 서버 사용
    python app.py &
fi

echo "✅ 배포 완료!"
echo "🌐 접속 URL: https://$DOMAIN"
echo "📊 API 상태: https://$DOMAIN/api/health"