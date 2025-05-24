'use client';

import { Inter } from 'next/font/google';
import { Toaster } from 'react-hot-toast';
import { AppRouterCacheProvider } from '@mui/material-nextjs/v14-appRouter';
import { ThemeProvider } from '@mui/material/styles';
import { createAppTheme } from '@/theme';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>
        <AppRouterCacheProvider>
          <ThemeProvider theme={createAppTheme(false)}>
            {children}
            <Toaster />
          </ThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
} 