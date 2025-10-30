import React, { useState, useRef } from 'react';
import {
  Typography,
  Button,
  Box,
  Alert,
  CircularProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  TextField,
  InputAdornment,
  Divider,
  Paper,
} from '@mui/material';
import {
  CloudUpload,
  Search,
  CheckCircle,
  Warning,
  Restaurant,
} from '@mui/icons-material';

import { intakeService, classificationService } from '../services/api';
import './FoodClassification.css';

const FoodClassification = ({ onMealLog }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [classificationResult, setClassificationResult] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // 수동 선택 관련 상태
  const [manualSelectOpen, setManualSelectOpen] = useState(false);
  const [supportedFoods, setSupportedFoods] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredFoods, setFilteredFoods] = useState([]);

  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setClassificationResult(null);
      setError('');
      setSuccess('');
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const classifyImage = async () => {
    if (!selectedFile) {
      setError('이미지를 선택해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');
    setClassificationResult(null);

    try {
      const response = await classificationService.classifyFood(selectedFile);
      const result = response.data;

      setClassificationResult(result);

      if (result.is_confident) {
        setSuccess(`${result.predicted_food}로 정확하게 인식되었습니다! (신뢰도: ${result.confidence}%)`);
      } else {
        setError('신뢰도가 낮아, 아래 추천 음식 중 선택하거나 수동으로 선택해주세요.');
      }
    } catch (error) {
      console.error('분류 실패:', error);
      setError(error.response?.data?.error || '이미지 분류에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleManualSelect = async () => {
    try {
      const response = await classificationService.getSupportedFoods();
      const foods = response.data.supported_foods;
      setSupportedFoods(foods);
      setFilteredFoods(foods);
      setManualSelectOpen(true);
    } catch (error) {
      console.error('지원 음식 목록 로딩 실패:', error);
      setError('음식 목록을 불러오는데 실패했습니다.');
    }
  };

  const handleSearchChange = (event) => {
    const query = event.target.value;
    setSearchQuery(query);

    if (query.trim() === '') {
      setFilteredFoods(supportedFoods);
    } else {
      const filtered = supportedFoods.filter(food =>
        food.toLowerCase().includes(query.toLowerCase())
      );
      setFilteredFoods(filtered);
    }
  };

  const selectFood = async (foodName, isManual = false) => {
    setLoading(true);
    setError('');

    try {
      console.log('식사 기록 시작:', { foodName, isManual });

      const confidence = isManual ? 100 : classificationResult?.confidence;
      const response = await intakeService.logMeal(foodName, confidence);

      console.log('식사 기록 응답:', response.data);

      setSuccess(`${foodName}이(가) 성공적으로 기록되었습니다! 2초 후 초기화됩니다.`);
      setManualSelectOpen(false);

      if (onMealLog) {
        onMealLog();
      }

      setTimeout(() => {
        setSelectedFile(null);
        setPreviewUrl(null);
        setClassificationResult(null);
        setSuccess('');
        setError('');
      }, 2000);

    } catch (error) {
      console.error('음식 선택/기록 실패:', error);
      console.error('에러 상세:', error.response?.data);

      let errorMessage = '음식 기록에 실패했습니다.';

      if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.response?.data?.debug_message) {
        errorMessage += ` (${error.response.data.debug_message})`;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box className="food-classification-container">
      <Typography variant="h4" gutterBottom className="page-title">
        음식 기록하기
      </Typography>

      <Typography variant="body1" color="text.secondary" className="page-subtitle">
        사진을 올려 음식을 인식하고 간편하게 식사를 기록하세요.
      </Typography>

      <div className="main-layout">
        <div className="upload-section">
          <Paper
            variant="outlined"
            className="upload-paper"
            onClick={handleUploadClick}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept="image/*"
              style={{ display: 'none' }}
            />

            {previewUrl ? (
              <Box className="preview-box">
                <img
                  src={previewUrl}
                  alt="선택된 음식"
                  className="preview-image"
                />
                <Typography variant="body2" color="text.secondary" className="preview-reselect-text">
                  다른 이미지 선택하기
                </Typography>
              </Box>
            ) : (
              <Box className="upload-placeholder">
                <CloudUpload className="upload-icon" />
                <Typography variant="h6" className="upload-placeholder-title">
                  클릭하여 사진 업로드
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  (JPG, PNG, WEBP)
                </Typography>
              </Box>
            )}
          </Paper>
        </div>

        <div className="analysis-section-wrapper">
          <Box className="analysis-section">
            <Box>
              <Typography variant="h6" gutterBottom>음식 분석 및 기록</Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                MVP 모델이라 이미지 인식 가능한 음식 종류는 11가지입니다:
              </Typography>
              <Box component="ul" sx={{ paddingLeft: 2, margin: 0, marginBottom: 2 }}>
                <li>감자탕</li>
                <li>삼계탕</li>
                <li>김치찌개</li>
                <li>갈치조림</li>
                <li>곱창전골</li>
                <li>김치볶음밥</li>
                <li>잡곡밥</li>
                <li>꿀떡</li>
                <li>시금치나물</li>
                <li>배추김치</li>
                <li>콩나물국</li>
              </Box>
              {error && <Alert severity="error" className="alert-message">{error}</Alert>}
              {success && <Alert severity="success" className="alert-message">{success}</Alert>}

              {classificationResult && (
                <Box className="classification-result-box">
                  <Typography variant="subtitle1" gutterBottom>분석 결과:</Typography>
                  <Chip
                    icon={classificationResult.is_confident ? <CheckCircle /> : <Warning />}
                    label={`${classificationResult.predicted_food} (${classificationResult.confidence}%)`}
                    color={classificationResult.is_confident ? 'success' : 'warning'}
                    className="classification-chip"
                  />
                  {classificationResult.is_confident ? (
                    <Button
                      variant="contained"
                      fullWidth
                      onClick={() => selectFood(classificationResult.predicted_food)}
                      disabled={loading}
                      startIcon={<Restaurant />}
                      className="log-meal-button"
                    >
                      이 음식으로 식사 기록하기
                    </Button>
                  ) : (
                    <Box className="recommendation-box">
                      <Typography variant="body2" color="text.secondary">다른 추천:</Typography>
                      <div className="recommendation-grid">
                        {classificationResult.top_predictions?.map((pred) => (
                          <Chip
                            key={pred.food_name}
                            label={`${pred.food_name} (${pred.confidence.toFixed(1)}%)`}
                            onClick={() => selectFood(pred.food_name)}
                            clickable
                            variant="outlined"
                          />
                        ))}
                      </div>
                    </Box>
                  )}
                </Box>
              )}
            </Box>

            <Box className="action-buttons-container">
              <Button
                variant="contained"
                fullWidth
                onClick={classifyImage}
                disabled={!selectedFile || loading}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <CloudUpload />}
                className="action-button"
              >
                {loading ? '분석 중...' : '이미지 분석'}
              </Button>
              <Button
                variant="outlined"
                fullWidth
                onClick={handleManualSelect}
                startIcon={<Search />}
                className="action-button"
              >
                수동으로 선택
              </Button>
            </Box>
          </Box>
        </div>
      </div>

      {/* 수동 선택 다이얼로그 */}
      <Dialog open={manualSelectOpen} onClose={() => setManualSelectOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>음식 수동 선택</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            autoFocus
            placeholder="음식 이름 검색..."
            value={searchQuery}
            onChange={handleSearchChange}
            InputProps={{
              startAdornment: <InputAdornment position="start"><Search /></InputAdornment>,
            }}
            className="search-field"
          />
          <Paper className="food-list-paper">
            <List disablePadding>
              {filteredFoods.map((food, index) => (
                <React.Fragment key={food}>
                  <ListItem disablePadding>
                    <ListItemButton onClick={() => selectFood(food, true)} disabled={loading}>
                      <ListItemText primary={food} />
                    </ListItemButton>
                  </ListItem>
                  {index < filteredFoods.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
          {filteredFoods.length === 0 && searchQuery && (
            <Typography color="text.secondary" className="search-no-results">검색 결과가 없습니다.</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setManualSelectOpen(false)}>취소</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FoodClassification;