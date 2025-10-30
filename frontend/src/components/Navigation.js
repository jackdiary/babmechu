import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Tabs, Tab, Paper } from '@mui/material';
import {
  CameraAlt,
  Dashboard,
  Restaurant,
  Person,
  Videocam,
} from '@mui/icons-material';
import './Navigation.css';

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

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

  return (
    <Paper 
      elevation={1}
      className="navigation-container"
    >
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
    </Paper>
  );
};

export default Navigation;