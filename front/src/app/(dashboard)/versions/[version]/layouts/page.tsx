"use client";

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  Alert,
  Snackbar,
  TextField,
  InputAdornment,
  Stack,
  Button,
} from '@mui/material';
import { 
  Search,
  Refresh as RefreshIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { Layout } from '@/types/layout';
import { LayoutDrawer } from '@/components/layouts/LayoutDrawer';
import { formatDate } from '@/lib/utils';

export default function LayoutsPage() {
  const params = useParams();
  const api = useApi();
  const [layouts, setLayouts] = useState<Layout[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLayout, setSelectedLayout] = useState<Layout | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const isInitialized = useRef(false);
  const [isLoading, setIsLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error'
  });

  const fetchLayouts = async () => {
    try {
      const layouts = await api.getLayouts(params.version as string);
      const sortedLayouts = layouts.sort((a, b) => a.name.localeCompare(b.name));
      setLayouts(sortedLayouts);
    } catch (error) {
      console.error('Error fetching layouts:', error);
      setError('레이아웃을 불러오는데 실패했습니다. 서버가 실행 중인지 확인해주세요.');
      setLayouts([]);
    }
  };

  useEffect(() => {
    if (!isInitialized.current) {
      isInitialized.current = true;
      fetchLayouts();
    }
  }, [fetchLayouts]);

  const handleRefresh = useCallback(async () => {
    await fetchLayouts();
  }, [fetchLayouts]);

  const handleLayoutClick = (layout: Layout) => {
    setSelectedLayout(layout);
    setIsDrawerOpen(true);
  };

  const handleEdit = useCallback((layout: Layout) => {
    setSelectedLayout(layout);
    setIsDrawerOpen(true);
  }, []);

  const handleAdd = useCallback(() => {
    setSelectedLayout(null);
    setIsDrawerOpen(true);
  }, []);

  const handleDelete = async (layout: Layout) => {
    try {
      setIsLoading(true);
      await api.deleteLayout(params.version as string, layout.name);
      await fetchLayouts();
      setSnackbar({
        open: true,
        message: '레이아웃이 삭제되었습니다.',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error deleting layout:', error);
      setSnackbar({
        open: true,
        message: '레이아웃 삭제에 실패했습니다.',
        severity: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async (layout: Layout) => {
    try {
      setIsLoading(true);
      await fetchLayouts();
      setSelectedLayout(null);
      setIsDrawerOpen(false);
      setSnackbar({
        open: true,
        message: '레이아웃이 저장되었습니다.',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error saving layout:', error);
      setSnackbar({
        open: true,
        message: '레이아웃 저장에 실패했습니다.',
        severity: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const filteredLayouts = layouts.filter(layout =>
    layout.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          레이아웃 관리
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            onClick={handleRefresh}
            startIcon={<RefreshIcon />}
          >
            새로고침
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAdd}
          >
            레이아웃 추가
          </Button>
        </Stack>
      </Box>

      {/* 필터 섹션 */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <TextField
            placeholder="레이아웃 이름 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            size="small"
            sx={{ width: 300 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
          {searchQuery && (
            <Button
              size="small"
              onClick={() => setSearchQuery('')}
            >
              필터 초기화
            </Button>
          )}
        </Stack>
      </Paper>

      {/* 레이아웃 목록 */}
      <Stack spacing={0.5}>
        {filteredLayouts.map((layout) => (
          <Paper
            key={layout.name}
            onClick={() => handleLayoutClick(layout)}
            sx={{
              p: 1.5,
              cursor: 'pointer',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                bgcolor: 'action.hover',
                transform: 'translateY(-2px)',
                boxShadow: (theme) => theme.shadows[4],
              },
              borderLeft: selectedLayout?.name === layout.name ? '2px solid' : 'none',
              borderColor: 'primary.main',
            }}
          >
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                  <Typography variant="h6" sx={{ fontWeight: 500 }}>{layout.name}</Typography>
                  {layout.description && (
                    <Typography variant="body2" color="text.secondary">
                      - {layout.description}
                    </Typography>
                  )}
                </Box>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                    <Typography variant="caption" color="text.secondary">
                      생성: {formatDate(layout.created_at)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      수정: {formatDate(layout.updated_at)}
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </Box>
          </Paper>
        ))}
      </Stack>

      {/* 레이아웃 상세 Drawer */}
      <LayoutDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        selectedLayout={selectedLayout}
        version={params.version as string}
        onSave={handleSave}
        onNew={handleAdd}
        onLayoutClick={handleLayoutClick}
        onDelete={handleDelete}
      />

      {/* 스낵바 */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert 
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
} 