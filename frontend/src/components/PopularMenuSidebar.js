import { useState, useEffect, Fragment } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  List,
  ListItem,
  Chip,
  IconButton,
  Divider,
  Collapse
} from '@mui/material';
import {
  TrendingUp,
  Refresh,
  Restaurant,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material';
import './PopularMenuSidebar.css';

// Dummy food data (can be moved to a separate file)
const FOOD_DATABASE = [
  // 한식 (40개)
  '김치찌개', '된장찌개', '부대찌개', '순두부찌개', '감자탕', '삼계탕', '갈비탕', '설렁탕',
  '냉면', '비빔냉면', '물냉면', '비빔밥', '김치볶음밥', '볶음밥', '잡곡밥', '백미밥',
  '불고기', '갈비구이', '삼겹살', '목살구이', '닭갈비', '닭볶음탕', '찜닭', '닭강정',
  '생선구이', '갈치조림', '고등어조림', '동태찌개', '매운탕', '해물탕', '곱창전골', '육개장',
  '김치', '배추김치', '깍두기', '시금치나물', '콩나물무침', '도라지무침', '고사리나물', '꿀떡',
  
  // 중식 (35개)
  '짜장면', '짬뽕', '탕수육', '깐풍기', '양장피', '볶음밥', '차돌짬뽕', '삼선짬뽕',
  '마파두부', '궁보계정', '라조기', '유린기', '고추잡채', '팔보채', '춘장볶음밥', '새우볶음밥',
  '완탕면', '우동', '잡채밥', '중화비빔밥', '깐쇼새우', '멘보샤', '꿔바로우', '동파육',
  '마라탕', '훠궈', '딤섬', '샤오롱바오', '군만두', '물만두', '왕만두', '고기만두',
  '중화냉면', '온면', '칠리새우',
  
  // 일식 (30개)
  '초밥', '사시미', '연어초밥', '참치초밥', '새우초밥', '장어초밥', '광어초밥', '도미초밥',
  '라멘', '돈코츠라멘', '미소라멘', '쇼유라멘', '츠케멘', '우동', '소바', '야키소바',
  '돈카츠', '치킨카츠', '생선까스', '규카츠', '텐동', '가츠동', '규동', '오야코동',
  '타코야키', '오코노미야키', '야키토리', '테리야키', '스키야키', '샤브샤브',
  
  // 추가 아시아 요리 (20개)
  '팟타이', '똠양꿍', '그린커리', '레드커리', '쌀국수', '분짜', '반미', '월남쌈',
  '나시고렝', '미고렝', '렌당', '사테', '락사', '하이난치킨라이스', '바쿠테',
  '김치라면', '신라면', '불닭볶음면', '컵라면', '떡볶이'
];

const PopularMenuSidebar = ({ isModal = false }) => {
  const [popularMenus, setPopularMenus] = useState([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);

  const getCategoryByFood = (foodName) => {
    const koreanFoods = ['김치찌개', '된장찌개', '부대찌개', '순두부찌개', '감자탕', '삼계탕', '갈비탕', '설렁탕', '냉면', '비빔냉면', '물냉면', '비빔밥', '김치볶음밥', '볶음밥', '잡곡밥', '백미밥', '불고기', '갈비구이', '삼겹살', '목살구이', '닭갈비', '닭볶음탕', '찜닭', '닭강정', '생선구이', '갈치조림', '고등어조림', '동태찌개', '매운탕', '해물탕', '곱창전골', '육개장', '김치', '배추김치', '깍두기', '시금치나물', '콩나물무침', '도라지무침', '고사리나물', '꿀떡', '김치라면', '신라면', '불닭볶음면', '컵라면', '떡볶이'];
    const chineseFoods = ['짜장면', '짬뽕', '탕수육', '깐풍기', '양장피', '볶음밥', '차돌짬뽕', '삼선짬뽕', '마파두부', '궁보계정', '라조기', '유린기', '고추잡채', '팔보채', '춘장볶음밥', '새우볶음밥', '완탕면', '우동', '잡채밥', '중화비빔밥', '깐쇼새우', '멘보샤', '꿔바로우', '동파육', '마라탕', '훠궈', '딤섬', '샤오롱바오', '군만두', '물만두', '왕만두', '고기만두', '중화냉면', '온면', '칠리새우'];
    const japaneseFoods = ['초밥', '사시미', '연어초밥', '참치초밥', '새우초밥', '장어초밥', '광어초밥', '도미초밥', '라멘', '돈코츠라멘', '미소라멘', '쇼유라멘', '츠케멘', '우동', '소바', '야키소바', '돈카츠', '치킨카츠', '생선까스', '규카츠', '텐동', '가츠동', '규동', '오야코동', '타코야키', '오코노미야키', '야키토리', '테리야키', '스키야키', '샤브샤브'];
    
    if (koreanFoods.includes(foodName)) return '한식';
    if (chineseFoods.includes(foodName)) return '중식';
    if (japaneseFoods.includes(foodName)) return '일식';
    return '기타';
  };

  const generateRandomMenus = () => {
    const shuffled = [...FOOD_DATABASE].sort(() => 0.5 - Math.random());
    const selected = shuffled.slice(0, 10);
    
    return selected.map((menu, index) => ({
      name: menu,
      rank: index + 1,
      popularity: Math.floor(Math.random() * 50) + 50,
      trend: Math.random() > 0.5 ? 'up' : 'down',
      category: getCategoryByFood(menu)
    }));
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case '한식': return 'error';
      case '중식': return 'warning';
      case '일식': return 'info';
      default: return 'default';
    }
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setPopularMenus(generateRandomMenus());
      setIsRefreshing(false);
    }, 500);
  };

  const handleToggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  useEffect(() => {
    setPopularMenus(generateRandomMenus());
  }, []);

  return (
    <Card className={`sidebar-card ${isModal ? 'modal-sidebar' : ''}`}>
      <CardContent>
        <div className={`sidebar-card__header ${!isExpanded ? 'sidebar-card__header--collapsed' : ''}`}>
          <div className="sidebar-card__title-container" onClick={handleToggleExpand} style={{ cursor: 'pointer' }}>
            <TrendingUp className="sidebar-card__title-icon" />
            <Typography variant="h6" fontWeight="bold">실시간 인기 메뉴</Typography>
            <IconButton size="small" onClick={(e) => { e.stopPropagation(); handleToggleExpand(); }}>
              {isExpanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </div>
          {isExpanded && (
            <IconButton onClick={handleRefresh} disabled={isRefreshing} className={isRefreshing ? 'sidebar-card__refresh-button--spinning' : ''}>
              <Refresh />
            </IconButton>
          )}
        </div>

        <Collapse in={isExpanded} timeout="auto" unmountOnExit>
          <Typography variant="body2" color="text.secondary" className="sidebar-card__subtitle">
            지금 가장 인기있는 메뉴 TOP 10
          </Typography>

          <List dense>
            {popularMenus.map((menu, index) => (
              <Fragment key={`${menu.name}-${index}`}>
                <ListItem className="menu-item">
                  <div className="menu-item__content">
                    <div className={ `menu-item__rank ${menu.rank <= 3 ? 'menu-item__rank--top' : ''}` }>
                      {menu.rank}
                    </div>
                    
                    <div className="menu-item__details">
                      <div className="menu-item__name-container">
                        <Restaurant className="menu-item__name-icon" />
                        <Typography variant="body2" fontWeight="medium">{menu.name}</Typography>
                      </div>
                      
                      <div className="menu-item__meta">
                        <Chip 
                          label={menu.category}
                          size="small"
                          color={getCategoryColor(menu.category)}
                          className="menu-item__category-chip"
                        />
                        <Typography variant="caption" color="text.secondary">인기도 {menu.popularity}</Typography>
                        <div className={ `menu-item__trend ${menu.trend === 'up' ? 'menu-item__trend--up' : 'menu-item__trend--down'}` }>
                          {menu.trend === 'up' ? '↗' : '↘'}
                        </div>
                      </div>
                    </div>
                  </div>
                </ListItem>
                {index < popularMenus.length - 1 && <Divider />}
              </Fragment>
            ))}
          </List>

          <Box className="sidebar-card__info-box">
            <Typography variant="caption" color="text.secondary">
              💡 실시간으로 업데이트되는 인기 메뉴입니다. 새로고침할 때마다 다른 메뉴가 나타납니다!
            </Typography>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default PopularMenuSidebar;
