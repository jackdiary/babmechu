"""
업로드 관련 유틸리티
"""

from typing import Dict, Optional, Tuple
import os
import hashlib
from datetime import datetime
import logging

class UploadTracker:
    """업로드 추적기 (세션 기반)"""
    
    @staticmethod
    def track_upload_attempt(file_info: Dict, result: Dict, session) -> str:
        """
        업로드 시도 추적
        
        Args:
            file_info: 파일 정보
            result: 분류 결과
            session: Flask 세션
            
        Returns:
            업로드 ID
        """
        if 'upload_history' not in session:
            session['upload_history'] = []
        
        upload_id = _generate_upload_id(file_info)
        
        upload_record = {
            'upload_id': upload_id,
            'timestamp': datetime.now().isoformat(),
            'file_info': file_info,
            'classification_result': result,
            'status': result.get('status', 'unknown')
        }
        
        session['upload_history'].insert(0, upload_record)
        
        # 최대 50개까지만 보관
        if len(session['upload_history']) > 50:
            session['upload_history'] = session['upload_history'][:50]
        
        session.modified = True
        return upload_id
    
    @staticmethod
    def get_upload_history(session, limit: int = 10) -> list:
        """업로드 히스토리 조회"""
        if 'upload_history' not in session:
            return []
        
        return session['upload_history'][:limit]
    
    @staticmethod
    def get_recent_failures(session, limit: int = 5) -> list:
        """최근 실패한 업로드 조회"""
        if 'upload_history' not in session:
            return []
        
        failures = [
            record for record in session['upload_history']
            if record.get('status') in ['low_confidence', 'no_predictions', 'error']
        ]
        
        return failures[:limit]
    
    @staticmethod
    def get_upload_statistics(session) -> Dict:
        """업로드 통계"""
        if 'upload_history' not in session:
            return {
                'total_uploads': 0,
                'successful_uploads': 0,
                'failed_uploads': 0,
                'success_rate': 0.0
            }
        
        history = session['upload_history']
        total = len(history)
        
        successful = sum(1 for record in history 
                        if record.get('status') == 'confident')
        
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0
        
        return {
            'total_uploads': total,
            'successful_uploads': successful,
            'failed_uploads': failed,
            'success_rate': round(success_rate, 1)
        }

class ReuploadHelper:
    """재업로드 도우미"""
    
    @staticmethod
    def analyze_previous_failures(session) -> Dict:
        """이전 실패 분석"""
        failures = UploadTracker.get_recent_failures(session)
        
        if not failures:
            return {
                'has_failures': False,
                'message': '이전 실패 기록이 없습니다.'
            }
        
        # 실패 패턴 분석
        failure_types = {}
        for failure in failures:
            status = failure.get('status', 'unknown')
            failure_types[status] = failure_types.get(status, 0) + 1
        
        # 가장 흔한 실패 유형
        most_common_failure = max(failure_types.items(), key=lambda x: x[1])
        
        # 개선 제안 생성
        suggestions = _get_improvement_suggestions(most_common_failure[0])
        
        return {
            'has_failures': True,
            'total_failures': len(failures),
            'failure_types': failure_types,
            'most_common_failure': most_common_failure[0],
            'suggestions': suggestions
        }
    
    @staticmethod
    def get_reupload_guidance(previous_result: Dict) -> Dict:
        """재업로드 가이드"""
        if not previous_result:
            return {
                'message': '이전 결과가 없습니다.',
                'suggestions': ['새로운 이미지를 업로드해보세요.']
            }
        
        status = previous_result.get('status', 'unknown')
        
        guidance = {
            'low_confidence': {
                'message': '이전 업로드의 신뢰도가 낮았습니다.',
                'suggestions': [
                    '더 선명한 이미지로 다시 시도해보세요',
                    '조명을 개선해보세요',
                    '음식이 중앙에 오도록 촬영해보세요',
                    '배경을 단순하게 만들어보세요'
                ]
            },
            'no_predictions': {
                'message': '이전 업로드에서 음식을 인식하지 못했습니다.',
                'suggestions': [
                    '지원되는 17가지 한식인지 확인해보세요',
                    '음식이 명확하게 보이는 각도로 촬영해보세요',
                    '다른 음식과 함께 있다면 따로 촬영해보세요'
                ]
            },
            'error': {
                'message': '이전 업로드에서 오류가 발생했습니다.',
                'suggestions': [
                    '이미지 파일 형식을 확인해보세요 (JPG, PNG, WEBP)',
                    '파일 크기를 확인해보세요 (16MB 이하)',
                    '다른 이미지로 시도해보세요'
                ]
            }
        }
        
        return guidance.get(status, {
            'message': '다시 시도해보세요.',
            'suggestions': ['이미지 품질을 개선해보세요.']
        })

def _generate_upload_id(file_info: Dict) -> str:
    """업로드 ID 생성"""
    # 파일명, 크기, 시간을 조합하여 해시 생성
    content = f"{file_info.get('filename', '')}{file_info.get('size', 0)}{datetime.now().isoformat()}"
    return hashlib.md5(content.encode()).hexdigest()[:12]

def _get_improvement_suggestions(failure_type: str) -> list:
    """실패 유형별 개선 제안"""
    suggestions_map = {
        'low_confidence': [
            '조명을 개선하세요 (자연광 권장)',
            '음식에 더 가까이 다가가서 촬영하세요',
            '배경을 단순하게 만드세요',
            '음식의 특징적인 부분이 잘 보이도록 하세요'
        ],
        'no_predictions': [
            '지원되는 음식 목록을 확인하세요',
            '음식 전체가 프레임에 들어오도록 하세요',
            '다른 각도에서 촬영해보세요',
            '음식만 단독으로 촬영하세요'
        ],
        'error': [
            '지원되는 파일 형식을 사용하세요 (JPG, PNG, WEBP)',
            '파일 크기를 줄여보세요 (16MB 이하)',
            '이미지가 손상되지 않았는지 확인하세요'
        ]
    }
    
    return suggestions_map.get(failure_type, [
        '이미지 품질을 개선해보세요',
        '다른 이미지로 시도해보세요'
    ])

def get_upload_best_practices() -> Dict:
    """업로드 모범 사례"""
    return {
        'preparation': [
            '음식을 잘 보이는 위치에 배치하세요',
            '배경을 정리하고 단순하게 만드세요',
            '충분한 조명을 확보하세요'
        ],
        'photography': [
            '음식을 화면 중앙에 배치하세요',
            '45도 각도에서 촬영하면 좋습니다',
            '음식 전체가 프레임에 들어오도록 하세요',
            '초점을 음식에 맞추세요'
        ],
        'technical': [
            'JPG, PNG, WEBP 형식을 사용하세요',
            '파일 크기는 16MB 이하로 유지하세요',
            '최소 224x224 픽셀 이상의 해상도를 권장합니다'
        ],
        'troubleshooting': [
            '인식이 안 되면 다른 각도로 시도하세요',
            '신뢰도가 낮으면 조명을 개선하세요',
            '계속 실패하면 수동 선택을 이용하세요'
        ]
    }