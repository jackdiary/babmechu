"""
섭취량 추적 관련 라우트 (세션 기반 MVP)
"""

from flask import Blueprint, request, jsonify
from services.intake_service import SessionIntakeService
from services.nutrition_data_service import get_nutrition_data_service
from services.profile_service import SessionProfileService
from services.nutrition_service import NutritionCalculatorService
from utils.nutrition_utils import get_nutrition_display_names, format_nutrition_value
import logging

intake_bp = Blueprint('intake', __name__)

@intake_bp.route('/intake/log', methods=['POST'])
def log_meal():
    """식사 기록"""
    try:
        data = request.get_json()
        
        if not data:
            logging.warning("식사 기록 요청에 데이터가 없음")
            return jsonify({'error': '요청 데이터가 필요합니다.'}), 400
        
        if 'food_name' not in data:
            logging.warning(f"식사 기록 요청에 food_name이 없음: {data}")
            return jsonify({'error': '음식명이 필요합니다.'}), 400
        
        food_name = data['food_name'].strip()
        confidence_score = data.get('confidence_score')
        
        if not food_name:
            return jsonify({'error': '유효한 음식명이 필요합니다.'}), 400
        
        logging.info(f"식사 기록 시도: {food_name}, 신뢰도: {confidence_score}")
        
        # 영양 데이터 조회
        nutrition_service = get_nutrition_data_service()
        nutrition_data = nutrition_service.get_nutrition_data(food_name)
        
        if not nutrition_data:
            logging.warning(f"영양 정보를 찾을 수 없음: {food_name}, 대체 데이터 사용")
            # 대체 영양 데이터 사용
            nutrition_data = nutrition_service.get_fallback_nutrition_data(food_name)
        
        logging.info(f"영양 데이터 조회 성공: {food_name}")
        
        # 식사 기록
        meal_log = SessionIntakeService.log_meal(
            food_name=food_name,
            nutrition_data=nutrition_data['nutrition'],
            confidence_score=confidence_score
        )
        
        logging.info(f"식사 기록 완료: ID {meal_log['id']}")
        
        # 현재 총 섭취량 조회
        current_totals = SessionIntakeService.get_current_totals()
        
        # 사용자 프로필이 있다면 목표 대비 분석
        analysis = None
        profile = SessionProfileService.get_profile()
        
        if profile and 'nutrition_targets' in profile:
            try:
                calculator = NutritionCalculatorService()
                
                # 백분율 계산
                percentages = calculator.calculate_nutrition_percentage(
                    current_totals,
                    profile['nutrition_targets']
                )
                
                # 남은 허용량 계산
                remaining = calculator.get_remaining_allowance(
                    current_totals,
                    profile['nutrition_targets']
                )
                
                # 부족분과 과잉분 식별
                deficient, excess = calculator.identify_nutritional_gaps(
                    current_totals,
                    profile['nutrition_targets']
                )
                
                analysis = {
                    'percentages': percentages,
                    'remaining_allowance': remaining,
                    'deficient_nutrients': deficient,
                    'excess_nutrients': excess
                }
                
                logging.info("영양 분석 완료")
                
            except Exception as analysis_error:
                logging.error(f"영양 분석 중 오류: {str(analysis_error)}")
                # 분석 실패해도 식사 기록은 성공으로 처리
        
        return jsonify({
            'success': True,
            'message': '식사가 성공적으로 기록되었습니다.',
            'meal_log': meal_log,
            'current_totals': current_totals,
            'analysis': analysis,
            'debug_info': {
                'nutrition_data_found': bool(nutrition_data),
                'profile_exists': bool(profile),
                'analysis_completed': bool(analysis)
            }
        }), 201
        
    except Exception as e:
        logging.error(f"식사 기록 중 오류 발생: {str(e)}", exc_info=True)
        return jsonify({
            'error': '서버 내부 오류가 발생했습니다.',
            'debug_message': str(e) if logging.getLogger().isEnabledFor(logging.DEBUG) else None
        }), 500

@intake_bp.route('/intake/daily', methods=['GET'])
def get_daily_intake():
    """일일 섭취량 조회"""
    try:
        target_date = request.args.get('date')  # YYYY-MM-DD 형식
        
        daily_data = SessionIntakeService.get_daily_intake(target_date)
        
        if not daily_data:
            return jsonify({
                'success': True,
                'daily_intake': None,
                'message': '해당 날짜의 섭취 기록이 없습니다.'
            }), 200
        
        # 표시용 데이터 포맷팅
        display_names = get_nutrition_display_names()
        formatted_nutrition = {}
        
        for nutrient, value in daily_data['total_nutrition'].items():
            formatted_nutrition[nutrient] = {
                'value': value,
                'formatted': format_nutrition_value(nutrient, value),
                'display_name': display_names.get(nutrient, nutrient)
            }
        
        response_data = {
            'success': True,
            'daily_intake': {
                'date': daily_data['date'],
                'total_nutrition': formatted_nutrition,
                'total_meals': len(daily_data.get('meals', [])),
                'meals': daily_data.get('meals', []),
                'created_at': daily_data.get('created_at'),
                'updated_at': daily_data.get('updated_at')
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logging.error(f"일일 섭취량 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@intake_bp.route('/intake/progress', methods=['GET'])
def get_progress():
    """진행 상황 조회 (목표 대비)"""
    try:
        profile = SessionProfileService.get_profile()
        has_targets = bool(profile and 'nutrition_targets' in profile)

        # 현재 섭취량 및 요약 정보는 프로필과 관계없이 제공
        current_totals = SessionIntakeService.get_current_totals()
        summary = SessionIntakeService.get_intake_summary()

        if not has_targets:
            logging.info('프로필 없이 기본 진행 상황을 반환합니다.')
            empty_targets = SessionIntakeService._get_empty_nutrition()

            return jsonify({
                'success': True,
                'progress': {
                    'current_totals': current_totals,
                    'targets': empty_targets,
                    'percentages': {},
                    'remaining_allowance': empty_targets,
                    'deficient_nutrients': {},
                    'excess_nutrients': {},
                    'nutrition_score': None,
                    'summary': summary,
                    'requires_profile': True
                }
            }), 200

        # 분석 수행
        calculator = NutritionCalculatorService()

        percentages = calculator.calculate_nutrition_percentage(
            current_totals,
            profile['nutrition_targets']
        )

        remaining = calculator.get_remaining_allowance(
            current_totals,
            profile['nutrition_targets']
        )

        deficient, excess = calculator.identify_nutritional_gaps(
            current_totals,
            profile['nutrition_targets']
        )

        # 영양 점수 계산
        from utils.nutrition_utils import calculate_nutrition_score
        nutrition_score = calculate_nutrition_score(current_totals, profile['nutrition_targets'])

        return jsonify({
            'success': True,
            'progress': {
                'current_totals': current_totals,
                'targets': profile['nutrition_targets'],
                'percentages': percentages,
                'remaining_allowance': remaining,
                'deficient_nutrients': deficient,
                'excess_nutrients': excess,
                'nutrition_score': nutrition_score,
                'summary': summary,
                'requires_profile': False
            }
        }), 200

    except Exception as e:
        logging.error(f"진행 상황 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@intake_bp.route('/intake/meals/history', methods=['GET'])
def get_meal_history():
    """식사 기록 히스토리 조회"""
    try:
        limit = int(request.args.get('limit', 10))
        
        meals = SessionIntakeService.get_meal_history(limit)
        
        return jsonify({
            'success': True,
            'meals': meals,
            'total_count': len(meals)
        }), 200
        
    except Exception as e:
        logging.error(f"식사 기록 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@intake_bp.route('/intake/meals/<int:meal_id>', methods=['DELETE'])
def delete_meal(meal_id):
    """식사 기록 삭제"""
    try:
        success = SessionIntakeService.delete_meal(meal_id)
        
        if success:
            # 업데이트된 총 섭취량 반환
            current_totals = SessionIntakeService.get_current_totals()
            
            return jsonify({
                'success': True,
                'message': '식사 기록이 삭제되었습니다.',
                'current_totals': current_totals
            }), 200
        else:
            return jsonify({'error': '해당 식사 기록을 찾을 수 없습니다.'}), 404
            
    except Exception as e:
        logging.error(f"식사 기록 삭제 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@intake_bp.route('/intake/reset', methods=['POST'])
def reset_daily_intake():
    """일일 섭취량 리셋"""
    try:
        target_date = request.get_json().get('date') if request.get_json() else None
        
        SessionIntakeService.reset_daily_intake(target_date)
        
        return jsonify({
            'success': True,
            'message': '일일 섭취량이 리셋되었습니다.'
        }), 200
        
    except Exception as e:
        logging.error(f"일일 섭취량 리셋 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@intake_bp.route('/intake/summary', methods=['GET'])
def get_intake_summary():
    """섭취량 요약 정보 조회"""
    try:
        summary = SessionIntakeService.get_intake_summary()
        
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
        
    except Exception as e:
        logging.error(f"섭취량 요약 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500