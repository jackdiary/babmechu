#!/bin/bash

# jacktest.shop 도메인 연결 및 SSL 설정 스크립트
# EC2 배포 완료 후 실행하는 스크립트

set -e

DOMAIN="jacktest.shop"
EMAIL="9radaz@naver.com"  # 실제 이메일로 변경 필요

echo "=== jacktest.shop 도메인 및 SSL 설정 시작 ==="

# 현재 EC2 퍼블릭 IP 확인
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com/)
echo "현재 EC2 퍼블릭 IP: $PUBLIC_IP"

echo "=== 1단계: Nginx 설정 업데이트 ==="

# Nginx 설정을 도메인용으로 업데이트
sudo tee /etc/nginx/sites-available/babmechu > /dev/null << 'NGINXEOF'
server {
    listen 80;
    server_name jacktest.shop www.jacktest.shop;
    
    # 보안 헤더
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
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

# Nginx 설정 테스트 및 재시작
sudo nginx -t
sudo systemctl reload nginx

echo "=== 2단계: Certbot 설치 ==="

# Certbot 설치
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

echo "=== 3단계: SSL 인증서 발급 ==="

# SSL 인증서 발급 (자동으로 Nginx 설정도 업데이트됨)
sudo certbot --nginx -d jacktest.shop -d www.jacktest.shop --non-interactive --agree-tos --email $EMAIL

echo "=== 4단계: 자동 갱신 설정 ==="

# 자동 갱신 크론잡 설정
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

echo "=== 5단계: 환경변수 업데이트 ==="

# .env 파일 업데이트
cd /home/ubuntu/babmechu
sudo -u ubuntu tee .env > /dev/null << 'ENVEOF'
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///babmechu.db
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
DOMAIN=jacktest.shop
CORS_ORIGINS=https://jacktest.shop,https://www.jacktest.shop,http://localhost:3000
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
ENVEOF

# 서비스 재시작
sudo systemctl restart babmechu

echo "=== 6단계: 방화벽 설정 확인 ==="

# 방화벽 상태 확인
sudo ufw status

echo "=== 설정 완료! ==="
echo ""
echo "🎉 도메인 및 SSL 설정이 완료되었습니다!"
echo ""
echo "✅ 웹사이트 접속: https://jacktest.shop"
echo "✅ www 서브도메인: https://www.jacktest.shop"
echo "✅ SSL 인증서: Let's Encrypt (자동 갱신 설정됨)"
echo ""
echo "📋 다음 단계:"
echo "1. 도메인 DNS를 EC2 IP($PUBLIC_IP)로 설정"
echo "2. https://jacktest.shop 접속 테스트"
echo "3. SSL 인증서 상태 확인: sudo certbot certificates"
echo ""
echo "🔧 문제 해결:"
echo "- Nginx 로그: sudo tail -f /var/log/nginx/error.log"
echo "- 애플리케이션 로그: sudo journalctl -u babmechu -f"
echo "- SSL 인증서 갱신 테스트: sudo certbot renew --dry-run"