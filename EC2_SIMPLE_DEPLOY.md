# 🚀 밥메추 EC2 단순 배포 가이드

## 📋 배포 개요
- **아키텍처**: Internet → Route 53 → EC2 (Nginx + Flask + React)
- **예상 비용**: $30-40/월
- **복잡도**: 낮음
- **관리**: 쉬움

## 🎯 1단계: AWS EC2 인스턴스 생성

### 1.1 EC2 인스턴스 설정
```
AMI: Ubuntu Server 22.04 LTS (Free tier eligible)
Instance Type: t3.medium (권장) 또는 t2.micro (테스트용)
Storage: 20GB gp3 (또는 gp2)
Key Pair: 새로 생성하거나 기존 키 사용
```

### 1.2 보안 그룹 설정
다음 포트들을 열어주세요:
```
SSH (22): 0.0.0.0/0 (또는 본인 IP만)
HTTP (80): 0.0.0.0/0
HTTPS (443): 0.0.0.0/0
Custom TCP (5000): 0.0.0.0/0 (개발/디버깅용)
```

### 1.3 User Data 스크립트 입력
EC2 인스턴스 생성 시 "Advanced Details" → "User data"에 다음 내용을 복사해서 붙여넣으세요:

```bash
#!/bin/bash
# 자동 배포 스크립트 다운로드 및 실행
cd /tmp
curl -O https://raw.githubusercontent.com/your-username/babmechu/main/complete-auto-deploy.sh
chmod +x complete-auto-deploy.sh
./complete-auto-deploy.sh
```

**또는** `complete-auto-deploy.sh` 파일의 전체 내용을 복사해서 붙여넣으세요.

## 🎯 2단계: 도메인 설정 (선택사항)

### 2.1 Route 53 호스팅 존 생성
```bash
# AWS CLI로 호스팅 존 생성
aws route53 create-hosted-zone --name your-domain.com --caller-reference $(date +%s)
```

### 2.2 DNS 레코드 추가
```bash
# A 레코드 추가 (EC2 퍼블릭 IP로)
aws route53 change-resource-record-sets --hosted-zone-id YOUR_ZONE_ID --change-batch '{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "your-domain.com",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [{"Value": "YOUR_EC2_PUBLIC_IP"}]
    }
  }]
}'
```

## 🎯 3단계: SSL 인증서 설정 (선택사항)

### 3.1 Let's Encrypt 인증서 발급
EC2에 SSH 접속 후:
```bash
# Certbot 설치
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 자동 갱신 설정
sudo crontab -e
# 다음 라인 추가: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🎯 4단계: 배포 확인

### 4.1 서비스 상태 확인
```bash
# EC2에 SSH 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# 서비스 상태 확인
sudo systemctl status babmechu
sudo systemctl status nginx

# 로그 확인
sudo journalctl -u babmechu -f
tail -f /var/log/user-data.log
```

### 4.2 웹사이트 접속 테스트
- **IP 접속**: http://your-ec2-ip
- **도메인 접속**: http://your-domain.com
- **API 테스트**: http://your-domain.com/api/health

## 🔧 트러블슈팅

### 문제 1: 502 Bad Gateway
```bash
# Backend 서비스 확인
sudo systemctl status babmechu
sudo journalctl -u babmechu -n 50

# 포트 확인
sudo netstat -tlnp | grep :5000
```

### 문제 2: 프론트엔드가 로드되지 않음
```bash
# Nginx 설정 확인
sudo nginx -t
sudo systemctl reload nginx

# 빌드 파일 확인
ls -la /home/ubuntu/babmechu/frontend/build/
```

### 문제 3: 메모리 부족
```bash
# 메모리 사용량 확인
free -h
htop

# 스왑 파일 확인
sudo swapon --show
```

## 📊 비용 예상

### 월간 예상 비용 (서울 리전)
- **EC2 t3.medium**: ~$30
- **Route 53 호스팅 존**: $0.50
- **데이터 전송**: ~$1-5
- **총 예상 비용**: **$31-35/월**

### 비용 절약 팁
- **Reserved Instance**: 1년 약정 시 30% 절약
- **t2.micro**: 프리티어 사용 (첫 12개월 무료)
- **CloudWatch 로그**: 보존 기간 조정

## 🔄 업데이트 방법

### 코드 업데이트
```bash
# EC2에 SSH 접속 후
cd /home/ubuntu/babmechu
git pull origin main

# Backend 재시작
sudo systemctl restart babmechu

# Frontend 재빌드 (필요시)
cd frontend
npm run build
cd ..
sudo systemctl reload nginx
```

## 📞 지원

### 로그 파일 위치
- **배포 로그**: `/var/log/user-data.log`
- **애플리케이션 로그**: `sudo journalctl -u babmechu`
- **Nginx 로그**: `/var/log/nginx/error.log`

### 유용한 명령어
```bash
# 서비스 재시작
sudo systemctl restart babmechu nginx

# 설정 다시 로드
sudo systemctl reload nginx

# 실시간 로그 보기
sudo journalctl -u babmechu -f
```

---

## ✅ 배포 체크리스트

- [ ] EC2 인스턴스 생성 및 보안 그룹 설정
- [ ] User Data 스크립트 실행
- [ ] 웹사이트 접속 확인 (http://ec2-ip)
- [ ] 도메인 설정 (선택사항)
- [ ] SSL 인증서 설정 (선택사항)
- [ ] 백업 전략 수립
- [ ] 모니터링 설정

**성공적인 배포를 위해 단계별로 천천히 진행하세요!** 🎉