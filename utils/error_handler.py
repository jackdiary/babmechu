"""
오류 처리 유틸리티
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from datetime import datetime
import os

class AdminNotificationService:
    """관리자 알림 서비스"""
    
    def __init__(self):
        self.email_enabled = os.getenv('ADMIN_EMAIL_ENABLED', 'false').lower() == 'true'
        self.admin_email = os.getenv('ADMIN_EMAIL', '')
        self.smtp_server = os.getenv('SMTP_SERVER', '')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
    
    def notify_missing_nutrition_data(self, food_name: str, context: Dict = None):
        """영양 데이터 누락 알림"""
        message = f"""
        영양 데이터 누락 알림
        
        음식명: {food_name}
        시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        해당 음식의 영양 데이터 JSON 파일이 누락되었습니다.
        파일 경로: data/nutrition/{food_name}.json
        
        조치 필요: 해당 음식의 영양 데이터를 추가해주세요.
        """
        
        if context:
            message += f"\n추가 정보: {context}"
        
        self._send_notification("영양 데이터 누락", message)
        
        # 로그에도 기록
        logging.warning(f"영양 데이터 누락: {food_name}")
    
    def notify_json_parsing_error(self, file_path: str, error_message: str):
        """JSON 파싱 오류 알림"""
        message = f"""
        JSON 파싱 오류 알림
        
        파일: {file_path}
        시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        오류: {error_message}
        
        조치 필요: JSON 파일의 형식을 확인하고 수정해주세요.
        """
        
        self._send_notification("JSON 파싱 오류", message)
        
        # 로그에도 기록
        logging.error(f"JSON 파싱 오류 {file_path}: {error_message}")
    
    def notify_data_validation_error(self, food_name: str, validation_errors: list):
        """데이터 유효성 검증 오류 알림"""
        message = f"""
        데이터 유효성 검증 오류 알림
        
        음식명: {food_name}
        시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        검증 오류:
        """
        
        for error in validation_errors:
            message += f"- {error}\n"
        
        message += "\n조치 필요: 영양 데이터의 형식과 값을 확인해주세요."
        
        self._send_notification("데이터 유효성 오류", message)
        
        # 로그에도 기록
        logging.error(f"데이터 유효성 오류 {food_name}: {validation_errors}")
    
    def _send_notification(self, subject: str, message: str):
        """실제 알림 전송"""
        # 콘솔 로그 (항상 실행)
        logging.info(f"관리자 알림: {subject}")
        
        # 이메일 전송 (설정된 경우에만)
        if self.email_enabled and self.admin_email:
            try:
                self._send_email(subject, message)
            except Exception as e:
                logging.error(f"이메일 전송 실패: {str(e)}")
    
    def _send_email(self, subject: str, message: str):
        """이메일 전송"""
        if not all([self.smtp_server, self.smtp_username, self.smtp_password, self.admin_email]):
            return
        
        msg = MIMEMultipart()
        msg['From'] = self.smtp_username
        msg['To'] = self.admin_email
        msg['Subject'] = f"[밥메추] {subject}"
        
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.smtp_username, self.smtp_password)
        server.send_message(msg)
        server.quit()

class NutritionDataErrorHandler:
    """영양 데이터 오류 처리기"""
    
    def __init__(self):
        self.notification_service = AdminNotificationService()
        self.error_counts = {}  # 오류 발생 횟수 추적
    
    def handle_missing_data(self, food_name: str) -> Dict:
        """영양 데이터 누락 처리"""
        # 오류 횟수 증가
        self.error_counts[f"missing_{food_name}"] = self.error_counts.get(f"missing_{food_name}", 0) + 1
        
        # 첫 번째 오류이거나 10회마다 알림
        if self.error_counts[f"missing_{food_name}"] == 1 or self.error_counts[f"missing_{food_name}"] % 10 == 0:
            self.notification_service.notify_missing_nutrition_data(
                food_name, 
                {'error_count': self.error_counts[f"missing_{food_name}"]}
            )
        
        # 대체 데이터 생성
        from services.nutrition_data_service import get_nutrition_data_service
        nutrition_service = get_nutrition_data_service()
        fallback_data = nutrition_service.get_fallback_nutrition_data(food_name)
        
        return {
            'status': 'fallback_used',
            'data': fallback_data,
            'message': f'{food_name}의 영양 데이터가 없어 기본값을 사용합니다.'
        }
    
    def handle_parsing_error(self, file_path: str, error: Exception) -> Optional[Dict]:
        """JSON 파싱 오류 처리"""
        error_message = str(error)
        
        # 관리자에게 알림
        self.notification_service.notify_json_parsing_error(file_path, error_message)
        
        # 파일명에서 음식명 추출
        food_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # 대체 데이터 제공
        from services.nutrition_data_service import get_nutrition_data_service
        nutrition_service = get_nutrition_data_service()
        fallback_data = nutrition_service.get_fallback_nutrition_data(food_name)
        
        return {
            'status': 'parsing_error',
            'data': fallback_data,
            'message': f'JSON 파싱 오류로 인해 {food_name}의 기본값을 사용합니다.',
            'error': error_message
        }
    
    def handle_validation_error(self, food_name: str, validation_errors: list) -> Dict:
        """데이터 유효성 검증 오류 처리"""
        # 관리자에게 알림
        self.notification_service.notify_data_validation_error(food_name, validation_errors)
        
        # 대체 데이터 제공
        from services.nutrition_data_service import get_nutrition_data_service
        nutrition_service = get_nutrition_data_service()
        fallback_data = nutrition_service.get_fallback_nutrition_data(food_name)
        
        return {
            'status': 'validation_error',
            'data': fallback_data,
            'message': f'{food_name}의 데이터 검증 오류로 인해 기본값을 사용합니다.',
            'validation_errors': validation_errors
        }
    
    def get_error_statistics(self) -> Dict:
        """오류 통계 반환"""
        return {
            'total_errors': len(self.error_counts),
            'error_details': self.error_counts.copy()
        }

# 전역 인스턴스
_error_handler = None

def get_error_handler() -> NutritionDataErrorHandler:
    """오류 처리기 인스턴스 반환"""
    global _error_handler
    if _error_handler is None:
        _error_handler = NutritionDataErrorHandler()
    return _error_handler