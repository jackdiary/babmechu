"""
추천 시스템 관련 라우트
"""

from flask import Blueprint, request, jsonify, session
from services.recommendation_service import MenuRecommendationEngine, NutritionalGapAnalyzer
from services.profile_service import SessionProfileService
from utils.nutrition_utils import get_nutrition_display_names, format_nutrition_value
import logging
from datetime import datetime

recommendation_bp = Blueprint('recommendation', __name__)

@recommendation_bp.route('/recommendations', methods=['GET'])
def get_meal_recommendations():
    """식사 추천 조회"""
    try:
        # 사용자 프로필 확인
        profile = SessionProfileService.get_profile()
        if not profile:
            return jsonify({
                'error': '프로필이 설정되지 않았습니다.',
                'suggestion': 'setup_profile_required'
            }), 400
        
        # 추천 개수 파라미터
        max_recommendations = int(request.args.get('limit', 3))
        max_recommendations = min(max_recommendations, 5)  # 최대 5개로 제한
        
        # 추천 엔진 실행
        recommendation_engine = MenuRecommendationEngine()
        recommendations = recommendation_engine.generate_recommendations(max_recommendations)
        
        if not recommendations:
            return jsonify({
                'success': True,
                'recommendations': [],
                'message': '현재 추천할 수 있는 메뉴가 없습니다.',
                'suggestion': 'try_later_or_manual_selection'
            }), 200
        
        # 영양 분석 정보도 함께 제공
        analyzer = NutritionalGapAnalyzer()
        analysis = analyzer.get_detailed_analysis()
        
        # 추천 결과 포맷팅
        formatted_recommendations = []
        
        for rec in recommendations:
            # 영양 정보 포맷팅
            display_names = get_nutrition_display_names()
            formatted_nutrition = {}
            
            for nutrient, value in rec['nutrition_data']['nutrition'].items():
                formatted_nutrition[nutrient] = {
                    'value': value,
                    'formatted': format_nutrition_value(nutrient, value),
                    'display_name': display_names.get(nutrient, nutrient)
                }
            
            formatted_recommendations.append({
                'food_name': rec['food_name'],
                'score': round(rec['score'], 1),
                'reasoning': rec['reasoning'],
                'benefits': rec['benefits'],
                'nutrition': formatted_nutrition,
                'serving_size': rec['nutrition_data']['serving_size']
            })
        
        # 추천 히스토리에 저장
        _save_recommendation_history(formatted_recommendations, analysis)
        
        return jsonify({
            'success': True,
            'recommendations': formatted_recommendations,
            'nutritional_analysis': {
                'deficient_nutrients': analysis['deficient_nutrients'],
                'excess_nutrients': analysis['excess_nutrients'],
                'analysis_summary': analysis['analysis_summary']
            },
            'generated_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logging.error(f"식사 추천 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@recommendation_bp.route('/recommendations/analysis', methods=['GET'])
def get_nutritional_analysis():
    """영양 분석 정보만 조회"""
    try:
        # 사용자 프로필 확인
        profile = SessionProfileService.get_profile()
        if not profile:
            return jsonify({
                'error': '프로필이 설정되지 않았습니다.'
            }), 400
        
        # 영양 분석 수행
        analyzer = NutritionalGapAnalyzer()
        analysis = analyzer.get_detailed_analysis()
        
        # 우선순위 영양소 정보
        priorities = analyzer.get_nutrient_priorities()
        
        return jsonify({
            'success': True,
            'analysis': {
                'current_intake': analysis['current_intake'],
                'targets': analysis['targets'],
                'deficient_nutrients': analysis['deficient_nutrients'],
                'excess_nutrients': analysis['excess_nutrients'],
                'percentages': analysis['percentages'],
                'remaining_allowance': analysis['remaining_allowance'],
                'priority_nutrients': priorities,
                'summary': analysis['analysis_summary']
            }
        }), 200
        
    except Exception as e:
        logging.error(f"영양 분석 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@recommendation_bp.route('/recommendations/feedback', methods=['POST'])
def submit_recommendation_feedback():
    """추천 피드백 제출"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '피드백 데이터가 필요합니다.'}), 400
        
        required_fields = ['food_name', 'feedback_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'필수 필드가 누락되었습니다: {field}'}), 400
        
        food_name = data['food_name']
        feedback_type = data['feedback_type']  # 'liked', 'disliked', 'tried', 'not_interested'
        comment = data.get('comment', '')
        
        # 유효한 피드백 타입 확인
        valid_feedback_types = ['liked', 'disliked', 'tried', 'not_interested']
        if feedback_type not in valid_feedback_types:
            return jsonify({
                'error': '유효하지 않은 피드백 타입입니다.',
                'valid_types': valid_feedback_types
            }), 400
        
        # 피드백 저장
        feedback_data = {
            'food_name': food_name,
            'feedback_type': feedback_type,
            'comment': comment,
            'timestamp': datetime.now().isoformat()
        }
        
        _save_feedback(feedback_data)
        
        # 피드백에 따른 응답 메시지
        response_messages = {
            'liked': '좋은 피드백 감사합니다! 비슷한 음식을 더 추천해드리겠습니다.',
            'disliked': '피드백 감사합니다. 다음 추천에 반영하겠습니다.',
            'tried': '시도해주셔서 감사합니다! 어떠셨는지 궁금하네요.',
            'not_interested': '피드백 감사합니다. 다른 옵션을 찾아보겠습니다.'
        }
        
        return jsonify({
            'success': True,
            'message': response_messages.get(feedback_type, '피드백이 저장되었습니다.'),
            'feedback_saved': feedback_data
        }), 200
        
    except Exception as e:
        logging.error(f"추천 피드백 제출 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@recommendation_bp.route('/recommendations/history', methods=['GET'])
def get_recommendation_history():
    """추천 히스토리 조회"""
    try:
        limit = int(request.args.get('limit', 10))
        
        history = _get_recommendation_history(limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'total_count': len(history)
        }), 200
        
    except Exception as e:
        logging.error(f"추천 히스토리 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@recommendation_bp.route('/recommendations/guidelines', methods=['GET'])
def get_dietary_guidelines():
    """일반적인 식단 지침 조회"""
    try:
        # 사용자 프로필 확인
        profile = SessionProfileService.get_profile()
        
        if not profile:
            # 일반적인 지침
            guidelines = _get_general_dietary_guidelines()
        else:
            # 개인 맞춤형 지침
            analyzer = NutritionalGapAnalyzer()
            analysis = analyzer.get_detailed_analysis()
            guidelines = _get_personalized_guidelines(analysis, profile)
        
        return jsonify({
            'success': True,
            'guidelines': guidelines
        }), 200
        
    except Exception as e:
        logging.error(f"식단 지침 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

def _save_recommendation_history(recommendations: list, analysis: dict):
    """추천 히스토리 저장 (세션 기반)"""
    if 'recommendation_history' not in session:
        session['recommendation_history'] = []
    
    history_entry = {
        'timestamp': datetime.now().isoformat(),
        'recommendations': recommendations,
        'nutritional_context': {
            'deficient_nutrients': analysis['deficient_nutrients'],
            'nutrition_score': analysis['analysis_summary']['nutrition_score']
        }
    }
    
    session['recommendation_history'].insert(0, history_entry)
    
    # 최대 20개까지만 보관
    if len(session['recommendation_history']) > 20:
        session['recommendation_history'] = session['recommendation_history'][:20]
    
    session.modified = True

def _save_feedback(feedback_data: dict):
    """피드백 저장 (세션 기반)"""
    if 'recommendation_feedback' not in session:
        session['recommendation_feedback'] = []
    
    session['recommendation_feedback'].insert(0, feedback_data)
    
    # 최대 50개까지만 보관
    if len(session['recommendation_feedback']) > 50:
        session['recommendation_feedback'] = session['recommendation_feedback'][:50]
    
    session.modified = True

def _get_recommendation_history(limit: int) -> list:
    """추천 히스토리 조회"""
    if 'recommendation_history' not in session:
        return []
    
    return session['recommendation_history'][:limit]

def _get_general_dietary_guidelines() -> dict:
    """일반적인 식단 지침"""
    return {
        'title': '건강한 식단 지침',
        'guidelines': [
            '하루 3끼 규칙적으로 식사하세요',
            '다양한 색깔의 채소와 과일을 섭취하세요',
            '충분한 수분을 섭취하세요 (하루 8잔 이상)',
            '가공식품보다는 자연식품을 선택하세요',
            '적당한 운동과 함께 균형 잡힌 식단을 유지하세요'
        ],
        'tips': [
            '식사 전 물 한 잔으로 포만감을 높이세요',
            '천천히 씹어서 드세요',
            '야식은 피하고 저녁 8시 이전에 식사를 마치세요'
        ]
    }

def _get_personalized_guidelines(analysis: dict, profile: dict) -> dict:
    """개인 맞춤형 식단 지침"""
    guidelines = []
    tips = []
    
    # 영양 상태에 따른 지침
    summary = analysis['analysis_summary']
    
    if summary['nutrition_score'] < 50:
        guidelines.append('전반적인 영양 균형 개선이 필요합니다')
        tips.append('매 끼니마다 단백질, 탄수화물, 채소를 포함하세요')
    
    # 부족한 영양소에 따른 지침
    deficient = analysis['deficient_nutrients']
    
    if 'protein' in deficient:
        guidelines.append('단백질 섭취를 늘려주세요 (육류, 생선, 콩류)')
    
    if 'fiber' in deficient:
        guidelines.append('식이섬유가 풍부한 음식을 섭취하세요 (채소, 과일, 통곡물)')
    
    if 'calories' in deficient:
        guidelines.append('충분한 칼로리 섭취로 에너지를 보충하세요')
    
    # 과잉 영양소에 따른 지침
    excess = analysis['excess_nutrients']
    
    if 'sodium' in excess:
        guidelines.append('나트륨 섭취를 줄여주세요 (짠 음식 피하기)')
        tips.append('조리 시 소금 대신 허브나 향신료를 사용하세요')
    
    if 'saturated_fat' in excess:
        guidelines.append('포화지방 섭취를 줄여주세요')
    
    # 목표에 따른 지침
    goal = profile.get('goal', 'maintain')
    
    if goal == 'lose':
        tips.append('칼로리 밀도가 낮은 음식을 선택하세요')
        tips.append('식사 전 채소나 샐러드를 먼저 드세요')
    elif goal == 'gain':
        tips.append('영양가 높은 간식을 추가하세요')
        tips.append('운동 후 단백질 보충을 잊지 마세요')
    
    if not guidelines:
        guidelines.append('현재 영양 상태가 양호합니다. 이 상태를 유지하세요!')
    
    return {
        'title': '개인 맞춤 식단 지침',
        'nutrition_score': summary['nutrition_score'],
        'overall_status': summary['overall_status'],
        'guidelines': guidelines,
        'tips': tips if tips else ['균형 잡힌 식단을 계속 유지하세요']
    }