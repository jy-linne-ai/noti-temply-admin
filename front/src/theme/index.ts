import { createTheme, ThemeOptions } from '@mui/material/styles';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

// 라이트 테마 설정
const lightTheme: ThemeOptions = {
  typography: {
    fontFamily: inter.style.fontFamily,
  },
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
};

// 다크 테마 설정
const darkTheme: ThemeOptions = {
  typography: {
    fontFamily: inter.style.fontFamily,
  },
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
};

// 테마 생성 함수
export const createAppTheme = (isDarkMode: boolean) => {
  return createTheme(isDarkMode ? darkTheme : lightTheme);
}; 