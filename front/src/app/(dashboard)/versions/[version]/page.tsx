'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Alert,
  Snackbar,
  Button,
} from '@mui/material';
import { useApi } from '@/lib/api';
import { VersionInfo } from '@/types/version';

export default function VersionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApi();
  const [version, setVersion] = useState<VersionInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, [params.version]);

  const fetchData = async () => {
    try {
      const data = await api.getVersion(params.version as string);
      setVersion(data);
    } catch (err) {
      setError('데이터를 불러오는데 실패했습니다.');
    }
  };

  const handleDashboardClick = () => {
    router.push(`/versions/${params.version}/dashboard`);
  };

  const handleVersionChange = async (newVersion: string) => {
    try {
      setIsLoading(true);
      const updatedVersion = await api.updateVersion(version, newVersion);
      router.push(`/versions/${updatedVersion.version}`);
    } catch (err) {
      console.error('Error updating version:', err);
      setError('버전 업데이트에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!version) {
    return null;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1">
          {version.version} 버전 정보
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
          {version.description}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              버전 상세 정보
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              생성일: {new Date(version.created_at).toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              수정일: {new Date(version.updated_at).toLocaleString()}
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={handleDashboardClick}
              sx={{ mt: 2 }}
            >
              대시보드로 이동
            </Button>
          </Paper>
        </Grid>
      </Grid>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
} 