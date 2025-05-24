'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { useMediaQuery } from '@mui/material';
import { createAppTheme } from './index';

type ThemeContextType = {
  isDarkMode: boolean;
  toggleTheme: () => void;
};

const ThemeContext = createContext<ThemeContextType>({
  isDarkMode: false,
  toggleTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // 시스템 테마 감지
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // 로컬 스토리지에서 테마 설정 로드
    const savedTheme = localStorage.getItem('app_settings');
    if (savedTheme) {
      const settings = JSON.parse(savedTheme);
      setIsDarkMode(settings.DARK_MODE ?? prefersDarkMode);
    } else {
      // 저장된 설정이 없으면 시스템 테마 사용
      setIsDarkMode(prefersDarkMode);
    }
  }, [prefersDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode((prev) => !prev);
  };

  const theme = createAppTheme(isDarkMode);

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme }}>
      <MuiThemeProvider theme={theme}>
        <CssBaseline enableColorScheme />
        <style jsx global>{`
          body {
            transition: background-color 0.2s ease-in-out;
          }
          .MuiPaper-root,
          .MuiAppBar-root,
          .MuiDrawer-root,
          .MuiCard-root {
            transition: background-color 0.2s ease-in-out, border-color 0.2s ease-in-out;
          }
          .MuiButton-root,
          .MuiIconButton-root {
            transition: background-color 0.2s ease-in-out, border-color 0.2s ease-in-out;
          }
          .MuiTypography-root {
            transition: color 0.2s ease-in-out;
          }
        `}</style>
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
}; 