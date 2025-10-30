import { useState, useEffect } from 'react';
import {
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Alert,
  CircularProgress,
  Divider,
  Paper,
} from '@mui/material';
import { Save, CheckCircle } from '@mui/icons-material';
import { profileService } from '../services/api';
import './ProfileSetup.css';

const ProfileSetup = ({ isEdit = false, onProfileCreated }) => {
  const [formData, setFormData] = useState({
    age: '', height: '', weight: '', gender: '', activity_level: '', goal: 'maintain',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [calculatedValues, setCalculatedValues] = useState(null);

  useEffect(() => {
    if (isEdit) {
      loadExistingProfile();
    }
  }, [isEdit]);

  const loadExistingProfile = async () => {
    setLoading(true);
    try {
      const response = await profileService.getProfile();
      const profile = response.data.profile;
      setFormData({
        age: profile.age || '', height: profile.height || '', weight: profile.weight || '',
        gender: profile.gender || '', activity_level: profile.activity_level || '', goal: profile.goal || 'maintain',
      });
      setCalculatedValues({ bmr: profile.bmr, tdee: profile.tdee, nutrition_targets: profile.nutrition_targets });
    } catch (error) {
      console.error('프로필 로딩 실패:', error);
      setError('프로필을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const validateForm = () => {
    const { age, height, weight, gender, activity_level } = formData;
    if (!age || !height || !weight || !gender || !activity_level) {
      setError('모든 필수 항목을 입력해주세요.');
      return false;
    }
    if (age < 10 || age > 100) {
      setError('나이는 10세에서 100세 사이여야 합니다.');
      return false;
    }
    if (height < 100 || height > 250) {
      setError('키는 100cm에서 250cm 사이여야 합니다.');
      return false;
    }
    if (weight < 30 || weight > 300) {
      setError('몸무게는 30kg에서 300kg 사이여야 합니다.');
      return false;
    }
    return true;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const profileData = {
        ...formData,
        age: parseInt(formData.age),
        height: parseFloat(formData.height),
        weight: parseFloat(formData.weight),
      };

      const response = isEdit ? await profileService.updateProfile(profileData) : await profileService.createProfile(profileData);
      setSuccess(isEdit ? '프로필이 성공적으로 업데이트되었습니다!' : '프로필이 성공적으로 생성되었습니다!');
      
      const profile = response.data.profile;
      setCalculatedValues({ bmr: profile.bmr, tdee: profile.tdee, nutrition_targets: profile.nutrition_targets });

      if (onProfileCreated) {
        setTimeout(() => onProfileCreated(), 1500);
      }
    } catch (error) {
      console.error('프로필 저장 실패:', error);
      setError(error.response?.data?.error || '프로필 저장에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const activityLevels = [
    { value: 'low', label: '저활동 (사무직, 운동 거의 안함)' },
    { value: 'moderate', label: '보통활동 (주 3-5회 운동)' },
    { value: 'high', label: '고활동 (주 6-7회 운동 또는 육체노동)' },
  ];

  const goals = [
    { value: 'lose', label: '체중 감량' },
    { value: 'maintain', label: '체중 유지' },
    { value: 'gain', label: '체중 증량' },
  ];

  return (
    <Box className="profile-setup">
      <Typography variant="h4" component="h1" className="profile-setup__title">
        {isEdit ? '프로필 수정' : '초기 프로필 설정'}
      </Typography>
      <Typography variant="body1" color="text.secondary" className="profile-setup__subtitle">
        정확한 영양 정보와 추천을 위해 아래 정보를 입력해주세요.
      </Typography>

      {error && <Alert severity="error" className="profile-setup__alert">{error}</Alert>}
      {success && <Alert severity="success" icon={<CheckCircle />} className="profile-setup__alert">{success}</Alert>}

      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          <div className="form-grid__item form-grid__item--half">
            <TextField fullWidth label="나이" name="age" type="number" value={formData.age} onChange={handleChange} required helperText="만 10-100세" />
          </div>
          <div className="form-grid__item form-grid__item--half">
            <FormControl fullWidth required>
              <InputLabel>성별</InputLabel>
              <Select name="gender" value={formData.gender} onChange={handleChange} label="성별">
                <MenuItem value="M">남성</MenuItem>
                <MenuItem value="F">여성</MenuItem>
              </Select>
            </FormControl>
          </div>
          <div className="form-grid__item form-grid__item--half">
            <TextField fullWidth label="키 (cm)" name="height" type="number" value={formData.height} onChange={handleChange} required helperText="100-250cm" />
          </div>
          <div className="form-grid__item form-grid__item--half">
            <TextField fullWidth label="몸무게 (kg)" name="weight" type="number" value={formData.weight} onChange={handleChange} required helperText="30-300kg" />
          </div>
          <div className="form-grid__item form-grid__item--full">
            <FormControl fullWidth required>
              <InputLabel>활동 수준</InputLabel>
              <Select name="activity_level" value={formData.activity_level} onChange={handleChange} label="활동 수준">
                {activityLevels.map(l => <MenuItem key={l.value} value={l.value}>{l.label}</MenuItem>)}
              </Select>
            </FormControl>
          </div>
          <div className="form-grid__item form-grid__item--full">
            <FormControl fullWidth>
              <InputLabel>목표</InputLabel>
              <Select name="goal" value={formData.goal} onChange={handleChange} label="목표">
                {goals.map(g => <MenuItem key={g.value} value={g.value}>{g.label}</MenuItem>)}
              </Select>
            </FormControl>
          </div>
          <div className="form-grid__item form-grid__item--full profile-setup__submit-button-container">
            <Button type="submit" fullWidth variant="contained" size="large" disabled={loading} startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Save />}>
              {loading ? '저장 중...' : (isEdit ? '프로필 업데이트' : '프로필 생성 및 시작')}
            </Button>
          </div>
        </div>
      </form>

      {calculatedValues && (
        <Paper variant="outlined" className="profile-setup__results">
          <Typography variant="h6" gutterBottom>나의 예상 필요 영양</Typography>
          <div className="results-grid">
            <div className="results-grid__item results-grid__item--half">
              <Typography variant="body2" color="text.secondary">기초대사량 (BMR)</Typography>
              <Typography variant="h5">{calculatedValues.bmr?.toFixed(0)} kcal</Typography>
            </div>
            <div className="results-grid__item results-grid__item--half">
              <Typography variant="body2" color="text.secondary">일일 권장 칼로리 (TDEE)</Typography>
              <Typography variant="h5">{calculatedValues.tdee?.toFixed(0)} kcal</Typography>
            </div>
            <Divider className="results-grid__divider" />
            <div className="results-grid__item results-grid__item--third">
              <Typography variant="body2" color="text.secondary">탄수화물</Typography>
              <Typography variant="h6">{calculatedValues.nutrition_targets.carbohydrates?.toFixed(0)}g</Typography>
            </div>
            <div className="results-grid__item results-grid__item--third">
              <Typography variant="body2" color="text.secondary">단백질</Typography>
              <Typography variant="h6">{calculatedValues.nutrition_targets.protein?.toFixed(0)}g</Typography>
            </div>
            <div className="results-grid__item results-grid__item--third">
              <Typography variant="body2" color="text.secondary">지방</Typography>
              <Typography variant="h6">{calculatedValues.nutrition_targets.fat?.toFixed(0)}g</Typography>
            </div>
          </div>
        </Paper>
      )}
    </Box>
  );
};

export default ProfileSetup;
