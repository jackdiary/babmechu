import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Tabs, 
  Tab, 
  Paper, 
  IconButton, 
  Dialog, 
  DialogTitle, 
  DialogContent,
  useMediaQuery,
  useTheme
} from '@mui/material';
import {
  CameraAlt,
  Dashboard,
  Restaurant,
  Person,
  Videocam,
  TrendingUp,
  Close
} from '@mui/icons-material';
import PopularMenuSidebar from './PopularMenuSidebar';
import './Navigation.css';

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [isPopularMenuOpen, setIsPopularMenuOpen] = useState(false);

  const getValueFromPath = (pathname) => {
    switch (pathname) {
      case '/':
        return 0;
      case '/webcam':
        return 1;
      case '/dashboard':
        return 2;
      case '/recommendations':
        return 3;
      case '/profile':
        return 4;
      default:
        return 0;
    }
  };

  const handleChange = (event, newValue) => {
    switch (newValue) {
      case 0:
        navigate('/');
        break;
      case 1:
        navigate('/webcam');
        break;
      case 2:
        navigate('/dashboard');
        break;
      case 3:
        navigate('/recommendations');
        break;
      case 4:
        navigate('/profile');
        break;
      default:
        navigate('/');
    }
  };

  const handlePopularMenuOpen = () => {
    setIsPopularMenuOpen(true);
  };

  const handlePopularMenuClose = () => {
    setIsPopularMenuOpen(false);
  };

  return (
    <>
      <Paper 
        elevation={1}
        className="navigation-container"
      >
        <div className="navigation-wrapper">
          <Tabs
            value={getValueFromPath(location.pathname)}
            onChange={handleChange}
            scrollButtons="auto"
            allowScrollButtonsMobile
            indicatorColor="primary"
            textColor="primary"
            centered
            className="navigation-tabs"
          >
            <Tab icon={<CameraAlt />} label="음식 업로드" />
            <Tab icon={<Videocam />} label={"(라이브 <예정>)"} />
            <Tab icon={<Dashboard />} label="대시보드" />
            <Tab icon={<Restaurant />} label="추천" />
            <Tab icon={<Person />} label="프로필" />
          </Tabs>
          
          {isMobile && (
            <IconButton 
              onClick={handlePopularMenuOpen}
              className="popular-menu-button"
              color="primary"
            >
              <TrendingUp />
            </IconButton>
          )}
        </div>
      </Paper>

      {/* 모바일용 인기메뉴 모달 */}
      <Dialog
        open={isPopularMenuOpen}
        onClose={handlePopularMenuClose}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            margin: isMobile ? 1 : 3,
            maxHeight: isMobile ? '90vh' : '80vh'
          }
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          실시간 인기 메뉴
          <IconButton onClick={handlePopularMenuClose}>
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent sx={{ padding: 0 }}>
          <div style={{ padding: '0 16px 16px 16px' }}>
            <PopularMenuSidebar isModal={true} />
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default Navigation;