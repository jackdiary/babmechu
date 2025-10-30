import './App.css';
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Box, Paper, Grid } from '@mui/material';

// 컴포넌트 임포트
import ProfileSetup from './components/ProfileSetup';
import FoodClassification from './components/FoodClassification';
import NutritionDashboard from './components/NutritionDashboard';
import Recommendations from './components/Recommendations';
import PopularMenuSidebar from './components/PopularMenuSidebar';
import Navigation from './components/Navigation';

// API 서비스
import { profileService } from './services/api';

function App() {
  const [hasProfile, setHasProfile] = useState(false);
  const [loading, setLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  useEffect(() => {
    checkProfile();
  }, []);

  const checkProfile = async () => {
    try {
      const response = await profileService.checkProfile();
      setHasProfile(response.data.has_profile);
    } catch (error) {
      console.error('프로필 확인 실패:', error);
      setHasProfile(false);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileCreated = () => {
    setHasProfile(true);
  };

  if (loading) {
    return (
      <>
        <Box className="loading-container">
          <Typography variant="h6">로딩 중...</Typography>
        </Box>
      </>
    );
  }

  return (
    <div className="app-container">
      <Router>
        <Box>
          <AppBar position="static" className="app-bar">
            <Toolbar className="toolbar">
              {/* 로고 이미지 */}
              <Box className="logo-container">
                <img 
                  src="/logo.png" 
                  alt="밥메추 로고" 
                  className="logo-image"
                />
              </Box>
              
              <Typography variant="h3" component="div" className="heading">
                밥메추 - 오늘 부족한 영양소를 추천받자!
              </Typography>
            </Toolbar>
          </AppBar>

          <Container component="div" className="main-content" maxWidth="xl">
            <Paper elevation={3} className="main-paper">
              {!hasProfile ? (
                <ProfileSetup onProfileCreated={handleProfileCreated} />
              ) : (
                <>
                  <Navigation />
                  <Box className="routes-container">
                    <Grid container spacing={3} className="main-grid">
                      <Grid item xs={12} lg={8} className="content-grid">
                        <Routes>
                          <Route path="/" element={<FoodClassification onMealLog={handleRefresh} />} />
                          <Route path="/dashboard" element={<NutritionDashboard refreshTrigger={refreshTrigger} />} />
                          <Route path="/recommendations" element={<Recommendations />} />
                          <Route path="/profile" element={
                            <ProfileSetup
                              isEdit={true}
                              onProfileCreated={handleProfileCreated}
                            />
                          } />
                        </Routes>
                      </Grid>
                      {/* PopularMenuSidebar is now outside the main grid to allow for fixed positioning */}
                    </Grid>
                  </Box>
                  <PopularMenuSidebar />

                </>
              )}
            </Paper>
          </Container>
          
          <Box component="footer" className="footer">
            <Typography variant="body2">
              © {new Date().getFullYear()} 밥메추. All rights reserved.
            </Typography>
          </Box>
        </Box>
      </Router>
    </div>
  );
}

export default App;