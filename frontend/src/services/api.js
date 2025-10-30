import axios from 'axios';

// API 기본 설정
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // 세션 쿠키 포함
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 (로깅)
api.interceptors.request.use(
  (config) => {
    console.log('API 요청:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      data: config.data,
      headers: config.headers
    });
    return config;
  },
  (error) => {
    console.error('API 요청 오류:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터 (에러 처리)
api.interceptors.response.use(
  (response) => {
    console.log('API 응답:', {
      status: response.status,
      url: response.config.url,
      data: response.data
    });
    return response;
  },
  (error) => {
    console.error('API 응답 오류:', {
      status: error.response?.status,
      url: error.config?.url,
      data: error.response?.data,
      message: error.message
    });
    return Promise.reject(error);
  }
);

// 프로필 관련 API
export const profileService = {
  // 프로필 존재 여부 확인
  checkProfile: () => api.get('/profile/check'),
  
  // 프로필 생성
  createProfile: (profileData) => api.post('/profile/setup', profileData),
  
  // 프로필 조회
  getProfile: () => api.get('/profile'),
  
  // 프로필 업데이트
  updateProfile: (profileData) => api.put('/profile', profileData),
  
  // 프로필 삭제
  deleteProfile: () => api.delete('/profile'),
};

// 음식 분류 관련 API
export const classificationService = {
  // 음식 이미지 분류 (SavedModel 사용)
  classifyFood: (imageFile) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    return api.post('/classify', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // 지원되는 음식 목록
  getSupportedFoods: () => api.get('/foods/supported'),
  
  // 수동 음식 선택
  manualSelect: (foodName) => api.post('/classification/manual-select', { food_name: foodName }),
  
  // 음식 검색
  searchFoods: (query) => api.get(`/classification/search?q=${encodeURIComponent(query)}`),
  
  // 업로드 가이드라인
  getUploadGuidelines: () => api.get('/upload/guidelines'),
  
  // 분류 도움말
  getClassificationHelp: () => api.get('/classification/help'),
  
  // 촬영 팁
  getPhotographyTips: (errorType = 'general') => api.get(`/classification/tips?type=${errorType}`),
};

// TensorFlow.js 관련 API
export const tensorflowJsService = {
  // 모델 정보 조회
  getModelInfo: () => api.get('/tensorflow-js/model-info'),
  
  // 클라이언트 사이드 코드 조회
  getClientCode: () => api.get('/tensorflow-js/client-code'),
  
  // 웹캠 통합 코드 조회
  getWebcamCode: () => api.get('/tensorflow-js/webcam-code'),
};

// 영양 정보 관련 API
export const nutritionService = {
  // 특정 음식의 영양 정보
  getFoodNutrition: (foodName) => api.get(`/nutrition/${encodeURIComponent(foodName)}`),
  
  // 사용 가능한 음식 목록
  getAvailableFoods: () => api.get('/nutrition/available'),
  
  // 영양소 비교
  compareWithTargets: (nutritionData) => api.post('/nutrition/compare', { nutrition: nutritionData }),
};

// 섭취량 추적 관련 API
export const intakeService = {
  // 식사 기록
  logMeal: async (foodName, confidenceScore = null) => {
    try {
      if (!foodName || typeof foodName !== 'string') {
        throw new Error('유효한 음식명이 필요합니다.');
      }
      
      console.log('식사 기록 요청:', { foodName, confidenceScore });
      
      const response = await api.post('/intake/log', { 
        food_name: foodName.trim(), 
        confidence_score: confidenceScore 
      });
      
      console.log('식사 기록 성공:', response.data);
      return response;
      
    } catch (error) {
      console.error('식사 기록 실패:', error.response?.data || error.message);
      throw error;
    }
  },
  
  // 일일 섭취량 조회
  getDailyIntake: (date = null) => {
    const params = date ? `?date=${date}` : '';
    return api.get(`/intake/daily${params}`);
  },
  
  // 진행 상황 조회
  getProgress: () => api.get('/intake/progress'),
  
  // 식사 기록 히스토리
  getMealHistory: (limit = 10) => api.get(`/intake/meals/history?limit=${limit}`),
  
  // 식사 기록 삭제
  deleteMeal: (mealId) => api.delete(`/intake/meals/${mealId}`),
  
  // 일일 섭취량 리셋
  resetDailyIntake: (date = null) => api.post('/intake/reset', date ? { date } : {}),
  
  // 섭취량 요약
  getIntakeSummary: () => api.get('/intake/summary'),
};

// 추천 관련 API
export const recommendationService = {
  // 식사 추천 조회
  getRecommendations: (limit = 3) => api.get(`/recommendations?limit=${limit}`),
  
  // 영양 분석 정보
  getNutritionalAnalysis: () => api.get('/recommendations/analysis'),
  
  // 추천 피드백 제출
  submitFeedback: (foodName, feedbackType, comment = '') => 
    api.post('/recommendations/feedback', {
      food_name: foodName,
      feedback_type: feedbackType,
      comment: comment,
    }),
  
  // 추천 히스토리
  getRecommendationHistory: (limit = 10) => api.get(`/recommendations/history?limit=${limit}`),
  
  // 식단 지침
  getDietaryGuidelines: () => api.get('/recommendations/guidelines'),
};

// 디버깅 관련 API
export const debugService = {
  // 세션 상태 확인
  getSessionStatus: () => api.get('/debug/session'),
};

export default api;