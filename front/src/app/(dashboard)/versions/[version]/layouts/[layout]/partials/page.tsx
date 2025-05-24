"use client";

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  Button,
  Snackbar,
  Alert,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { PartialTemplate } from '@/types/partial';
import { Layout } from '@/types/layout';
import { PartialEditor } from '@/components/features/partials/PartialEditor';

export default function PartialsPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApi();
  const [partials, setPartials] = useState<PartialTemplate[]>([]);
  const [layout, setLayout] = useState<Layout | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  useEffect(() => {
    fetchData();
  }, [params.version, params.layout]);

  const fetchData = async () => {
    try {
      const [partialsData, layoutData] = await Promise.all([
        api.getPartials(params.version as string, params.layout as string),
        api.getLayout(params.version as string, params.layout as string),
      ]);
      setPartials(partialsData);
      setLayout(layoutData);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('데이터를 불러오는데 실패했습니다.');
    }
  };

  const handleCreate = async (data: { name: string; description: string; content: string }) => {
    try {
      await api.createPartial(params.version as string, params.layout as string, {
        ...data,
        version: params.version as string,
        layout: params.layout as string,
      });
      setIsCreateDialogOpen(false);
      fetchData();
    } catch (err) {
      console.error('Error creating partial:', err);
      setError('파셜 생성에 실패했습니다.');
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" component="h1">
            파셜 목록
          </Typography>
          {layout && (
            <Typography variant="subtitle1" color="text.secondary">
              {layout.name} 레이아웃의 파셜
            </Typography>
          )}
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setIsCreateDialogOpen(true)}
        >
          파셜 추가
        </Button>
      </Box>

      <Box sx={{ display: 'grid', gap: 2 }}>
        {partials.map((partial) => (
          <Paper
            key={partial.name}
            sx={{
              p: 2,
              cursor: 'pointer',
              '&:hover': {
                bgcolor: 'action.hover',
              },
            }}
            onClick={() => router.push(`/versions/${params.version}/layouts/${params.layout}/partials/${partial.name}`)}
          >
            <Typography variant="h6">{partial.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              {partial.description}
            </Typography>
          </Paper>
        ))}
      </Box>

      {/* 생성 다이얼로그 */}
      <PartialEditor
        partial={{
          name: '',
          description: '',
          content: '',
          version: params.version as string,
          layout: params.layout as string,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }}
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        onSubmit={handleCreate}
        isNew={true}
      />

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