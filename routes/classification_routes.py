"""
음식 분류 관련 라우트 (SavedModel 사용)
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from services.pytorch_service import get_pytorch_service
from utils.image_utils import ImageValidator, get_image_upload_guidelines
import logging

classification_bp = Blueprint('classification', __name__)

@classification_bp.route('/classify', methods=['POST'])
def classify_food():
    """음식 이미지 분류 (SavedModel 사용)"""
    try:
        # 파일 업로드 확인
        if 'image' not in request.files:
            return jsonify({'error': '이미지 파일이 필요합니다.'}), 400
        
        file = request.files['image']
        
        # 파일명 확인
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다.'}), 400
        
        # 파일 확장자 검증
        if not ImageValidator.validate_file_extension(file.filename):
            return jsonify({
                'error': '지원되지 않는 파일 형식입니다.',
                'supported_formats': list(ImageValidator.SUPPORTED_FORMATS)
            }), 400
        
        # 파일 크기 검증
        file.seek(0, 2)  # 파일 끝으로 이동
        file_size = file.tell()
        file.seek(0)  # 파일 시작으로 이동
        
        if not ImageValidator.validate_file_size(file_size):
            max_size_mb = ImageValidator.MAX_FILE_SIZE // (1024 * 1024)
            return jsonify({
                'error': f'파일 크기가 너무 큽니다. 최대 {max_size_mb}MB까지 지원됩니다.'
            }), 400
        
        # 이미지 내용 검증
        is_valid, error_message = ImageValidator.validate_image_content(file)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # PyTorch 서비스 사용
        ml_service = get_pytorch_service()
        
        if not ml_service.is_model_ready():
            return jsonify({
                'error': '모델이 준비되지 않았습니다. 잠시 후 다시 시도해주세요.',
                'model_status': 'not_ready'
            }), 503
        
        # PyTorch 이미지 전처리
        processed_image = ml_service.preprocess_image(file)
        if processed_image is None:
            return jsonify({'error': '이미지 처리 중 오류가 발생했습니다.'}), 500
        
        # PyTorch 음식 분류 수행
        classification_result = ml_service.classify_food(processed_image)
        if classification_result is None:
            return jsonify({'error': '음식 분류 중 오류가 발생했습니다.'}), 500
        
        food_name, confidence, top_3_predictions = classification_result
        
        # 신뢰도 임계값 확인
        confidence_threshold = ml_service.get_confidence_threshold()
        is_confident = confidence >= confidence_threshold
        
        response_data = {
            'success': True,
            'predicted_food': food_name,
            'confidence': round(confidence * 100, 1),  # 백분율로 변환
            'is_confident': is_confident,
            'top_predictions': [
                {
                    'food_name': pred_food,
                    'confidence': round(pred_conf * 100, 1)
                }
                for pred_food, pred_conf in top_3_predictions
            ],
            'threshold': round(confidence_threshold * 100, 1)
        }
        
        # 낮은 신뢰도일 경우 추가 안내
        if not is_confident:
            response_data['message'] = '분류 결과의 신뢰도가 낮습니다. 수동으로 음식을 선택해주세요.'
            response_data['suggestion'] = 'manual_selection_required'
        
        # 업로드 추적
        from utils.upload_utils import UploadTracker
        file_info = {
            'filename': secure_filename(file.filename),
            'size': file_size
        }
        
        classification_result = {
            'status': 'confident' if is_confident else 'low_confidence',
            'predicted_food': food_name,
            'confidence': confidence * 100
        }
        
        upload_id = UploadTracker.track_upload_attempt(file_info, classification_result, session)
        response_data['upload_id'] = upload_id
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logging.error(f"음식 분류 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@classification_bp.route('/foods/supported', methods=['GET'])
def get_supported_foods():
    """지원되는 음식 목록 조회"""
    try:
        ml_service = get_pytorch_service()
        supported_foods = ml_service.get_supported_foods()
        
        return jsonify({
            'success': True,
            'supported_foods': supported_foods,
            'total_count': len(supported_foods),
            'model_ready': ml_service.is_model_ready()
        }), 200
        
    except Exception as e:
        logging.error(f"지원 음식 목록 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@classification_bp.route('/upload/guidelines', methods=['GET'])
def get_upload_guidelines():
    """이미지 업로드 가이드라인 조회"""
    try:
        guidelines = get_image_upload_guidelines()
        
        return jsonify({
            'success': True,
            'guidelines': guidelines
        }), 200
        
    except Exception as e:
        logging.error(f"업로드 가이드라인 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@classification_bp.route('/model/status', methods=['GET'])
def get_model_status():
    """PyTorch 모델 상태 확인"""
    try:
        ml_service = get_pytorch_service()
        model_info = ml_service.get_model_info()
        
        return jsonify({
            'success': True,
            'model_ready': ml_service.is_model_ready(),
            'supported_foods_count': len(ml_service.get_supported_foods()),
            'confidence_threshold': round(ml_service.get_confidence_threshold() * 100, 1),
            'model_info': model_info
        }), 200
        
    except Exception as e:
        logging.error(f"모델 상태 확인 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@classification_bp.route('/classification/help', methods=['GET'])
def get_classification_help():
    """분류 도움말 조회"""
    try:
        from utils.classification_utils import get_classification_help
        
        help_info = get_classification_help()
        
        return jsonify({
            'success': True,
            'help': help_info
        }), 200
        
    except Exception as e:
        logging.error(f"분류 도움말 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@classification_bp.route('/classification/alternatives/<food_name>', methods=['GET'])
def get_alternative_foods(food_name):
    """대안 음식 제안"""
    try:
        ml_service = get_pytorch_service()
        available_foods = ml_service.get_supported_foods()
        
        from utils.classification_utils import ClassificationErrorHandler
        alternatives = ClassificationErrorHandler.suggest_alternative_foods(
            food_name, available_foods
        )
        
        return jsonify({
            'success': True,
            'original_food': food_name,
            'alternatives': alternatives,
            'message': f'{food_name}와(과) 유사한 음식들입니다.'
        }), 200
        
    except Exception as e:
        logging.error(f"대안 음식 제안 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@classification_bp.route('/classification/tips', methods=['GET'])
def get_photography_tips():
    """촬영 팁 조회"""
    try:
        error_type = request.args.get('type', 'general')
        
        from utils.classification_utils import ClassificationErrorHandler
        tips = ClassificationErrorHandler.generate_photography_tips(error_type)
        
        return jsonify({
            'success': True,
            'error_type': error_type,
            'tips': tips
        }), 200
        
    except Exception as e:
        logging.error(f"촬영 팁 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@classification_bp.route('/classification/manual-select', methods=['POST'])
def manual_food_selection():
    """수동 음식 선택"""
    try:
        data = request.get_json()
        
        if not data or 'food_name' not in data:
            return jsonify({'error': '음식명이 필요합니다.'}), 400
        
        food_name = data['food_name']
        
        # 지원되는 음식인지 확인
        ml_service = get_pytorch_service()
        supported_foods = ml_service.get_supported_foods()
        
        if food_name not in supported_foods:
            return jsonify({
                'error': f'{food_name}은(는) 지원되지 않는 음식입니다.',
                'supported_foods': supported_foods
            }), 400
        
        # 영양 정보 조회
        from services.nutrition_data_service import get_nutrition_data_service
        nutrition_service = get_nutrition_data_service()
        nutrition_data = nutrition_service.get_nutrition_data(food_name)
        
        if not nutrition_data:
            return jsonify({
                'error': f'{food_name}의 영양 정보를 찾을 수 없습니다.'
            }), 404
        
        # 수동 선택 결과 반환
        response_data = {
            'success': True,
            'selected_food': food_name,
            'selection_method': 'manual',
            'confidence': 100.0,  # 수동 선택이므로 100%
            'nutrition_data': nutrition_data,
            'message': f'{food_name}이(가) 수동으로 선택되었습니다.'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logging.error(f"수동 음식 선택 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@classification_bp.route('/classification/validate-selection', methods=['POST'])
def validate_food_selection():
    """음식 선택 유효성 검증"""
    try:
        data = request.get_json()
        
        if not data or 'food_name' not in data:
            return jsonify({'error': '음식명이 필요합니다.'}), 400
        
        food_name = data['food_name']
        
        # 지원되는 음식인지 확인
        ml_service = get_pytorch_service()
        supported_foods = ml_service.get_supported_foods()
        
        is_supported = food_name in supported_foods
        
        # 영양 데이터 존재 여부 확인
        nutrition_available = False
        if is_supported:
            from services.nutrition_data_service import get_nutrition_data_service
            nutrition_service = get_nutrition_data_service()
            nutrition_data = nutrition_service.get_nutrition_data(food_name)
            nutrition_available = nutrition_data is not None
        
        # 유사한 음식 제안
        alternatives = []
        if not is_supported:
            from utils.classification_utils import ClassificationErrorHandler
            alternatives = ClassificationErrorHandler.suggest_alternative_foods(
                food_name, supported_foods
            )
        
        return jsonify({
            'success': True,
            'food_name': food_name,
            'is_supported': is_supported,
            'nutrition_available': nutrition_available,
            'alternatives': alternatives,
            'message': '선택 가능한 음식입니다.' if is_supported else '지원되지 않는 음식입니다.'
        }), 200
        
    except Exception as e:
        logging.error(f"음식 선택 검증 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@classification_bp.route('/classification/search', methods=['GET'])
def search_foods():
    """음식 검색"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'error': '검색어가 필요합니다.'}), 400
        
        # 지원되는 음식 목록에서 검색
        ml_service = get_pytorch_service()
        supported_foods = ml_service.get_supported_foods()
        
        # 간단한 부분 문자열 매칭
        matching_foods = [
            food for food in supported_foods 
            if query.lower() in food.lower()
        ]
        
        # 정확히 일치하는 것을 먼저 정렬
        exact_matches = [food for food in matching_foods if query.lower() == food.lower()]
        partial_matches = [food for food in matching_foods if food not in exact_matches]
        
        results = exact_matches + partial_matches
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results[:10],  # 최대 10개 결과
            'total_count': len(results)
        }), 200
        
    except Exception as e:
        logging.error(f"음식 검색 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@classification_bp.route('/upload/history', methods=['GET'])
def get_upload_history():
    """업로드 히스토리 조회"""
    try:
        limit = int(request.args.get('limit', 10))
        
        from utils.upload_utils import UploadTracker
        history = UploadTracker.get_upload_history(session, limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'total_count': len(history)
        }), 200
        
    except Exception as e:
        logging.error(f"업로드 히스토리 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@classification_bp.route('/upload/statistics', methods=['GET'])
def get_upload_statistics():
    """업로드 통계 조회"""
    try:
        from utils.upload_utils import UploadTracker
        stats = UploadTracker.get_upload_statistics(session)
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        logging.error(f"업로드 통계 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

@classification_bp.route('/upload/reupload-guidance', methods=['GET'])
def get_reupload_guidance():
    """재업로드 가이드 조회"""
    try:
        from utils.upload_utils import ReuploadHelper
        
        # 이전 실패 분석
        failure_analysis = ReuploadHelper.analyze_previous_failures(session)
        
        # 모범 사례
        from utils.upload_utils import get_upload_best_practices
        best_practices = get_upload_best_practices()
        
        return jsonify({
            'success': True,
            'failure_analysis': failure_analysis,
            'best_practices': best_practices
        }), 200
        
    except Exception as e:
        logging.error(f"재업로드 가이드 조회 중 오류 발생: {str(e)}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500