# 밥메추 (Korean Food Nutrition Recommendation System)

AI 기반 한국 음식 영양 분석 및 추천 시스템

##  프로젝트 개요

밥메추는 사용자가 업로드한 음식 이미지를 AI로 분석하여 영양 정보를 제공하고, 개인의 영양 상태에 맞는 음식을 추천하는 웹 애플리케이션입니다.

### 주요 기능
-  AI 기반 음식 이미지 인식 (11가지 한국 음식)
-  개인 맞춤 영양 분석 및 대시보드
-  영양 상태 기반 음식 추천
-  사용자 프로필 관리 (BMR, TDEE 계산)
-  반응형 웹 인터페이스

### 지원 음식 (MVP 버전)
- 감자탕, 삼계탕, 김치찌개, 갈치조림, 곱창전골
- 김치볶음밥, 잡곡밥, 꿀떡, 시금치나물, 배추김치, 콩나물국

##  프로젝트 구조

```
밥메추/
├── 📁 backend/
│   ├── 📁 models/           # 데이터베이스 모델
│   │   ├── user_models.py
│   │   ├── nutrition_models.py
│   │   └── ml_models/       # AI 모델 파일들
│   ├── 📁 routes/           # API 라우트
│   │   ├── profile_routes.py
│   │   ├── classification_routes.py
│   │   ├── intake_routes.py
│   │   ├── nutrition_routes.py
│   │   └── recommendation_routes.py
│   ├── 📁 services/         # 비즈니스 로직
│   │   ├── ml_service.py
│   │   ├── pytorch_service.py
│   │   ├── nutrition_service.py
│   │   └── recommendation_service.py
│   ├── 📁 utils/            # 유틸리티 함수
│   ├── 📁 data/             # 영양 데이터
│   │   └── nutrition/       # JSON 영양 정보 파일들
│   ├── app.py              # Flask 애플리케이션 진입점
│   ├── config.py           # 설정 파일
│   └── requirements.txt    # Python 의존성
├── 📁 frontend/
│   ├── 📁 public/          # 정적 파일
│   ├── 📁 src/
│   │   ├── 📁 components/  # React 컴포넌트
│   │   │   ├── FoodClassification.js
│   │   │   ├── NutritionDashboard.js
│   │   │   ├── Recommendations.js
│   │   │   ├── ProfileSetup.js
│   │   │   └── Navigation.js
│   │   ├── 📁 services/    # API 서비스
│   │   └── App.js          # 메인 React 앱
│   ├── package.json        # Node.js 의존성
│   └── build/              # 빌드된 정적 파일
├── .env                    # 환경 변수
├── .gitignore             # Git 제외 파일 목록
└── README.md              # 프로젝트 문서
```

##  기술 스택

### Backend
- **Framework**: Flask 2.3.3
- **Database**: SQLite (SQLAlchemy ORM)
- **AI/ML**: PyTorch 2.6.0+, ONNX Runtime
- **Image Processing**: Pillow, OpenCV
- **API**: Flask-CORS, RESTful API

### Frontend
- **Framework**: React 19.2.0
- **UI Library**: Material-UI (MUI) 7.3.4
- **Routing**: React Router DOM 7.9.4
- **HTTP Client**: Axios 1.12.2
- **Charts**: MUI X-Charts 8.14.1

##  로컬 개발 환경 설정

### 1. 저장소 클론
```bash
git clone <repository-url>
cd 밥메추
```

### 2. Backend 설정
```bash
# Python 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 설정 입력

# 데이터베이스 초기화
python init_db.py

# Flask 서버 실행
python app.py
```

### 3. Frontend 설정
```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm start
```

### 4. 접속
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### 배포 아키텍처
```
Internet → CloudFront → ALB → EC2 (Frontend + Backend)
                              ↓
                           RDS (PostgreSQL)
```

### 1. EC2 인스턴스 설정
```bash
# EC2 인스턴스 생성 (Ubuntu 22.04 LTS 권장)
# t3.medium 이상 권장 (AI 모델 로딩을 위해)

# 보안 그룹 설정
- HTTP (80)
- HTTPS (443)
- SSH (22)
- Custom TCP (5000) - Backend API
```

### 2. 도메인 및 SSL 설정
```bash
# Route 53에서 jacktest.shop 도메인 설정
# Certificate Manager에서 SSL 인증서 발급
# CloudFront 배포 생성
```

### 3. 데이터베이스 설정 (선택사항)
```bash
# RDS PostgreSQL 인스턴스 생성 (프로덕션 환경)
# 또는 EC2에서 SQLite 사용 (개발/테스트 환경)
```

### 4. 배포 스크립트
```bash
# 프로덕션 환경 변수 설정
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Frontend 빌드
cd frontend
npm run build

# Backend 배포
cd ..
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 5. Nginx 설정
```nginx
server {
    listen 80;
    server_name jacktest.shop;
    
    # Frontend (React build)
    location / {
        root /path/to/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

##  환경 변수 설정

### Backend (.env)
```env
# Flask 설정
SECRET_KEY=your-production-secret-key
FLASK_ENV=production
FLASK_DEBUG=False

# 데이터베이스
DATABASE_URL=sqlite:///korean_food_recommendation.db

# ML 모델 경로
MODEL_PATH=models/ml_models/best_food_model_v2.onnx
LABELS_PATH=models/ml_models/labels.txt

# 영양 데이터 경로
NUTRITION_DATA_PATH=data/nutrition
```

### Frontend (.env)
```env
REACT_APP_API_URL=https://jacktest.shop/api
REACT_APP_ENV=production
```



##  모니터링 및 로깅

### 로그 설정
- Flask 로그: `/var/log/flask/app.log`
- Nginx 로그: `/var/log/nginx/access.log`
- 시스템 로그: `journalctl -u your-app-service`

### 성능 모니터링
- AWS CloudWatch 메트릭 설정
- 애플리케이션 성능 모니터링 (APM) 도구 연동

---

**밥메추** - AI로 더 건강한 식단을 제안합니다! 🍚✨
