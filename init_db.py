#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
"""

from app import app, db
from models import *

def init_database():
    """데이터베이스 테이블 생성"""
    with app.app_context():
        # 모든 테이블 생성
        db.create_all()
        print("✅ 데이터베이스 테이블이 성공적으로 생성되었습니다.")

def drop_database():
    """데이터베이스 테이블 삭제 (개발용)"""
    with app.app_context():
        db.drop_all()
        print("🗑️ 모든 데이터베이스 테이블이 삭제되었습니다.")

def reset_database():
    """데이터베이스 리셋 (삭제 후 재생성)"""
    drop_database()
    init_database()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'init':
            init_database()
        elif command == 'drop':
            drop_database()
        elif command == 'reset':
            reset_database()
        else:
            print("사용법: python init_db.py [init|drop|reset]")
    else:
        init_database()