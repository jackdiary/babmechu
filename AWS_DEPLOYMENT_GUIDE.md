# 밥메추 AWS 배포 가이드

## 🎯 배포 목표
- 도메인: `jacktest.shop`
- 환경: AWS EC2 + CloudFront + Route 53
- SSL: AWS Certificate Manager

## 📋 사전 준비사항

### 1. AWS 계정 및 도구
- [ ] AWS 계정 생성 및 결제 정보 등록
- [ ] AWS CLI 설치 및 구성
- [ ] EC2 Key Pair 생성

### 2. 도메인 설정
- [ ] `jacktest.shop` 도메인 소유권 확인
- [ ] Route 53 Hosted Zone 생성

## 🚀 단계별 배포 가이드

### Step 1: EC2 인스턴스 생성

```bash
# 1. EC2 인스턴스 사양
- AMI: Ubuntu Server 22.04 LTS
- Instance Type: t3.medium (최소 권장)
- Storage: 20GB gp3
- Security Group: HTTP(80), HTTPS(443), SSH(22), Custom(5000)

# 2. 인스턴스 접속
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 2: 서버 환경 설정

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y python3-pip python3-venv nodejs npm nginx git

# Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 프로젝트 클론
git clone <your-repository-url> /home/ubuntu/babmechu
cd /home/ubuntu/babmechu
```

### Step 3: 애플리케이션 설정

```bash
# Backend 설정
pip install -r requirements.txt
cp .env.example .env
# .env 파일 편집 (프로덕션 설정)

# Frontend 빌드
cd frontend
npm install
npm run build
cd ..

# 데이터베이스 초기화
python init_db.py
```

### Step 4: Nginx 설정

```bash
# Nginx 설정 파일 생성
sudo nano /etc/nginx/sites-available/babmechu
```

```nginx
server {
    listen 80;
    server_name jacktest.shop www.jacktest.shop;
    
    # Frontend (React build)
    location / {
        root /home/ubuntu/babmechu/frontend/build;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 정적 파일 최적화
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        root /home/ubuntu/babmechu/frontend/build;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Nginx 설정 활성화
sudo ln -s /etc/nginx/sites-available/babmechu /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Step 5: SSL 인증서 설정

```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d jacktest.shop -d www.jacktest.shop

# 자동 갱신 설정
sudo crontab -e
# 다음 라인 추가:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### Step 6: 시스템 서비스 설정

```bash
# Gunicorn 서비스 파일 생성
sudo nano /etc/systemd/system/babmechu.service
```

```ini
[Unit]
Description=Babmechu Flask App
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/babmechu
Environment="PATH=/home/ubuntu/babmechu/venv/bin"
ExecStart=/home/ubuntu/babmechu/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 시작 및 활성화
sudo systemctl daemon-reload
sudo systemctl start babmechu
sudo systemctl enable babmechu
sudo systemctl status babmechu
```

### Step 7: Route 53 DNS 설정

```bash
# AWS CLI로 DNS 레코드 생성
aws route53 change-resource-record-sets --hosted-zone-id YOUR_ZONE_ID --change-batch '{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "jacktest.shop",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [{"Value": "YOUR_EC2_IP"}]
    }
  }]
}'
```

### Step 8: CloudFront 설정 (선택사항)

```bash
# CloudFront 배포 생성 (AWS 콘솔에서)
1. Origin Domain: jacktest.shop
2. Viewer Protocol Policy: Redirect HTTP to HTTPS
3. Allowed HTTP Methods: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
4. Cache Policy: CachingDisabled (API 경로용)
5. Custom SSL Certificate: 선택 (Certificate Manager에서 발급)
```

## 🔧 개발자 작업 체크리스트

### 필수 작업
- [ ] `.env` 파일에 프로덕션 설정 입력
- [ ] `SECRET_KEY` 강력한 값으로 변경
- [ ] 데이터베이스 백업 전략 수립
- [ ] 로그 모니터링 설정

### 권장 작업
- [ ] CloudWatch 모니터링 설정
- [ ] Auto Scaling Group 구성
- [ ] RDS PostgreSQL 마이그레이션
- [ ] S3 정적 파일 호스팅
- [ ] CI/CD 파이프라인 구축

## 🔍 배포 후 확인사항

### 1. 서비스 상태 확인
```bash
# 서비스 상태
sudo systemctl status babmechu
sudo systemctl status nginx

# 로그 확인
sudo journalctl -u babmechu -f
sudo tail -f /var/log/nginx/error.log
```

### 2. API 테스트
```bash
# 헬스체크
curl https://jacktest.shop/api/health

# 음식 분류 테스트 (이미지 파일 필요)
curl -X POST https://jacktest.shop/api/classify \
  -F "image=@test_image.jpg"
```

### 3. 웹사이트 접속 테스트
- https://jacktest.shop 접속 확인
- 모든 페이지 정상 작동 확인
- 모바일 반응형 확인

## 🚨 트러블슈팅

### 일반적인 문제들

#### 1. 502 Bad Gateway
```bash
# Backend 서비스 상태 확인
sudo systemctl status babmechu
sudo journalctl -u babmechu -n 50

# 포트 확인
sudo netstat -tlnp | grep :5000
```

#### 2. SSL 인증서 문제
```bash
# 인증서 상태 확인
sudo certbot certificates

# 수동 갱신
sudo certbot renew --dry-run
```

#### 3. 메모리 부족
```bash
# 메모리 사용량 확인
free -h
htop

# 스왑 파일 생성 (필요시)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📊 모니터링 설정

### CloudWatch 에이전트 설치
```bash
# CloudWatch 에이전트 설치
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# 설정 파일 생성
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### 로그 로테이션 설정
```bash
# logrotate 설정
sudo nano /etc/logrotate.d/babmechu
```

```
/var/log/babmechu/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload babmechu
    endscript
}
```

## 🔄 업데이트 및 배포

### 자동 배포 스크립트
```bash
#!/bin/bash
# update.sh

cd /home/ubuntu/babmechu
git pull origin main

# Backend 업데이트
source venv/bin/activate
pip install -r requirements.txt

# Frontend 빌드
cd frontend
npm install
npm run build
cd ..

# 서비스 재시작
sudo systemctl restart babmechu
sudo systemctl reload nginx

echo "배포 완료!"
```

## 💰 비용 최적화

### 예상 월 비용 (서울 리전)
- EC2 t3.medium: ~$30
- Route 53 Hosted Zone: $0.50
- CloudFront (선택): ~$1-5
- **총 예상 비용: $31-35/월**

### 비용 절약 팁
- Reserved Instance 사용 (1년 약정 시 30% 절약)
- CloudWatch 로그 보존 기간 조정
- 불필요한 스냅샷 정리

---

## 📞 지원

배포 중 문제가 발생하면:
1. 로그 파일 확인
2. 시스템 리소스 확인
3. 네트워크 연결 확인
4. AWS 서비스 상태 페이지 확인

**성공적인 배포를 위해 단계별로 천천히 진행하세요!** 🚀