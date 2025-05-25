"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
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
  Chip,
  IconButton,
  TextField,
  InputAdornment,
} from '@mui/material';
import { Add as AddIcon, ExpandMore as ExpandMoreIcon, ExpandLess as ExpandLessIcon, ViewList as ViewListIcon, Refresh as RefreshIcon, Search } from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { PartialTemplate } from '@/types/partial';
import { PartialEditor } from '@/components/features/partials/PartialEditor';
import { PartialDrawer } from '@/components/partials/PartialDrawer';
import { formatDate } from '@/lib/utils';

interface PartialWithChildren extends PartialTemplate {
  children?: PartialWithChildren[];
  isExpanded?: boolean;
}

export default function PartialsPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const api = useApi();
  const [partials, setPartials] = useState<PartialWithChildren[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPartial, setSelectedPartial] = useState<PartialTemplate | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  useEffect(() => {
    fetchRootPartials();
  }, [params.version]);

  // 필터링된 파셜 목록
  const filteredPartials = useMemo(() => {
    const filterPartial = (partial: PartialWithChildren): boolean => {
      const matchesSearch = partial.name.toLowerCase().includes(searchQuery.toLowerCase());
      if (!partial.children) return matchesSearch;
      
      const filteredChildren = partial.children
        .map(child => filterPartial(child))
        .filter(Boolean);
      
      return matchesSearch || filteredChildren.length > 0;
    };

    return partials.filter(filterPartial);
  }, [partials, searchQuery]);

  const fetchRootPartials = async () => {
    try {
      const data = await api.getPartials('root', true);
      // 각 파셜의 하위 파셜 개수를 가져옵니다
      const partialsWithChildren = await Promise.all(
        data.map(async (p) => {
          const children = await api.getPartialChildren(params.version as string, p.name);
          return {
            ...p,
            isExpanded: true,
            children: children.map(c => ({ ...c, isExpanded: true }))
          };
        })
      );
      setPartials(partialsWithChildren);
    } catch (err) {
      console.error('Error fetching root partials:', err);
      setError('파셜 목록을 불러오는데 실패했습니다.');
    }
  };

  const fetchChildren = async (partial: PartialWithChildren) => {
    try {
      const children = await api.getPartialChildren(params.version as string, partial.name);
      const childrenWithExpanded = await Promise.all(
        children.map(async (child) => {
          const childWithChildren: PartialWithChildren = { ...child, isExpanded: true };
          // 재귀적으로 하위 파셜을 가져옵니다
          const grandChildren = await api.getPartialChildren(params.version as string, child.name);
          if (grandChildren.length > 0) {
            childWithChildren.children = await Promise.all(
              grandChildren.map(async (grandChild) => ({
                ...grandChild,
                isExpanded: true,
                children: await fetchChildrenRecursively(grandChild)
              }))
            );
          }
          return childWithChildren;
        })
      );

      const updatedPartials = partials.map(p => {
        if (p.name === partial.name) {
          return {
            ...p,
            children: childrenWithExpanded,
            isExpanded: true
          };
        }
        return p;
      });
      setPartials(updatedPartials);
    } catch (err) {
      console.error('Error fetching children:', err);
      setError('하위 파셜 목록을 불러오는데 실패했습니다.');
    }
  };

  // 재귀적으로 하위 파셜을 가져오는 헬퍼 함수
  const fetchChildrenRecursively = async (partial: PartialTemplate): Promise<PartialWithChildren[]> => {
    try {
      const children = await api.getPartialChildren(params.version as string, partial.name);
      if (children.length === 0) return [];

      return await Promise.all(
        children.map(async (child) => ({
          ...child,
          isExpanded: true,
          children: await fetchChildrenRecursively(child)
        }))
      );
    } catch (err) {
      console.error('Error fetching children recursively:', err);
      return [];
    }
  };

  const handleToggleExpand = (partial: PartialWithChildren) => {
    if (!partial.children && !partial.isExpanded) {
      fetchChildren(partial);
    } else {
      const updatedPartials = partials.map(p => {
        if (p.name === partial.name) {
          return { ...p, isExpanded: !p.isExpanded };
        }
        return p;
      });
      setPartials(updatedPartials);
    }
  };

  const handleCreate = async (partial: Partial<PartialTemplate>) => {
    try {
      const createdPartial = await api.createPartial(params.version as string, partial);
      setIsCreateDialogOpen(false);
      fetchRootPartials();
      router.push(`/versions/${params.version}/partials/${createdPartial.name}`);
    } catch (err) {
      console.error('Error creating partial:', err);
      setError('파셜 생성에 실패했습니다.');
    }
  };

  const handleCloseDialog = () => {
    setIsCreateDialogOpen(false);
  };

  const handlePartialClick = (partial: PartialTemplate) => {
    setSelectedPartial(partial);
    setIsDrawerOpen(true);
  };

  const renderPartial = (partial: PartialWithChildren, level: number = 0) => (
    <Box key={partial.name}>
      <Paper
        onClick={() => handlePartialClick(partial)}
        sx={{
          p: 1.5,
          cursor: 'pointer',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            bgcolor: 'action.hover',
            transform: 'translateY(-2px)',
            boxShadow: (theme) => theme.shadows[4],
          },
          ml: level * 2,
          borderLeft: level > 0 ? '2px solid' : 'none',
          borderColor: 'primary.main',
          position: 'relative',
          '&::before': level > 0 ? {
            content: '""',
            position: 'absolute',
            left: -2,
            top: '50%',
            width: 8,
            height: 2,
            bgcolor: 'primary.main',
          } : {},
        }}
      >
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                handleToggleExpand(partial);
              }}
              sx={{
                color: 'primary.main',
                '&:hover': {
                  bgcolor: 'primary.light',
                },
              }}
            >
              {partial.isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 500 }}>{partial.name}</Typography>
              {partial.description && (
                <Typography variant="body2" color="text.secondary">
                  - {partial.description}
                </Typography>
              )}
              {partial.children && partial.children.length > 0 && (
                <Chip
                  label={`${partial.children.length}개의 하위 파셜`}
                  size="small"
                  color="primary"
                  variant="outlined"
                  sx={{ ml: 'auto' }}
                />
              )}
            </Box>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                <Typography variant="caption" color="text.secondary">
                  생성: {formatDate(partial.created_at)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  수정: {formatDate(partial.updated_at)}
                </Typography>
              </Box>
            </Box>
          </Box>
          {partial.dependencies && partial.dependencies.length > 0 && (
            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 1 }}>
              {partial.dependencies.map((dep) => (
                <Chip
                  key={dep}
                  label={dep}
                  size="small"
                  color="warning"
                  variant="outlined"
                />
              ))}
            </Box>
          )}
        </Box>
      </Paper>
      {partial.isExpanded && partial.children && (
        <Box sx={{ mt: 0.5 }}>
          {partial.children.map(child => renderPartial(child, level + 1))}
        </Box>
      )}
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          파셜 관리
        </Typography>
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            onClick={() => {
              setPartials([]);
              fetchRootPartials();
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
            파셜 추가
          </Button>
        </Stack>
      </Box>

      {/* 필터 섹션 */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <TextField
            placeholder="파셜 이름 검색..."
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

      <Stack spacing={0.5}>
        {filteredPartials.map(partial => renderPartial(partial))}
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
        <DialogTitle>파셜 생성</DialogTitle>
        <DialogContent dividers>
          <PartialEditor
            isNew={true}
            partial={{
              id: '',
              name: '',
              description: '',
              content: '',
              dependencies: [],
              version: params.version as string,
              layout: '',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            }}
            open={isCreateDialogOpen}
            onOpenChange={setIsCreateDialogOpen}
            onSubmit={handleCreate}
            version={params.version as string}
          />
        </DialogContent>
      </Dialog>

      {/* Drawer */}
      <PartialDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        selectedPartial={selectedPartial}
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