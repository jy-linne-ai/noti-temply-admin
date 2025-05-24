'use client';

import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

export default function DashboardPage() {
  return (
    <Box>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          환영합니다
        </Typography>
        <Typography variant="body1">
          왼쪽 메뉴에서 원하는 기능을 선택하세요.
        </Typography>
      </Paper>
    </Box>
  );
} 