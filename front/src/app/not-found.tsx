'use client';

import { useRouter } from 'next/navigation';
import { Box, Button, Typography } from '@mui/material';

export default function NotFound() {
  const router = useRouter();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '400px',
      }}
    >
      <Typography variant="h4" component="h2" gutterBottom>
        페이지를 찾을 수 없습니다
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        요청하신 페이지가 존재하지 않습니다.
      </Typography>
      <Button
        variant="contained"
        onClick={() => router.push('/')}
        sx={{ mt: 2 }}
      >
        홈으로 돌아가기
      </Button>
    </Box>
  );
} 