"use client";

import React, { useState, useEffect, useMemo, useRef } from 'react';
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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

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
  const [selectedPartial, setSelectedPartial] = useState<PartialWithChildren | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const isInitialized = useRef(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState("");
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const fetchRootPartials = async () => {
    console.log('fetchRootPartials called', new Date().toISOString());
    try {
      // 루트 파셜 목록 가져오기
      const rootPartials = await api.getPartials(params.version as string, true);
      
      // 루트 파셜을 5개씩 나누어 처리
      const BATCH_SIZE = 5;
      const partialsWithChildren: PartialWithChildren[] = [];
      
      for (let i = 0; i < rootPartials.length; i += BATCH_SIZE) {
        const batch = rootPartials.slice(i, i + BATCH_SIZE);
        
        // 현재 배치의 자식 파셜을 병렬로 로드
        const childrenPromises = batch.map(p => 
          api.getPartialChildren(params.version as string, p.name)
            .then(children => ({
              parentName: p.name,
              children: children.map(c => ({
                ...c,
                isExpanded: true,
                children: [] // 하위 파셜의 자식은 필요할 때 로드
              }))
            }))
            .catch(err => {
              console.error(`Error fetching children for ${p.name}:`, err);
              return {
                parentName: p.name,
                children: []
              };
            })
        );

        // 현재 배치의 로드 완료 대기
        const childrenResults = await Promise.all(childrenPromises);
        
        // 현재 배치의 결과를 partialsWithChildren에 추가
        batch.forEach(p => {
          const childrenResult = childrenResults.find(r => r.parentName === p.name);
          partialsWithChildren.push({
            ...p,
            isExpanded: true,
            children: childrenResult?.children || []
          });
        });

        // 다음 배치 전에 잠시 대기 (서버 부하 방지)
        if (i + BATCH_SIZE < rootPartials.length) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }
      }
      
      setPartials(partialsWithChildren);
    } catch (err) {
      console.error('Error fetching root partials:', err);
      setError('파셜 목록을 불러오는데 실패했습니다.');
    }
  };

  useEffect(() => {
    if (!isInitialized.current) {
      console.log('Initial fetch', new Date().toISOString());
      isInitialized.current = true;
      fetchRootPartials();
    }
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

  const handleToggleExpand = async (partial: PartialWithChildren) => {
    if (!partial.children?.length && !partial.isExpanded) {
      try {
        console.log('Fetching children for:', partial.name);
        const children = await api.getPartialChildren(params.version as string, partial.name);
        const childrenWithExpanded = children.map(c => ({
          ...c,
          isExpanded: true,
          children: [] // 하위 파셜의 자식은 필요할 때 로드
        }));

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
      setIsDrawerOpen(false);
      fetchRootPartials();
      setSnackbar({
        open: true,
        message: "파셜이 성공적으로 생성되었습니다.",
        severity: "success"
      });
    } catch (err) {
      console.error('Error creating partial:', err);
      setSnackbar({
        open: true,
        message: "파셜 생성에 실패했습니다.",
        severity: "error"
      });
    }
  };

  const handleCloseDialog = () => {
    setIsCreateDialogOpen(false);
  };

  const handlePartialClick = (partial: PartialWithChildren) => {
    setSelectedPartial(partial);
    setIsDrawerOpen(true);
  };

  const handleNewPartial = () => {
    setSelectedPartial({
      name: '',
      description: '',
      content: '',
      dependencies: [],
      version: params.version as string,
      layout: '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    });
    setIsDrawerOpen(true);
  };

  const handleSave = async () => {
    if (!selectedPartial) return;

    try {
      const response = await fetch(
        `/api/versions/${params.version}/partials/${selectedPartial.name}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ content: editContent }),
        }
      );

      if (!response.ok) throw new Error("Failed to save");

      setSnackbar({
        open: true,
        message: "파셜이 성공적으로 저장되었습니다.",
        severity: "success"
      });
      setIsEditing(false);
      fetchRootPartials();
    } catch (error) {
      setSnackbar({
        open: true,
        message: "파셜 저장에 실패했습니다.",
        severity: "error"
      });
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setSelectedPartial(null);
    setEditContent("");
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
            onClick={fetchRootPartials}
            startIcon={<RefreshIcon />}
          >
            새로고침
          </Button>
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={handleNewPartial}
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
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
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

      {/* Drawer */}
      <PartialDrawer
        isOpen={isDrawerOpen}
        onClose={() => {
          setIsDrawerOpen(false);
          setSelectedPartial(null);
        }}
        selectedPartial={selectedPartial}
        version={params.version as string}
        onSave={handleCreate}
      />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert 
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
} 