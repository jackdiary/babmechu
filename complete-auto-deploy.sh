#!/bin/bash

# 밥메추 완전 자동 배포 스크립트 (EC2 User Data용)
# EC2 인스턴스 생성 시 User Data에 이 스크립트를 입력하면 자동으로 배포됩니다.

exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "=== 밥메추 완전 자동 배포 시작 $(date) ==="

# 에러 발생 시 스크립트 중단
set -e

# 변수 설정
PROJECT_DIR="/home/ubuntu/babmechu"
GITHUB_REPO="https://github.com/jackdiary/babmechu.git"
DOMAIN_NAME="your-domain.com"  # 실제 도메인으로 변경 필요

# 시스템 업데이트
apt-get update -y
apt-get upgrade -y

# 필수 패키지 설치
apt-get install -y python3 python3-pip python3-venv nodejs npm nginx git curl wget unzip htop tree

# Node.js 최신 LTS 설치
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
apt-get install -y nodejs

# ubuntu 사용자로 전환하여 작업
sudo -u ubuntu bash << 'EOF'
cd /home/ubuntu

echo "프로젝트 클론 중..."
if [ -d "babmechu" ]; then
    rm -rf babmechu
fi
git clone $GITHUB_REPO babmechu
cd babmechu

echo "Python 가상환경 생성 중..."
python3 -m venv venv
source venv/bin/activate

echo "PyTorch CPU 버전 설치 중..."
pip install --upgrade pip
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cpu

echo "Python 의존성 설치 중..."
pip install -r requirements.txt
pip install gunicorn

echo "환경변수 파일 생성 중..."
cat > .env << 'ENVEOF'
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///babmechu.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
CORS_ORIGINS=http://localhost:3000,https://$DOMAIN_NAME
ENVEOF

echo "프론트엔드 빌드 중..."
cd frontend
npm install --production
npm run build
cd ..

echo "데이터베이스 초기화 중..."
python init_db.py

echo "업로드 디렉토리 생성 중..."
mkdir -p uploads
chmod 755 uploads

EOF

# Nginx 설정
echo "Nginx 설정 중..."
cat > /etc/nginx/sites-available/babmechu << 'NGINXEOF'
server {
    listen 80;
    server_name _ $DOMAIN_NAME www.$DOMAIN_NAME;
    
    # 보안 헤더
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # 파일 업로드 크기 제한
    client_max_body_size 16M;
    
    # Frontend (React build)
    location / {
        root /home/ubuntu/babmechu/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # 캐시 설정
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # 헬스체크
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
NGINXEOF

# Nginx 사이트 활성화
ln -sf /etc/nginx/sites-available/babmechu /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# 시스템 서비스 생성
echo "시스템 서비스 생성 중..."
cat > /etc/systemd/system/babmechu.service << 'SERVICEEOF'
[Unit]
Description=Babmechu Flask App
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/babmechu
Environment="PATH=/home/ubuntu/babmechu/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/home/ubuntu/babmechu/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 50 app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal
SyslogIdentifier=babmechu

[Install]
WantedBy=multi-user.target
SERVICEEOF

# 서비스 시작
systemctl daemon-reload
systemctl start babmechu
systemctl enable babmechu

# 방화벽 설정
ufw --force enable
ufw allow ssh
ufw allow http
ufw allow https

# 로그 로테이션 설정
echo "로그 로테이션 설정 중..."
cat > /etc/logrotate.d/babmechu << 'LOGROTATEEOF'
/var/log/babmechu/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload babmechu
    endscript
}
LOGROTATEEOF

# 로그 디렉토리 생성
mkdir -p /var/log/babmechu
chown ubuntu:ubuntu /var/log/babmechu

# 스왑 파일 생성 (메모리 부족 방지)
echo "스왑 파일 생성 중..."
if [ ! -f /swapfile ]; then
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# 완료 상태 파일 생성
echo "Babmechu deployment completed at $(date)" > /home/ubuntu/deployment-complete.txt
echo "Public IP: $(curl -s http://checkip.amazonaws.com/)" >> /home/ubuntu/deployment-complete.txt
echo "Domain: $DOMAIN_NAME" >> /home/ubuntu/deployment-complete.txt
chown ubuntu:ubuntu /home/ubuntu/deployment-complete.txt

# 서비스 상태 확인
echo "=== 서비스 상태 확인 ==="
systemctl status babmechu --no-pager
systemctl status nginx --no-pager

echo "=== 밥메추 자동 배포 완료 ==="
echo "웹사이트 접속: http://$(curl -s http://checkip.amazonaws.com/)"
echo "도메인 설정 후: http://$DOMAIN_NAME"
echo "배포 로그: /var/log/user-data.log"