"use client";

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Alert,
  Snackbar,
  Divider,
  TextField,
  InputAdornment,
  Stack,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
} from '@mui/material';
import { 
  Search,
  ViewList as ViewListIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { Layout } from '@/types/layout';
import { LayoutEditor } from '@/components/features/layouts/LayoutEditor';
import { LayoutDrawer } from '@/components/layouts/LayoutDrawer';
import { formatDate } from '@/lib/utils';

export default function LayoutsPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApi();
  const [layouts, setLayouts] = useState<Layout[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedLayout, setSelectedLayout] = useState<Layout | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

    const fetchLayouts = async () => {
      try {
      const data = await api.getLayouts(params.version as string);
      setLayouts(data);
    } catch (err) {
      console.error('Error fetching layouts:', err);
      setError('레이아웃 목록을 불러오는데 실패했습니다.');
      }
    };

  useEffect(() => {
    fetchLayouts();
  }, [params.version]);

  const handleLayoutClick = (layout: Layout) => {
    setSelectedLayout(layout);
    setIsDrawerOpen(true);
  };

  const filteredLayouts = layouts.filter(layout =>
    layout.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreate = async (layout: Partial<Layout>) => {
    try {
      const createdLayout = await api.createLayout(params.version as string, {
        ...layout,
        version: params.version as string,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
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
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          레이아웃 관리
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            onClick={() => {
              setLayouts([]);
              fetchLayouts();
            }}
            startIcon={<RefreshIcon />}
          >
            새로고침
          </Button>
        <Button
          variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setIsCreateDialogOpen(true)}
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
              borderLeft: '2px solid',
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
            isNew={true}
            layout={{
              name: '',
              description: '',
              content: '',
              version: params.version as string,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            }}
            open={isCreateDialogOpen}
            onOpenChange={setIsCreateDialogOpen}
            onSubmit={handleCreate}
            />
        </DialogContent>
      </Dialog>

      {/* 레이아웃 상세 Drawer */}
      <LayoutDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        selectedLayout={selectedLayout}
        version={params.version as string}
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