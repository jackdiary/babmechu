import './App.css';
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Box, Paper, Grid, useMediaQuery, useTheme, createTheme, ThemeProvider } from '@mui/material';

// 컴포넌트 임포트
import ProfileSetup from './components/ProfileSetup';
import FoodClassification from './components/FoodClassification';
import NutritionDashboard from './components/NutritionDashboard';
import Recommendations from './components/Recommendations';
import PopularMenuSidebar from './components/PopularMenuSidebar';
import Navigation from './components/Navigation';

// API 서비스
import { profileService } from './services/api';

// 로고 클릭 컴포넌트 (Router 내부에서 사용)
const ClickableLogo = ({ isMobile }) => {
  const navigate = useNavigate();
  
  const handleLogoClick = () => {
    navigate('/');
  };

  return (
    <img 
      src="/logo.png" 
      alt="밥메추 로고" 
      className="logo-image"
      onClick={handleLogoClick}
      style={{
        width: isMobile ? '80px' : '130px',
        height: isMobile ? '80px' : '130px',
        minWidth: isMobile ? '80px' : '130px',
        minHeight: isMobile ? '80px' : '130px',
        maxWidth: isMobile ? '80px' : '130px',
        maxHeight: isMobile ? '80px' : '130px',
        borderRadius: '50%',
        objectFit: 'cover',
        display: 'block',
        flexShrink: 0,
        cursor: 'pointer',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease'
      }}
      onMouseEnter={(e) => {
        e.target.style.transform = 'scale(1.05)';
        e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
      }}
      onMouseLeave={(e) => {
        e.target.style.transform = 'scale(1)';
        e.target.style.boxShadow = 'none';
      }}
    />
  );
};

// 빈 LogoComponent (Router 외부에서 사용)
const LogoComponent = () => null;

// Material-UI 테마 생성 - CSS 우선순위 해결
const customTheme = createTheme({
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage: `url("${process.env.PUBLIC_URL}/ba.jpg") !important`,
          backgroundSize: 'cover !important',
          backgroundPosition: 'center !important',
          backgroundRepeat: 'no-repeat !important',
          backgroundAttachment: 'fixed !important',
        }
      }
    }
  }
});

function App() {
  const [hasProfile, setHasProfile] = useState(false);
  const [loading, setLoading] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

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
    <ThemeProvider theme={customTheme}>
      <div 
        className="app-container"
        style={{
          backgroundImage: `url("${process.env.PUBLIC_URL}/ba.jpg") !important`,
          backgroundSize: 'cover !important',
          backgroundPosition: 'center !important',
          backgroundRepeat: 'no-repeat !important',
          backgroundAttachment: 'fixed !important',
          minHeight: '100vh !important',
          width: '100% !important',
          margin: '0 auto !important',
          position: 'relative !important'
        }}
      >
        <Router>
          <LogoComponent isMobile={isMobile} />
        <Box>
          <AppBar position="static" className="app-bar">
            <Toolbar className="toolbar">
              {/* 로고 이미지 */}
              <Box 
                className="logo-container"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  width: isMobile ? '80px' : '130px',
                  height: isMobile ? '80px' : '130px',
                  minWidth: isMobile ? '80px' : '130px',
                  minHeight: isMobile ? '80px' : '130px',
                  maxWidth: isMobile ? '80px' : '130px',
                  maxHeight: isMobile ? '80px' : '130px',
                  overflow: 'hidden',
                  cursor: 'pointer'
                }}
              >
                <ClickableLogo isMobile={isMobile} />
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
                  {!isMobile && <PopularMenuSidebar />}

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
    </ThemeProvider>
  );
}

export default App;