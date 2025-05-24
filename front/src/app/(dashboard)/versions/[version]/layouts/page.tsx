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
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { Layout } from '@/types/layout';
import { LayoutEditor } from '@/components/features/layouts/LayoutEditor';

export default function LayoutsPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApi();
  const [layouts, setLayouts] = useState<Layout[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  useEffect(() => {
    fetchLayouts();
  }, [params.version]);

  const fetchLayouts = async () => {
    try {
      const data = await api.getLayouts(params.version as string);
      setLayouts(data);
    } catch (err) {
      console.error('Error fetching layouts:', err);
      setError('레이아웃 목록을 불러오는데 실패했습니다.');
    }
  };

  const handleCreate = async (layout: Partial<Layout>) => {
    if (!layout.name?.trim()) {
      setError('레이아웃 이름을 입력해주세요.');
      return;
    }
    if (!layout.content?.trim()) {
      setError('레이아웃 내용을 입력해주세요.');
      return;
    }

    try {
      const createdLayout = await api.createLayout(params.version as string, layout);
      setIsCreateDialogOpen(false);
      fetchLayouts();
      router.push(`/versions/${params.version}/layouts/${createdLayout.name}`);
    } catch (err) {
      console.error('Error creating layout:', err);
      setError('레이아웃 생성에 실패했습니다.');
    }
  };

  const handleCloseDialog = () => {
    setIsCreateDialogOpen(false);
    setError(null);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          레이아웃 목록
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setIsCreateDialogOpen(true)}
        >
          레이아웃 추가
        </Button>
      </Box>

      <Stack spacing={2}>
        {layouts.map((layout) => (
          <Paper
            key={layout.name}
            onClick={() => router.push(`/versions/${params.version}/layouts/${layout.name}`)}
            sx={{
              p: 2,
              cursor: 'pointer',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                bgcolor: 'action.hover',
                transform: 'translateY(-2px)',
                boxShadow: (theme) => theme.shadows[4],
              },
            }}
          >
            <Box>
              <Typography variant="h6">{layout.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                {layout.description}
              </Typography>
            </Box>
          </Paper>
        ))}
      </Stack>

      {/* 생성 다이얼로그 */}
      <Dialog
        open={isCreateDialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
        keepMounted={false}
        disablePortal
        disableEnforceFocus
        disableAutoFocus
      >
        <DialogTitle>레이아웃 생성</DialogTitle>
        <DialogContent dividers>
          <LayoutEditor
            open={isCreateDialogOpen}
            isNew={true}
            layout={{
              name: '',
              description: '',
              content: '',
              version: params.version as string,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            }}
            onSubmit={handleCreate}
            onOpenChange={setIsCreateDialogOpen}
          />
        </DialogContent>
      </Dialog>

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