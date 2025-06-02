"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { useParams } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  Button,
  Snackbar,
  Alert,
  Stack,
  Chip,
  IconButton,
  TextField,
  InputAdornment,
} from '@mui/material';
import { 
  Add as AddIcon, 
  Refresh as RefreshIcon,
  Edit as EditIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  Search,
} from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { PartialTemplate } from '@/types/partial';
import { PartialDrawer } from '@/components/partials/PartialDrawer';
import { formatDate } from '@/lib/utils';

interface PartialWithChildren extends PartialTemplate {
  children?: PartialWithChildren[];
  isExpanded?: boolean;
}

export default function PartialsPage() {
  const params = useParams();
  const api = useApi();
  const [partials, setPartials] = useState<PartialWithChildren[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedPartial, setSelectedPartial] = useState<PartialTemplate | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  const fetchPartials = async () => {
    try {
      setIsLoading(true);
      // 루트 파셜 목록 가져오기 (is_root=true인 파셜만)
      const rootPartials = await api.getPartials(params.version as string, true);
      
      // 루트 파셜을 5개씩 나누어 처리
      const BATCH_SIZE = 5;
      const partialsWithChildren: PartialWithChildren[] = [];
      
      // 재귀적으로 자식 파셜을 로드하는 함수
      const loadChildrenRecursively = async (partial: PartialTemplate, depth: number = 0): Promise<PartialWithChildren> => {
        try {
          // 최대 깊이 제한 (무한 루프 방지)
          if (depth > 10) {
            console.warn(`Maximum depth reached for partial: ${partial.name}`);
            return {
              ...partial,
              isExpanded: false,
              children: []
            };
          }

          // 자식 파셜 목록 조회
          const children = await api.getPartialChildren(params.version as string, partial.name);
          console.log(`[${depth}단계] ${partial.name}의 자식 파셜:`, children);
          
          // 각 자식 파셜에 대해 재귀적으로 하위 파셜 로드
          const childrenWithSubChildren = await Promise.all(
            children.map(child => loadChildrenRecursively(child, depth + 1))
          );

          return {
            ...partial,
            isExpanded: false,
            children: childrenWithSubChildren
          };
        } catch (err) {
          console.error(`Error loading children for ${partial.name}:`, err);
          return {
            ...partial,
            isExpanded: false,
            children: []
          };
        }
      };

      const sortedRootPartials = rootPartials.sort((a, b) => a.name.localeCompare(b.name));

      for (let i = 0; i < sortedRootPartials.length; i += BATCH_SIZE) {
        const batch = sortedRootPartials.slice(i, i + BATCH_SIZE);
        
        // 현재 배치의 파셜들을 재귀적으로 로드
        const batchResults = await Promise.all(
          batch.map(partial => loadChildrenRecursively(partial))
        );
        
        partialsWithChildren.push(...batchResults);

        // 다음 배치 전에 잠시 대기 (서버 부하 방지)
        if (i + BATCH_SIZE < rootPartials.length) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }
      }
      
      setPartials(partialsWithChildren);
    } catch (err) {
      console.error('Error fetching partials:', err);
      setError('파셜 목록을 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPartials();
  }, [params.version]);

  const handleNewPartial = () => {
    setSelectedPartial(null);
    setIsDrawerOpen(true);
  };

  const handlePartialClick = (partial: PartialTemplate) => {
    setSelectedPartial(partial);
    setIsDrawerOpen(true);
  };

  const handlePartialChange = (partial: PartialTemplate) => {
    setSelectedPartial(partial);
  };

  const handleSave = async (partial: Partial<PartialTemplate>) => {
    try {
      setIsLoading(true);
      if (selectedPartial) {
        await api.updatePartial(params.version as string, selectedPartial.name, partial);
      } else {
        await api.createPartial(params.version as string, partial);
      }
      setIsDrawerOpen(false);
      fetchPartials();
      setSnackbar({
        open: true,
        message: selectedPartial ? "파셜이 수정되었습니다." : "파셜이 생성되었습니다.",
        severity: "success"
      });
    } catch (err) {
      console.error('Error saving partial:', err);
      setSnackbar({
        open: true,
        message: "파셜 저장에 실패했습니다.",
        severity: "error"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedPartial) return;

    try {
      setIsLoading(true);
      await api.deletePartial(params.version as string, selectedPartial.name);
      setIsDrawerOpen(false);
      fetchPartials();
      setSnackbar({
        open: true,
        message: "파셜이 삭제되었습니다.",
        severity: "success"
      });
    } catch (err) {
      console.error('Error deleting partial:', err);
      setSnackbar({
        open: true,
        message: "파셜 삭제에 실패했습니다.",
        severity: "error"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleExpand = async (partial: PartialWithChildren) => {
    if (!partial.children?.length && !partial.isExpanded) {
      try {
        // 재귀적으로 자식 파셜을 로드하는 함수
        const loadChildrenRecursively = async (partial: PartialTemplate, depth: number = 0): Promise<PartialWithChildren> => {
          try {
            // 최대 깊이 제한 (무한 루프 방지)
            if (depth > 10) {
              console.warn(`Maximum depth reached for partial: ${partial.name}`);
              return {
                ...partial,
                isExpanded: false,
                children: []
              };
            }

            // 자식 파셜 목록 조회
            const children = await api.getPartialChildren(params.version as string, partial.name);
            console.log(`[${depth}단계] ${partial.name}의 자식 파셜:`, children);
            
            // 각 자식 파셜에 대해 재귀적으로 하위 파셜 로드
            const childrenWithSubChildren = await Promise.all(
              children.map(child => loadChildrenRecursively(child, depth + 1))
            );

            return {
              ...partial,
              isExpanded: false,
              children: childrenWithSubChildren
            };
          } catch (err) {
            console.error(`Error loading children for ${partial.name}:`, err);
            return {
              ...partial,
              isExpanded: false,
              children: []
            };
          }
        };

        const partialWithChildren = await loadChildrenRecursively(partial);
        console.log(`${partial.name}의 전체 하위 파셜:`, partialWithChildren);
        
        // 상태 업데이트 로직 수정
        setPartials(prevPartials => {
          const updatePartial = (partials: PartialWithChildren[]): PartialWithChildren[] => {
            return partials.map(p => {
              if (p.name === partial.name) {
                return {
                  ...partialWithChildren,
                  isExpanded: true
                };
              }
              if (p.children) {
                return {
                  ...p,
                  children: updatePartial(p.children)
                };
              }
              return p;
            });
          };
          return updatePartial(prevPartials);
        });
      } catch (err) {
        console.error('Error fetching children:', err);
        setError('하위 파셜 목록을 불러오는데 실패했습니다.');
      }
    } else {
      // 상태 업데이트 로직 수정
      setPartials(prevPartials => {
        const updatePartial = (partials: PartialWithChildren[]): PartialWithChildren[] => {
          return partials.map(p => {
            if (p.name === partial.name) {
              return { ...p, isExpanded: !p.isExpanded };
            }
            if (p.children) {
              return {
                ...p,
                children: updatePartial(p.children)
              };
            }
            return p;
          });
        };
        return updatePartial(prevPartials);
      });
    }
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
          ml: level * 3,
          position: 'relative',
          '&::before': level > 0 ? {
            content: '""',
            position: 'absolute',
            left: -12,
            top: '50%',
            width: 12,
            height: 2,
            bgcolor: 'divider',
          } : {},
          '&::after': level > 0 ? {
            content: '""',
            position: 'absolute',
            left: -12,
            top: 0,
            width: 2,
            height: '100%',
            bgcolor: 'divider',
          } : {},
        }}
      >
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {partial.children && partial.children.length > 0 && (
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
            )}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 500 }}>
                {partial.name}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {partial.children && partial.children.length > 0 && (
                  <Chip
                    label={`하위 ${partial.children.length}`}
                    size="small"
                    color="primary"
                    variant="outlined"
                    sx={{ 
                      height: 24,
                      '& .MuiChip-label': {
                        px: 1,
                        fontSize: '0.75rem'
                      }
                    }}
                  />
                )}
                {partial.dependencies && partial.dependencies.length > 0 && (
                  <Chip
                    label={`의존 ${partial.dependencies.length}`}
                    size="small"
                    color="warning"
                    variant="outlined"
                    sx={{ 
                      height: 24,
                      '& .MuiChip-label': {
                        px: 1,
                        fontSize: '0.75rem'
                      }
                    }}
                  />
                )}
                {partial.description && (
                  <Typography 
                    variant="body2" 
                    color="text.secondary"
                    sx={{ 
                      fontWeight: 'normal'
                    }}
                  >
                    - {partial.description}
                  </Typography>
                )}
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                <Typography variant="caption" color="text.secondary">
                  생성: {formatDate(partial.created_at || '')}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  수정: {formatDate(partial.updated_at || '')}
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      </Paper>
      {partial.isExpanded && partial.children && partial.children.length > 0 && (
        <Box sx={{ mt: 0.5 }}>
          {partial.children.map(child => renderPartial(child, level + 1))}
        </Box>
      )}
    </Box>
  );

  // 필터링된 파셜 목록
  const filteredPartials = useMemo(() => {
    const filterPartial = (partial: PartialWithChildren): boolean => {
      const matchesSearch = partial.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (partial.description || '').toLowerCase().includes(searchQuery.toLowerCase());
      
      if (partial.children) {
        const hasMatchingChild = partial.children.some(child => filterPartial(child));
        return matchesSearch || hasMatchingChild;
      }
      
      return matchesSearch;
    };

    return partials.filter(filterPartial);
  }, [partials, searchQuery]);

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h1">
          파셜 관리
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleNewPartial}
            disabled={isLoading}
          >
            새로 만들기
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchPartials}
            disabled={isLoading}
          >
            새로고침
          </Button>
        </Box>
      </Box>

      {/* 필터 섹션 */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <TextField
            placeholder="파셜 이름 또는 설명 검색..."
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

      <PartialDrawer
        isOpen={isDrawerOpen}
        onClose={() => {
          setIsDrawerOpen(false);
          setSelectedPartial(null);
        }}
        selectedPartial={selectedPartial}
        version={params.version as string}
        onSave={handleSave}
        onDelete={handleDelete}
        onNew={handleNewPartial}
        onPartialChange={handlePartialChange}
      />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
} 