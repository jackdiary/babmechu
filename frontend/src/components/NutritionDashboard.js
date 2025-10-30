import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Alert,
  CircularProgress,
  Divider,
  Button,
} from '@mui/material';
import {
  Delete,
  Refresh,
  TrendingUp,
  TrendingDown,
  Info,
} from '@mui/icons-material';
import { intakeService, debugService } from '../services/api';
import './NutritionDashboard.css';

const getNutrientColor = (percentage) => {
  if (percentage < 50) return 'error';
  if (percentage < 80) return 'warning';
  if (percentage <= 120) return 'success';
  return 'error';
};

const formatNutrientName = (nutrient) => {
  const names = {
    calories: '칼로리', carbohydrates: '탄수화물', sugars: '당류', protein: '단백질', fat: '지방',
    saturated_fat: '포화지방', cholesterol: '콜레스테롤', sodium: '나트륨', fiber: '식이섬유'
  };
  return names[nutrient] || nutrient;
};

const formatNutrientValue = (nutrient, value) => {
  const units = { calories: 'kcal', cholesterol: 'mg', sodium: 'mg' };
  return `${(value || 0).toFixed(1)}${units[nutrient] || 'g'}`;
};

const NutritionDashboard = ({ refreshTrigger }) => {
  const [progress, setProgress] = useState(null);
  const [mealHistory, setMealHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [debugInfo, setDebugInfo] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, [refreshTrigger]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const [progressResponse, historyResponse, debugResponse] = await Promise.all([
        intakeService.getProgress().catch(err => ({ data: { progress: null }, error: err })),
        intakeService.getMealHistory(10).catch(err => ({ data: { meals: [] }, error: err })),
        debugService.getSessionStatus().catch(err => ({ data: null, error: err }))
      ]);
      
      setProgress(progressResponse.data.progress);
      setMealHistory(historyResponse.data.meals);
      setDebugInfo(debugResponse.data);
      
      if (progressResponse.error) console.error('진행 상황 로딩 실패:', progressResponse.error);
      if (historyResponse.error) console.error('히스토리 로딩 실패:', historyResponse.error);
      
    } catch (error) {
      console.error('대시보드 데이터 로딩 실패:', error);
      setError('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteMeal = async (mealId) => {
    try {
      await intakeService.deleteMeal(mealId);
      loadDashboardData();
    } catch (error) {
      console.error('식사 기록 삭제 실패:', error);
      setError('식사 기록 삭제에 실패했습니다.');
    }
  };

  const handleResetDaily = async () => {
    if (window.confirm('오늘의 모든 섭취 기록을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
      try {
        await intakeService.resetDailyIntake();
        loadDashboardData();
      } catch (error) {
        console.error('일일 섭취량 리셋 실패:', error);
        setError('일일 섭취량 리셋에 실패했습니다.');
      }
    }
  };

  if (loading) {
    return <div className="dashboard-loader"><CircularProgress /></div>;
  }

  if (error) {
    return (
      <Alert severity="error" action={<Button color="inherit" size="small" onClick={loadDashboardData}>다시 시도</Button>}>
        {error}
      </Alert>
    );
  }

  if (!progress) {
    return (
      <Paper className="dashboard-empty-state">
        <Info className="dashboard-empty-state__icon" />
        <Typography variant="h6" className="dashboard-empty-state__title">아직 기록된 식사가 없습니다.</Typography>
        <Typography color="text.secondary" className="dashboard-empty-state__subtitle">음식을 기록하고 영양 상태를 확인해보세요!</Typography>
        
        {debugInfo && (
          <Box className="dashboard-empty-state__debug-box">
            <Typography variant="subtitle2" gutterBottom>디버그 정보:</Typography>
            <Typography variant="caption" component="pre" className="dashboard-empty-state__debug-pre">
              {JSON.stringify(debugInfo, null, 2)}
            </Typography>
          </Box>
        )}
        
        <div className="dashboard-empty-state__test-button-container">
          <Button 
            variant="contained" 
            color="secondary" 
            onClick={async () => {
              try {
                await intakeService.logMeal('김치찌개', 100);
                alert('테스트 성공! 페이지를 새로고침합니다.');
                loadDashboardData();
              } catch (err) {
                alert('테스트 실패: ' + (err.response?.data?.error || err.message));
              }
            }}
          >
            테스트: 김치찌개 기록하기
          </Button>
        </div>
      </Paper>
    );
  }

  const { 
    requires_profile: requiresProfile,
    summary = {},
    current_totals = {},
    targets = {},
    percentages = {},
    deficient_nutrients = {},
    excess_nutrients = {},
    nutrition_score
  } = progress;

  const nutritionScoreDisplay = (!requiresProfile && nutrition_score != null) ? nutrition_score : '--';

  return (
    <div className="dashboard">
      <div className="dashboard__header">
        <Typography variant="h4">영양 대시보드</Typography>
        <Button variant="outlined" startIcon={<Refresh />} onClick={loadDashboardData}>새로고침</Button>
      </div>

      {requiresProfile && (
        <Alert severity="info" className="dashboard__profile-alert">
          영양소 분석을 보려면 프로필을 먼저 설정해주세요. 기록된 식사는 계속 저장됩니다.
        </Alert>
      )}

      <div className="dashboard__grid">
        {/* Summary Cards */}
        <div className="dashboard__summary-cards">
          <Paper className="summary-card"><Typography variant="h3" color="primary">{summary.total_meals ?? 0}</Typography><Typography color="text.secondary">기록된 식사</Typography></Paper>
          <Paper className="summary-card"><Typography variant="h3" color="secondary">{nutritionScoreDisplay}</Typography><Typography color="text.secondary">영양 점수</Typography></Paper>
          <Paper className="summary-card"><Typography variant="h3" color="success.main">{formatNutrientValue('calories', current_totals.calories)}</Typography><Typography color="text.secondary">총 칼로리</Typography></Paper>
          <Paper className="summary-card"><Typography variant="h3" color="info.main">{formatNutrientValue('protein', current_totals.protein)}</Typography><Typography color="text.secondary">총 단백질</Typography></Paper>
        </div>

        {/* Nutrient Progress */}
        <Paper className="dashboard__progress-section">
          <Typography variant="h6" gutterBottom>일일 권장량 대비 섭취 현황</Typography>
          <div className="progress-grid">
            {Object.keys(percentages).length === 0 ? (
              <Typography color="text.secondary">프로필을 설정하면 영양소 진행 상황을 확인할 수 있습니다.</Typography>
            ) : (
              Object.entries(percentages).map(([nutrient, percentage]) => (
                <div className="progress-item" key={nutrient}>
                  <Typography variant="subtitle2">{formatNutrientName(nutrient)}</Typography>
                  <div className="progress-item__bar-container">
                    <div className="progress-item__bar">
                      <LinearProgress variant="determinate" value={Math.min(percentage, 100)} color={getNutrientColor(percentage)} className="progress-item__bar-component" />
                    </div>
                    <Typography variant="body2" color="text.secondary">{percentage.toFixed(0)}%</Typography>
                  </div>
                  <div className="progress-item__values">
                    <Typography variant="caption">{formatNutrientValue(nutrient, current_totals[nutrient])}</Typography>
                    <Typography variant="caption">목표: {formatNutrientValue(nutrient, targets[nutrient])}</Typography>
                  </div>
                </div>
              ))
            )}
          </div>
        </Paper>

        {/* Nutrient Status */}
        {(Object.keys(deficient_nutrients).length > 0 || Object.keys(excess_nutrients).length > 0) && (
          <Paper className="dashboard__status-section">
            <Typography variant="h6" gutterBottom>영양소 상태</Typography>
            {Object.keys(deficient_nutrients).length > 0 && (
              <div className="status-box">
                <Typography variant="subtitle1" color="warning.main" gutterBottom>부족</Typography>
                <div className="status-box__chips">
                  {Object.entries(deficient_nutrients).map(([n, v]) => <Chip key={n} icon={<TrendingDown />} label={`${formatNutrientName(n)} (-${formatNutrientValue(n, v)})`} size="small" color="warning" variant="outlined" />)}
                </div>
              </div>
            )}
            {Object.keys(excess_nutrients).length > 0 && (
              <div className="status-box">
                <Typography variant="subtitle1" color="error.main" gutterBottom>과잉</Typography>
                <div className="status-box__chips">
                  {Object.entries(excess_nutrients).map(([n, v]) => <Chip key={n} icon={<TrendingUp />} label={`${formatNutrientName(n)} (+${formatNutrientValue(n, v)})`} size="small" color="error" variant="outlined" />)}
                </div>
              </div>
            )}
          </Paper>
        )}

        {/* Meal History */}
        <Paper className="dashboard__history-section">
          <div className="history-section__header">
            <Typography variant="h6">최근 식사 기록</Typography>
            {mealHistory.length > 0 && <Button color="error" size="small" onClick={handleResetDaily}>오늘 기록 전체 삭제</Button>}
          </div>
          {mealHistory.length === 0 ? (
            <Typography className="history-section__empty-text" color="text.secondary">기록된 식사가 없습니다.</Typography>
          ) : (
            <List disablePadding>
              {mealHistory.map((meal, index) => (
                <React.Fragment key={meal.id}>
                  <ListItem secondaryAction={<IconButton edge="end" onClick={() => handleDeleteMeal(meal.id)}><Delete /></IconButton>}>
                    <ListItemText
                      primary={meal.food_name}
                      secondary={`${new Date(meal.logged_at).toLocaleTimeString('ko-KR')} - ${formatNutrientValue('calories', meal.nutrition_data.calories)}, 단백질 ${formatNutrientValue('protein', meal.nutrition_data.protein)}`}
                    />
                  </ListItem>
                  {index < mealHistory.length - 1 && <Divider component="li" />}
                </React.Fragment>
              ))}
            </List>
          )}
        </Paper>
      </div>
    </div>
  );
};

export default NutritionDashboard;