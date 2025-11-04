# 🌐 jacktest.shop 도메인 DNS 설정 가이드

## 📋 현재 상황
- ✅ EC2 인스턴스 배포 완료
- ✅ 도메인: `jacktest.shop` 보유
- 🎯 목표: 도메인을 EC2에 연결

## 🚀 DNS 설정 방법

### **Option A: AWS Route 53 사용 (추천)**

#### 1️⃣ Route 53 호스팅 존 생성
```bash
# AWS CLI로 호스팅 존 생성
aws route53 create-hosted-zone \
    --name jacktest.shop \
    --caller-reference $(date +%s) \
    --hosted-zone-config Comment="Babmechu hosting zone"
```

#### 2️⃣ 네임서버 확인
```bash
# 생성된 네임서버 확인
aws route53 get-hosted-zone --id YOUR_ZONE_ID
```

#### 3️⃣ 도메인 등록업체에서 네임서버 변경
도메인을 구매한 곳(가비아, 후이즈, GoDaddy 등)에서:
1. 도메인 관리 페이지 접속
2. 네임서버를 Route 53 네임서버로 변경:
   ```
   ns-xxx.awsdns-xx.com
   ns-xxx.awsdns-xx.co.uk
   ns-xxx.awsdns-xx.net
   ns-xxx.awsdns-xx.org
   ```

#### 4️⃣ A 레코드 생성
```bash
# EC2 퍼블릭 IP 확인
EC2_IP=$(curl -s http://checkip.amazonaws.com/)

# A 레코드 생성
aws route53 change-resource-record-sets \
    --hosted-zone-id YOUR_ZONE_ID \
    --change-batch '{
        "Changes": [
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "jacktest.shop",
                    "Type": "A",
                    "TTL": 300,
                    "ResourceRecords": [{"Value": "'$EC2_IP'"}]
                }
            },
            {
                "Action": "CREATE",
                "ResourceRecordSet": {
                    "Name": "www.jacktest.shop",
                    "Type": "A",
                    "TTL": 300,
                    "ResourceRecords": [{"Value": "'$EC2_IP'"}]
                }
            }
        ]
    }'
```

### **Option B: 기존 DNS 서비스 사용**

도메인 등록업체의 DNS 관리에서:

1. **A 레코드 추가**:
   ```
   호스트명: @
   타입: A
   값: YOUR_EC2_PUBLIC_IP
   TTL: 300
   ```

2. **www 서브도메인 추가**:
   ```
   호스트명: www
   타입: A
   값: YOUR_EC2_PUBLIC_IP
   TTL: 300
   ```

## 🔧 EC2에서 SSL 설정

DNS 설정 완료 후 (전파 시간: 5분-24시간), EC2에서 SSL 설정:

### 1️⃣ EC2에 SSH 접속
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### 2️⃣ 도메인 및 SSL 설정 스크립트 실행
```bash
# 스크립트 다운로드
curl -O https://raw.githubusercontent.com/your-username/babmechu/main/setup-domain-ssl.sh

# 실행 권한 부여
chmod +x setup-domain-ssl.sh

# 이메일 주소 수정 (스크립트 내부)
nano setup-domain-ssl.sh
# EMAIL="your-email@example.com" 부분을 실제 이메일로 변경

# 스크립트 실행
sudo ./setup-domain-ssl.sh
```

### 3️⃣ 수동 SSL 설정 (스크립트 대신)
```bash
# Certbot 설치
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d jacktest.shop -d www.jacktest.shop

# 자동 갱신 설정
sudo crontab -e
# 다음 라인 추가: 0 12 * * * /usr/bin/certbot renew --quiet
```

## ✅ 설정 완료 확인

### 1️⃣ DNS 전파 확인
```bash
# 도메인 DNS 확인
nslookup jacktest.shop
dig jacktest.shop

# 온라인 도구 사용
# https://www.whatsmydns.net/#A/jacktest.shop
```

### 2️⃣ 웹사이트 접속 테스트
- **HTTP**: http://jacktest.shop
- **HTTPS**: https://jacktest.shop
- **WWW**: https://www.jacktest.shop

### 3️⃣ SSL 인증서 확인
```bash
# 인증서 상태 확인
sudo certbot certificates

# SSL 테스트
curl -I https://jacktest.shop
```

## 🚨 문제 해결

### DNS가 전파되지 않는 경우
```bash
# DNS 캐시 플러시 (로컬)
# Windows: ipconfig /flushdns
# Mac: sudo dscacheutil -flushcache
# Linux: sudo systemctl restart systemd-resolved
```

### SSL 인증서 발급 실패
```bash
# 도메인 접근 가능 여부 확인
curl -I http://jacktest.shop

# Nginx 설정 확인
sudo nginx -t
sudo systemctl status nginx

# 방화벽 확인
sudo ufw status
```

### 502 Bad Gateway 에러
```bash
# 백엔드 서비스 확인
sudo systemctl status babmechu
sudo journalctl -u babmechu -f

# 포트 확인
sudo ss -tlnp | grep :5000
```

## 📊 예상 시간

- **DNS 설정**: 5분
- **DNS 전파**: 5분-24시간 (보통 1-2시간)
- **SSL 설정**: 2-5분
- **총 소요 시간**: 30분-24시간

## 💰 추가 비용

- **Route 53 호스팅 존**: $0.50/월
- **DNS 쿼리**: $0.40/백만 쿼리
- **SSL 인증서**: 무료 (Let's Encrypt)

---

## 🎯 다음 단계

1. ✅ DNS 설정 완료
2. ✅ SSL 인증서 설정 완료
3. 🔄 백업 전략 수립
4. 📊 모니터링 설정
5. 🚀 성능 최적화

**성공적인 도메인 연결을 위해 단계별로 진행하세요!** 🌐