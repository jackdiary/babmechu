# 🌐 가비아에서 jacktest.shop DNS 설정 가이드

## 📋 사전 준비
1. ✅ EC2 인스턴스 배포 완료
2. ✅ EC2 퍼블릭 IP 주소 확인 필요
3. ✅ 가비아 계정 로그인 준비

## 🎯 1단계: EC2 퍼블릭 IP 확인

### AWS 콘솔에서 확인:
1. **AWS 콘솔** → **EC2** → **인스턴스**
2. 배포한 인스턴스 선택
3. **퍼블릭 IPv4 주소** 복사 (예: 13.125.123.45)

### 또는 EC2에서 직접 확인:
```bash
# EC2에 SSH 접속 후
curl http://checkip.amazonaws.com/
```

## 🎯 2단계: 가비아 DNS 설정

### 2-1. 가비아 로그인
1. **가비아 홈페이지** 접속: https://www.gabia.com
2. **로그인** 클릭
3. 계정 정보 입력하여 로그인

### 2-2. 도메인 관리 페이지 접속
1. 로그인 후 **My가비아** 클릭
2. **서비스 관리** → **도메인** 클릭
3. **jacktest.shop** 도메인 찾기
4. **관리** 또는 **DNS 관리** 버튼 클릭

### 2-3. DNS 레코드 설정
1. **DNS 설정** 또는 **네임서버 설정** 메뉴 선택
2. **DNS 레코드 관리** 클릭

#### A 레코드 추가 (메인 도메인):
```
호스트명: @
레코드 타입: A
값(IP 주소): YOUR_EC2_PUBLIC_IP
TTL: 300 (기본값)
```

#### A 레코드 추가 (www 서브도메인):
```
호스트명: www
레코드 타입: A  
값(IP 주소): YOUR_EC2_PUBLIC_IP
TTL: 300 (기본값)
```

### 2-4. 설정 저장
1. **추가** 또는 **저장** 버튼 클릭
2. 설정 완료 확인

## 🎯 3단계: DNS 전파 확인 (5분-2시간)

### 3-1. 명령어로 확인:
```bash
# Windows 명령 프롬프트에서
nslookup jacktest.shop
nslookup www.jacktest.shop

# 결과에 EC2 IP가 나오면 성공!
```

### 3-2. 온라인 도구로 확인:
- https://www.whatsmydns.net/#A/jacktest.shop
- 전 세계 DNS 서버에서 전파 상태 확인 가능

### 3-3. 브라우저에서 확인:
- http://jacktest.shop (아직 SSL 설정 전이므로 http)
- http://www.jacktest.shop

## 🎯 4단계: SSL 인증서 설정

DNS 전파가 완료되면 (보통 10분-2시간):

### 4-1. EC2에 SSH 접속:
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### 4-2. SSL 설정 스크립트 실행:
```bash
# 스크립트 다운로드
curl -O https://raw.githubusercontent.com/your-username/babmechu/main/setup-domain-ssl.sh

# 실행 권한 부여
chmod +x setup-domain-ssl.sh

# 이메일 주소 수정
nano setup-domain-ssl.sh
# EMAIL="your-email@example.com" 부분을 실제 이메일로 변경

# 스크립트 실행
sudo ./setup-domain-ssl.sh
```

### 4-3. 수동 SSL 설정 (스크립트 대신):
```bash
# Certbot 설치
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d jacktest.shop -d www.jacktest.shop

# 이메일 입력 및 약관 동의
# 자동으로 Nginx 설정도 업데이트됨
```

## ✅ 최종 확인

### 성공적으로 완료되면:
- ✅ https://jacktest.shop 접속 가능
- ✅ https://www.jacktest.shop 접속 가능  
- ✅ SSL 인증서 A+ 등급
- ✅ 자동 HTTP → HTTPS 리다이렉트

## 🚨 문제 해결

### DNS가 전파되지 않는 경우:
1. **TTL 시간 대기** (최대 24시간, 보통 1-2시간)
2. **DNS 캐시 플러시**:
   ```bash
   # Windows
   ipconfig /flushdns
   
   # Mac  
   sudo dscacheutil -flushcache
   ```

### SSL 인증서 발급 실패:
1. **도메인 접근 확인**:
   ```bash
   curl -I http://jacktest.shop
   ```
2. **방화벽 확인**:
   ```bash
   sudo ufw status
   ```
3. **Nginx 상태 확인**:
   ```bash
   sudo systemctl status nginx
   ```

## 📞 추가 도움

### 가비아 고객센터:
- **전화**: 1588-3233
- **온라인 문의**: 가비아 홈페이지 → 고객센터

### 설정 확인 명령어:
```bash
# DNS 확인
dig jacktest.shop
nslookup jacktest.shop

# SSL 인증서 확인  
sudo certbot certificates

# 웹사이트 상태 확인
curl -I https://jacktest.shop
```

---

## 🎉 완료 후 결과

설정이 완료되면:
1. **https://jacktest.shop** - 메인 사이트
2. **https://www.jacktest.shop** - www 서브도메인
3. **SSL A+ 등급** - 보안 인증서
4. **자동 갱신** - 인증서 만료 걱정 없음

**단계별로 천천히 진행하시면 성공적으로 완료됩니다!** 🚀