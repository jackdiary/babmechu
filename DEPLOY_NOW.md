# 🚀 지금 바로 배포하기!

## ⚡ 빠른 배포 (5분 완료)

### 1️⃣ AWS EC2 인스턴스 생성

1. **AWS 콘솔** → **EC2** → **인스턴스 시작**
2. **설정값**:
   ```
   이름: babmechu-server
   AMI: Ubuntu Server 22.04 LTS
   인스턴스 유형: t3.medium (또는 t2.micro)
   키 페어: 새로 생성 또는 기존 사용
   스토리지: 20GB
   ```

3. **보안 그룹 설정**:
   ```
   SSH (22): 내 IP
   HTTP (80): 0.0.0.0/0
   HTTPS (443): 0.0.0.0/0
   ```

4. **고급 세부 정보** → **사용자 데이터**에 다음 스크립트 복사:

```bash
#!/bin/bash
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "=== 밥메추 자동 배포 시작 $(date) ==="
set -e

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
git clone https://github.com/your-username/babmechu.git babmechu
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
CORS_ORIGINS=http://localhost:3000
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
    server_name _;
    
    client_max_body_size 16M;
    
    location / {
        root /home/ubuntu/babmechu/frontend/build;
        try_files $uri $uri/ /index.html;
        
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
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
ExecStart=/home/ubuntu/babmechu/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 --timeout 120 app:app
Restart=always
RestartSec=3

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

# 스왑 파일 생성
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
chown ubuntu:ubuntu /home/ubuntu/deployment-complete.txt

echo "=== 밥메추 자동 배포 완료 ==="
echo "웹사이트 접속: http://$(curl -s http://checkip.amazonaws.com/)"
```

5. **인스턴스 시작** 클릭!

### 2️⃣ 배포 완료 확인 (5-10분 후)

1. **EC2 대시보드**에서 인스턴스 상태가 "실행 중"인지 확인
2. **퍼블릭 IP 주소** 복사
3. 브라우저에서 `http://YOUR-EC2-IP` 접속
4. 밥메추 웹사이트가 로드되면 **배포 성공!** 🎉

### 3️⃣ 문제 해결 (필요시)

배포가 안 되면 EC2에 SSH 접속해서 확인:

```bash
# SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 배포 로그 확인
tail -f /var/log/user-data.log

# 서비스 상태 확인
sudo systemctl status babmechu
sudo systemctl status nginx
```

## 🎯 다음 단계 (선택사항)

### 도메인 연결
1. **Route 53**에서 호스팅 존 생성
2. **A 레코드**를 EC2 IP로 설정
3. **SSL 인증서** 설정 (Let's Encrypt)

### 모니터링 설정
1. **CloudWatch** 에이전트 설치
2. **로그 모니터링** 설정
3. **알람** 설정

---

## 💰 예상 비용
- **t3.medium**: ~$30/월
- **t2.micro** (프리티어): 첫 12개월 무료

## 🆘 도움이 필요하면
- 배포 로그: `/var/log/user-data.log`
- 애플리케이션 로그: `sudo journalctl -u babmechu -f`
- Nginx 로그: `/var/log/nginx/error.log`

**지금 바로 배포를 시작하세요!** 🚀