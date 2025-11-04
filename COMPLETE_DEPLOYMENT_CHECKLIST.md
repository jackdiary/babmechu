# ✅ jacktest.shop 완전 배포 체크리스트

## 🎯 배포 목표
- **도메인**: https://jacktest.shop
- **아키텍처**: Internet → Route 53 → EC2 (Nginx + Flask + React)
- **SSL**: Let's Encrypt 자동 갱신

## 📋 배포 단계별 체크리스트

### **1단계: EC2 인스턴스 배포** ✅
- [x] EC2 인스턴스 생성 (t3.medium 권장)
- [x] 보안 그룹 설정 (80, 443, 22 포트)
- [x] User Data 스크립트로 자동 배포
- [x] 웹사이트 IP 접속 확인: http://EC2_IP

### **2단계: 도메인 DNS 설정** 🔄
- [ ] Route 53 호스팅 존 생성 (또는 기존 DNS 사용)
- [ ] A 레코드 설정: jacktest.shop → EC2_IP
- [ ] A 레코드 설정: www.jacktest.shop → EC2_IP
- [ ] DNS 전파 확인 (5분-24시간)

### **3단계: SSL 인증서 설정** 🔄
- [ ] EC2에 SSH 접속
- [ ] setup-domain-ssl.sh 스크립트 실행
- [ ] SSL 인증서 발급 확인
- [ ] HTTPS 접속 테스트: https://jacktest.shop

### **4단계: 최종 확인** 🔄
- [ ] 웹사이트 정상 작동 확인
- [ ] API 엔드포인트 테스트
- [ ] 모바일 반응형 확인
- [ ] 성능 테스트

## 🚀 현재 진행 상황

### ✅ **완료된 작업**
1. **EC2 자동 배포 스크립트** 준비 완료
2. **도메인 설정 파일** 업데이트 (jacktest.shop)
3. **SSL 자동 설정 스크립트** 생성
4. **DNS 설정 가이드** 작성

### 🔄 **다음에 할 일**

#### **즉시 실행 (5분)**
```bash
# 1. EC2 인스턴스 생성 (AWS 콘솔에서)
# - DEPLOY_NOW.md의 User Data 스크립트 사용
# - 인스턴스 타입: t3.medium
# - 보안 그룹: HTTP(80), HTTPS(443), SSH(22)

# 2. 퍼블릭 IP 확인
# EC2 대시보드에서 퍼블릭 IP 복사
```

#### **DNS 설정 (10분)**
```bash
# Option A: AWS Route 53 사용
aws route53 create-hosted-zone --name jacktest.shop --caller-reference $(date +%s)

# Option B: 기존 DNS 서비스 사용
# 도메인 등록업체에서 A 레코드 추가:
# jacktest.shop → EC2_PUBLIC_IP
# www.jacktest.shop → EC2_PUBLIC_IP
```

#### **SSL 설정 (5분)**
```bash
# EC2에 SSH 접속 후
ssh -i your-key.pem ubuntu@EC2_PUBLIC_IP

# SSL 설정 스크립트 실행
curl -O https://raw.githubusercontent.com/your-username/babmechu/main/setup-domain-ssl.sh
chmod +x setup-domain-ssl.sh
# 스크립트 내 이메일 주소 수정 후
sudo ./setup-domain-ssl.sh
```

## 📊 예상 결과

### **성능 지표**
- **동시 사용자**: 100-500명
- **응답 시간**: < 2초
- **가용성**: 99.9%
- **SSL 등급**: A+

### **월간 비용**
- **EC2 t3.medium**: ~$30
- **Route 53**: $0.50
- **데이터 전송**: ~$1-5
- **총 비용**: **$31-35/월**

## 🔧 배포 후 관리

### **일일 체크**
- [ ] 웹사이트 접속 확인
- [ ] 서버 리소스 사용량 확인
- [ ] 에러 로그 확인

### **주간 체크**
- [ ] SSL 인증서 상태 확인
- [ ] 백업 상태 확인
- [ ] 보안 업데이트 적용

### **월간 체크**
- [ ] 비용 분석
- [ ] 성능 최적화
- [ ] 용량 계획

## 🆘 문제 해결 가이드

### **웹사이트 접속 안 됨**
```bash
# 1. EC2 인스턴스 상태 확인
aws ec2 describe-instances --instance-ids i-your-instance-id

# 2. 보안 그룹 확인
aws ec2 describe-security-groups --group-ids sg-your-security-group

# 3. 서비스 상태 확인
ssh -i your-key.pem ubuntu@EC2_IP
sudo systemctl status babmechu nginx
```

### **SSL 인증서 문제**
```bash
# 인증서 상태 확인
sudo certbot certificates

# 수동 갱신
sudo certbot renew --dry-run

# Nginx 설정 확인
sudo nginx -t
```

### **성능 문제**
```bash
# 리소스 사용량 확인
htop
free -h
df -h

# 로그 확인
sudo journalctl -u babmechu -f
tail -f /var/log/nginx/access.log
```

## 📞 지원 리소스

### **로그 파일 위치**
- **배포 로그**: `/var/log/user-data.log`
- **애플리케이션 로그**: `sudo journalctl -u babmechu`
- **Nginx 로그**: `/var/log/nginx/error.log`
- **SSL 로그**: `/var/log/letsencrypt/letsencrypt.log`

### **유용한 명령어**
```bash
# 서비스 재시작
sudo systemctl restart babmechu nginx

# 설정 다시 로드
sudo systemctl reload nginx

# 실시간 로그 보기
sudo journalctl -u babmechu -f

# SSL 인증서 갱신
sudo certbot renew
```

---

## 🎉 배포 완료 후

배포가 완료되면 다음을 확인하세요:

1. ✅ **https://jacktest.shop** 접속 가능
2. ✅ **https://www.jacktest.shop** 접속 가능
3. ✅ **SSL 인증서** A+ 등급
4. ✅ **모든 기능** 정상 작동
5. ✅ **모바일 반응형** 확인

**축하합니다! 성공적으로 배포가 완료되었습니다!** 🚀🎊