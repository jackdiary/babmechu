"""
프로필 관리 라우트 (세션 기반 MVP)
"""

from flask import Blueprint, request, jsonify, session
from services.profile_service import SessionProfileService

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile/setup', methods=['POST'])
def setup_profile():
    """프로필 초기 설정"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '프로필 데이터가 필요합니다.'}), 400
        
        profile = SessionProfileService.create_profile(data)
        
        return jsonify({
            'message': '프로필이 성공적으로 생성되었습니다.',
            'profile': profile
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '프로필 생성 중 오류가 발생했습니다.'}), 500

@profile_bp.route('/profile', methods=['GET'])
def get_profile():
    """프로필 조회"""
    try:
        profile = SessionProfileService.get_profile()
        
        if not profile:
            return jsonify({'error': '프로필이 존재하지 않습니다.'}), 404
        
        return jsonify({'profile': profile}), 200
        
    except Exception as e:
        return jsonify({'error': '프로필 조회 중 오류가 발생했습니다.'}), 500

@profile_bp.route('/profile', methods=['PUT'])
def update_profile():
    """프로필 업데이트"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '업데이트할 데이터가 필요합니다.'}), 400
        
        profile = SessionProfileService.update_profile(data)
        
        return jsonify({
            'message': '프로필이 성공적으로 업데이트되었습니다.',
            'profile': profile
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': '프로필 업데이트 중 오류가 발생했습니다.'}), 500

@profile_bp.route('/profile/check', methods=['GET'])
def check_profile():
    """프로필 존재 여부 확인"""
    try:
        has_profile = SessionProfileService.has_profile()
        
        return jsonify({
            'has_profile': has_profile,
            'session_id': SessionProfileService.get_session_id()
        }), 200
        
    except Exception as e:
        return jsonify({'error': '프로필 확인 중 오류가 발생했습니다.'}), 500

@profile_bp.route('/profile', methods=['DELETE'])
def delete_profile():
    """프로필 삭제"""
    try:
        SessionProfileService.clear_profile()
        
        return jsonify({'message': '프로필이 성공적으로 삭제되었습니다.'}), 200
        
    except Exception as e:
        return jsonify({'error': '프로필 삭제 중 오류가 발생했습니다.'}), 500