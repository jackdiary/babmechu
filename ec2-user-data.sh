#!/bin/bash

# EC2 인스턴스 초기 설정 스크립트
# 이 스크립트는 EC2 인스턴스 생성 시 User Data에 입력하여 자동 실행됩니다.

# 로그 파일 설정
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "=== 밥메추 EC2 인스턴스 초기 설정 시작 ==="

# 시스템 업데이트
apt-get update -y
apt-get upgrade -y

# 필수 패키지 설치
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    nginx \
    git \
    curl \
    wget \
    unzip \
    htop \
    tree

# Node.js 최신 LTS 버전 설치
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
apt-get install -y nodejs

# 사용자 디렉토리 생성
mkdir -p /home/ubuntu/apps
chown ubuntu:ubuntu /home/ubuntu/apps

# 로그 디렉토리 생성
mkdir -p /var/log/babmechu
chown ubuntu:ubuntu /var/log/babmechu

# Nginx 기본 사이트 비활성화
rm -f /etc/nginx/sites-enabled/default

# 방화벽 설정 (UFW)
ufw --force enable
ufw allow ssh
ufw allow http
ufw allow https
ufw allow 5000

# 시스템 서비스 활성화
systemctl enable nginx
systemctl start nginx

# 완료 메시지
echo "=== EC2 인스턴스 초기 설정 완료 ==="
echo "인스턴스 준비 완료 시간: $(date)"

# 상태 파일 생성
echo "EC2 setup completed at $(date)" > /home/ubuntu/setup-complete.txt
chown ubuntu:ubuntu /home/ubuntu/setup-complete.txt