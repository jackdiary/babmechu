import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  Restaurant,
  Refresh,
  ThumbUp,
  ThumbDown,
  ExpandMore,
  ExpandLess,
  Lightbulb,
  CheckCircle,
} from '@mui/icons-material';
import { recommendationService, intakeService } from '../services/api';
import './Recommendations.css';

const Recommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [guidelines, setGuidelines] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [selectedFood, setSelectedFood] = useState('');
  const [feedbackType, setFeedbackType] = useState('');
  const [feedbackComment, setFeedbackComment] = useState('');

  const [expandedCards, setExpandedCards] = useState({});
  const [guidelinesExpanded, setGuidelinesExpanded] = useState(false);

  useEffect(() => {
    loadRecommendations();
    loadGuidelines();
  }, []);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      setError('');

      const [recsResponse, analysisResponse] = await Promise.all([
        recommendationService.getRecommendations(3),
        recommendationService.getNutritionalAnalysis()
      ]);

      setRecommendations(recsResponse.data.recommendations || []);
      setAnalysis(analysisResponse.data.analysis);
    } catch (err) {
      console.error('추천 로딩 실패:', err);
      if (err.response?.status === 400) {
        setError('프로필을 먼저 설정해주세요.');
      } else {
        setError('추천을 불러오는데 실패했습니다.');
      }
    } finally {
      setLoading(false);
    }
  };

  const loadGuidelines = async () => {
    try {
      const response = await recommendationService.getDietaryGuidelines();
      setGuidelines(response.data.guidelines);
    } catch (err) {
      console.error('가이드라인 로딩 실패:', err);
    }
  };

  const handleSelectRecommendation = async (foodName) => {
    try {
      await intakeService.logMeal(foodName, 100);
      alert(`${foodName}이(가) 성공적으로 기록되었습니다!`);
      loadRecommendations();
    } catch (err) {
      console.error('추천 음식 기록 실패:', err);
      setError('음식 기록에 실패했습니다.');
    }
  };

  const handleFeedback = (foodName, type) => {
    setSelectedFood(foodName);
    setFeedbackType(type);
    setFeedbackOpen(true);
  };

  const submitFeedback = async () => {
    try {
      await recommendationService.submitFeedback(selectedFood, feedbackType, feedbackComment);
      setFeedbackOpen(false);
      setFeedbackComment('');
      alert('피드백이 제출되었습니다!');
    } catch (err) {
      console.error('피드백 제출 실패:', err);
      setError('피드백 제출에 실패했습니다.');
    }
  };

  const toggleCardExpansion = (index) => {
    setExpandedCards(prev => ({ ...prev, [index]: !prev[index] }));
  };

  const getAnalysisStatusColor = (status) => {
    const colorMap = { excellent: 'success', good: 'info', fair: 'warning' };
    return colorMap[status] || 'error';
  };

  const getAnalysisStatusText = (status) => {
    const textMap = { excellent: '우수', good: '양호', fair: '보통' };
    return textMap[status] || '개선 필요';
  };

  if (loading) {
    return <div className="recommendations-loader"><CircularProgress /></div>;
  }

  return (
    <div className="recommendations-page">
      <div className="recommendations-page__header">
        <div className="recommendations-page__title-container">
          <Restaurant className="color-primary" />
          <Typography variant="h4">식사 추천</Typography>
        </div>
        <Button variant="outlined" startIcon={<Refresh />} onClick={loadRecommendations}>새로고침</Button>
      </div>

      {error && <Alert severity="error" className="recommendations-page__alert">{error}</Alert>}

      {analysis && (
        <Card className="analysis-card">
          <CardContent>
            <Typography variant="h6" gutterBottom>현재 영양 상태</Typography>
            <div className="analysis-grid">
              <div className="analysis-grid__item">
                <Typography variant="h4" className={`color-${getAnalysisStatusColor(analysis.summary.overall_status)}`}>{analysis.summary.nutrition_score}</Typography>
                <Typography variant="body2" color="text.secondary">영양 점수</Typography>
                <Chip label={getAnalysisStatusText(analysis.summary.overall_status)} color={getAnalysisStatusColor(analysis.summary.overall_status)} size="small" />
              </div>
              <div className="analysis-grid__item">
                <Typography variant="h4" className="color-success">{analysis.summary.balanced_nutrients}</Typography>
                <Typography variant="body2" color="text.secondary">균형 잡힌 영양소</Typography>
              </div>
              <div className="analysis-grid__item">
                <Typography variant="h4" className="color-error">{analysis.summary.deficient_nutrients}</Typography>
                <Typography variant="body2" color="text.secondary">부족한 영양소</Typography>
              </div>
              <div className="analysis-grid__item">
                <Typography variant="h4" className="color-warning">{analysis.summary.excess_nutrients}</Typography>
                <Typography variant="body2" color="text.secondary">과잉 영양소</Typography>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {recommendations.length === 0 ? (
        <Card>
          <CardContent>
            <div className="recommendations-empty-state">
              <Restaurant className="recommendations-empty-state__icon" />
              <Typography variant="h6" color="text.secondary">현재 추천할 수 있는 메뉴가 없습니다</Typography>
              <Typography variant="body2" color="text.secondary">더 많은 식사를 기록하거나 나중에 다시 확인해보세요</Typography>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="recommendations-grid">
          {recommendations.map((rec, index) => (
            <Card key={index} className="recommendation-card">
              <CardContent className="recommendation-card__content">
                <Typography variant="h6" gutterBottom>{rec.food_name}</Typography>
                <div className="recommendation-card__header">
                  <Chip label={`추천 점수: ${rec.score}`} color="primary" size="small" className="recommendation-card__score-chip" />
                  <Typography variant="body2" color="text.secondary">1회 제공량: {rec.serving_size}g</Typography>
                </div>
                <Typography variant="body2" color="text.secondary" className="recommendation-card__reasoning">{rec.reasoning}</Typography>
                {rec.benefits?.length > 0 && (
                  <div className="recommendation-card__benefits">
                    <Typography variant="body2" gutterBottom>영양상 이점:</Typography>
                    <div className="recommendation-card__benefits-chips">
                      {rec.benefits.map((benefit, idx) => <Chip key={idx} label={benefit} size="small" variant="outlined" color="success" />)}
                    </div>
                  </div>
                )}
                <div>
                  <Button size="small" onClick={() => toggleCardExpansion(index)} endIcon={expandedCards[index] ? <ExpandLess /> : <ExpandMore />}>영양 정보</Button>
                  <Collapse in={expandedCards[index]}>
                    <div className="nutrition-info__grid">
                      {Object.entries(rec.nutrition).map(([key, val]) => (
                        <div key={key}>
                          <Typography variant="caption" display="block">{val.display_name}</Typography>
                          <Typography variant="body2">{val.formatted}</Typography>
                        </div>
                      ))}
                    </div>
                  </Collapse>
                </div>
              </CardContent>
              <CardActions>
                <Button variant="contained" fullWidth onClick={() => handleSelectRecommendation(rec.food_name)} startIcon={<CheckCircle />}>이 음식 선택</Button>
              </CardActions>
              <CardActions>
                <Button size="small" startIcon={<ThumbUp />} onClick={() => handleFeedback(rec.food_name, 'liked')}>좋아요</Button>
                <Button size="small" startIcon={<ThumbDown />} onClick={() => handleFeedback(rec.food_name, 'disliked')}>별로예요</Button>
              </CardActions>
            </Card>
          ))}
        </div>
      )}

      {guidelines && (
        <Card className="guidelines-card">
          <CardContent>
            <div className="guidelines-card__header">
              <div className="guidelines-card__title-container">
                <Lightbulb className="guidelines-card__title-icon" />
                <Typography variant="h6">{guidelines.title}</Typography>
              </div>
              <IconButton onClick={() => setGuidelinesExpanded(!guidelinesExpanded)}>{guidelinesExpanded ? <ExpandLess /> : <ExpandMore />}</IconButton>
            </div>
            {guidelines.nutrition_score && (
              <div className="guidelines-card__chip-container">
                <Chip label={`영양 점수: ${guidelines.nutrition_score} (${getAnalysisStatusText(guidelines.overall_status)})`} color={getAnalysisStatusColor(guidelines.overall_status)} />
              </div>
            )}
            <Collapse in={guidelinesExpanded}>
              <div className="guidelines-card__collapse-content">
                {guidelines.guidelines?.length > 0 && (
                  <div className="guidelines-card__list-container">
                    <Typography variant="subtitle2" gutterBottom>권장사항:</Typography>
                    <List dense>{guidelines.guidelines.map((g, i) => <ListItem key={i}><ListItemText primary={`• ${g}`} /></ListItem>)}</List>
                  </div>
                )}
                {guidelines.tips?.length > 0 && (
                  <div className="guidelines-card__list-container">
                    <Typography variant="subtitle2" gutterBottom>실용적인 팁:</Typography>
                    <List dense>{guidelines.tips.map((t, i) => <ListItem key={i}><ListItemText primary={`• ${t}`} /></ListItem>)}</List>
                  </div>
                )}
              </div>
            </Collapse>
          </CardContent>
        </Card>
      )}

      <Dialog open={feedbackOpen} onClose={() => setFeedbackOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{selectedFood}에 대한 피드백</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" className="feedback-dialog__subtitle">이 추천에 대한 의견을 알려주세요. 더 나은 추천을 위해 활용됩니다.</Typography>
          <TextField fullWidth multiline rows={3} placeholder="추가 의견이 있다면 입력해주세요 (선택사항)" value={feedbackComment} onChange={(e) => setFeedbackComment(e.target.value)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackOpen(false)}>취소</Button>
          <Button onClick={submitFeedback} variant="contained">피드백 제출</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default Recommendations;