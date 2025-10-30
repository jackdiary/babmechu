"""
영양 정보 관련 라우트
"""

from flask import Blueprint, request, jsonify
from services.nutrition_data_service import get_nutrition_data_service
from services.profile_service import SessionProfileService
from services.nutrition_service import NutritionCalculatorService
from utils.nutrition_utils import get_nutrition_display_names, format_nutrition_value
import logging

nutrition_bp = Blueprint('nutrition', __name__)

@nutrition_bp.route('/nutrition/<food_name>', methods=['GET'])
def get_food_nutrition(food_name):
    """특정 음식의 영양 정보 조회"""
    try:
        nutrition_service = get_nutrition_data_service()
        nutrition_data = nutrition_service.get_nutrition_data(food_name)
        
        if not nutrition_data:
            # 대체 데이터 제공
            nutrition_data = nutrition_service.get_fallback_nutrition_data(food_name)
        
        # 사용자 프로필이 있다면 목표 대비 백분율 계산
        profile = SessionProfileService.get_profile()
        percentage_info = None
        
        if profile and 'nutrition_targets' in profile:
            calculator = NutritionCalculatorService()
            percentages = calculator.calculate_nutrition_percentage(
                nutrition_data['nutrition'],
                profile['nutrition_targets']
            )
            percentage_info = percentages
        
        # 표시용 데이터 포맷팅
        display_names = get_nutrition_display_names()
        formatted_nutrition = {}
        
        for nutrient, value in nutrition_data['nutrition'].items():
            formatted_nutrition[nutrient] = {
                'value': value,
                'formatted': format_nutrition_value(nutrient, value),
                'display_name': display_names.get(nutrient, nutrient),
                'percentage': percentage_info.get(nutrient) if percentage_info else None
            }
        
        response_data = {
            'success': True,
            'food_name': nutrition_data['name'],
            'serving_size': nutrition_data['serving_size'],
            'nutrition': formatted_nutrition,
            'is_fallback': nutrition_data.get('is_fallback', False)
        }
        
        if percentage_info:
            response_data['has_user_targets'] = True
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logging.error(f"영양 정보 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@nutrition_bp.route('/nutrition/available', methods=['GET'])
def get_available_foods():
    """사용 가능한 음식 목록 조회"""
    try:
        nutrition_service = get_nutrition_data_service()
        available_foods = nutrition_service.get_available_foods()
        
        return jsonify({
            'success': True,
            'available_foods': sorted(available_foods),
            'total_count': len(available_foods)
        }), 200
        
    except Exception as e:
        logging.error(f"사용 가능한 음식 목록 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@nutrition_bp.route('/nutrition/reload', methods=['POST'])
def reload_nutrition_data():
    """영양 데이터 다시 로딩 (관리자용)"""
    try:
        nutrition_service = get_nutrition_data_service()
        success = nutrition_service.reload_nutrition_data()
        
        if success:
            cache_info = nutrition_service.get_cache_info()
            return jsonify({
                'success': True,
                'message': '영양 데이터가 성공적으로 다시 로드되었습니다.',
                'cache_info': cache_info
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '영양 데이터 로딩에 실패했습니다.'
            }), 500
            
    except Exception as e:
        logging.error(f"영양 데이터 리로딩 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@nutrition_bp.route('/nutrition/cache/info', methods=['GET'])
def get_cache_info():
    """영양 데이터 캐시 정보 조회"""
    try:
        nutrition_service = get_nutrition_data_service()
        cache_info = nutrition_service.get_cache_info()
        
        return jsonify({
            'success': True,
            'cache_info': cache_info
        }), 200
        
    except Exception as e:
        logging.error(f"캐시 정보 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@nutrition_bp.route('/nutrition/compare', methods=['POST'])
def compare_with_targets():
    """영양소를 사용자 목표와 비교"""
    try:
        data = request.get_json()
        
        if not data or 'nutrition' not in data:
            return jsonify({'error': '영양소 데이터가 필요합니다.'}), 400
        
        # 사용자 프로필 확인
        profile = SessionProfileService.get_profile()
        if not profile or 'nutrition_targets' not in profile:
            return jsonify({'error': '사용자 프로필이 설정되지 않았습니다.'}), 400
        
        calculator = NutritionCalculatorService()
        
        # 백분율 계산
        percentages = calculator.calculate_nutrition_percentage(
            data['nutrition'],
            profile['nutrition_targets']
        )
        
        # 남은 허용량 계산
        remaining = calculator.get_remaining_allowance(
            data['nutrition'],
            profile['nutrition_targets']
        )
        
        # 부족분과 과잉분 식별
        deficient, excess = calculator.identify_nutritional_gaps(
            data['nutrition'],
            profile['nutrition_targets']
        )
        
        return jsonify({
            'success': True,
            'percentages': percentages,
            'remaining_allowance': remaining,
            'deficient_nutrients': deficient,
            'excess_nutrients': excess,
            'targets': profile['nutrition_targets']
        }), 200
        
    except Exception as e:
        logging.error(f"영양소 비교 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500