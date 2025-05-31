'use client';

import React, { useState, useEffect, useCallback, useMemo, Component } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  Alert,
  Snackbar,
  IconButton,
  Chip,
  Button,

  Stack,
  TextField,
  InputAdornment,
} from '@mui/material';
import { 
  ExpandMore, 
  ExpandLess, 
  Search as SearchIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { TemplateComponent } from '@/types/template';
import { TemplateDrawer } from '@/components/templates/TemplateDrawer';
import { formatDate } from '@/lib/utils';

export default function TemplatesPage() {
  const params = useParams();
  const api = useApi();
  const [defaultComponentNames, setDefaultComponentNames] = useState<string[]>([]);
  const [templates, setTemplates] = useState<Record<string,number>>({});
  const [templateComponents, setTemplateComponents] = useState<Record<string, TemplateComponent[]>>({});
  const [templateExpanded, setTemplateExpanded] = useState<Record<string, boolean>>({});
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  // 필터링 상태
  const [searchQuery, setSearchQuery] = useState('');
  

  const loadDefaultComponentNames = useCallback(async () => {
    try {
      const defaultComponentNames = await api.getDefaultComponentNames();
      if (!Array.isArray(defaultComponentNames) || defaultComponentNames.length === 0) {
        throw new Error('Failed to load default component names');
      }
      
      setDefaultComponentNames(defaultComponentNames);
      return defaultComponentNames;
    } catch (err) {
      console.error('Error loading default component names:', err);
      setError('Error loading default component names.');
      throw err;
    }
  }, [api]);

  // 템플릿 컴포넌트 로드
  const loadTemplateComponents = useCallback(async (templateName: string, componentNames: string[]) => {
    try {
      if (componentNames.length === 0) {
        throw new Error('Default component names not loaded');
      }

      const components = await api.getTemplateComponents(
        params.version as string,
        templateName
      );
      
      if (!Array.isArray(components)) {
        throw new Error('Invalid API response');
      }

      const componentMap = new Map(components.map(comp => {
        return [comp.component, comp];
      }));
      
      const sortedComponents: TemplateComponent[] = [];
      for (const componentName of componentNames) {
        const component = componentMap.get(componentName);
        if (component) {
          sortedComponents.push(component);
        }
      }
      setTemplateComponents(prev => ({
        ...prev,
        [templateName]: sortedComponents
      }));

      
    } catch (err) {
      console.error(`Error loading components for template ${templateName}:`, err);
    }
  }, [params.version, api]);

  // 새로고침
  const handleRefresh = useCallback(async (componentNames: string[]) => {
    try {
      setError(null);
    
      setTemplates({});
      setTemplateComponents({});
      setTemplateExpanded({});
      
      const templateNames = await api.getTemplateComponentCounts(params.version as string);
      const sortedTemplateNames = Object.keys(templateNames).sort();
      setTemplates(templateNames);

      const maxConcurrent = 5;
      let currentIndex = 0;
      let completedCount = 0;
      const runningPromises = new Set<Promise<void>>();
      
      const processNextTemplate = async () => {
        if (currentIndex >= sortedTemplateNames.length) return;
        const templateName = sortedTemplateNames[currentIndex++];
        const promise = loadTemplateComponents(templateName, componentNames).finally(() => {
          runningPromises.delete(promise);
          completedCount++;
          if (runningPromises.size < maxConcurrent) {
            processNextTemplate();
          }
        });
        
        runningPromises.add(promise);
      };

      for (let i = 0; i < Math.min(maxConcurrent, sortedTemplateNames.length); i++) {
        processNextTemplate();
      }

      while (completedCount < sortedTemplateNames.length) {
        await Promise.race(runningPromises);
      }
    

    } catch (err) {
      console.error('Error refreshing data:', err);
      setError('Error refreshing data.');
    }
  }, [params.version, loadTemplateComponents, api]);

  // 초기 데이터 로드
  useEffect(() => {
    let isMounted = true;

    const loadData = async () => {
      if (!isMounted) return;
      
      try {
        setIsLoading(true);
        const componentNames = await loadDefaultComponentNames();
        if (!isMounted) return;
        await handleRefresh(componentNames);
      } catch (err) {
        console.error('Error loading initial data:', err);
        setError('Error loading initial data.');
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadData();

    return () => {
      isMounted = false;
    };
  }, [params.version, loadDefaultComponentNames, handleRefresh]);

  // 템플릿 확장/축소 시 컴포넌트 로드
  const handleTemplateExpand = async (templateName: string) => {
    const newExpandedState = !templateExpanded[templateName];
    
    // 먼저 확장 상태를 변경
    setTemplateExpanded(prev => ({
      ...prev,
      [templateName]: newExpandedState
    }));
    
  };

  // 필터링된 템플릿 목록
  const filteredTemplates = useMemo(() => {
    return Object.keys(templates)
      .filter(templateName => {
        // 템플릿 이름 검색
        const matchesSearch = templateName.toLowerCase().includes(searchQuery.toLowerCase());
        return matchesSearch;
      });
  }, [templates, searchQuery]);

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          템플릿 관리
        </Typography>
        <Button
          variant="outlined"
          onClick={() => handleRefresh(defaultComponentNames)}
          startIcon={<RefreshIcon />}
        >
          새로고침
        </Button>
      </Box>

      {/* 필터 섹션 */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap" useFlexGap>
          <TextField
            placeholder="템플릿 이름 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            size="small"
            sx={{ width: 200 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Stack>
      </Paper>

      {/* 템플릿 목록 */}
      <Stack spacing={0.5}>
        {filteredTemplates.map((templateName) => {
          const components = templateComponents[templateName] || [];
          const isExpanded = templateExpanded[templateName];
          const templateCounts = templates[templateName] || 0;
          return (
            <Box key={templateName}>
              <Paper
                onClick={() => handleTemplateExpand(templateName)}
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
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleTemplateExpand(templateName);
                      }}
                      sx={{
                        color: 'primary.main',
                        '&:hover': {
                          bgcolor: 'primary.light',
                        },
                      }}
                    >
                      {isExpanded ? <ExpandLess /> : <ExpandMore />}
                    </IconButton>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                      <Typography variant="h6" sx={{ fontWeight: 500 }}>{templateName}</Typography>
                      <Chip
                        label={`${templateCounts}개의 컴포넌트`}
                        size="small"
                        color="primary"
                        variant="outlined"
                        sx={{ ml: 'auto' }}
                      />
                    </Box>
                  </Box>
                </Box>
              </Paper>
              {isExpanded && (
                <Box sx={{ mt: 0.5, ml: 3 }}>
                  {components.length > 0 ? (
                    components.map((component) => {
                      const isMapped = component.content !== '';
                      return (
                        <Paper
                          key={component.component}
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
                            borderColor: 'divider',
                            position: 'relative',
                            '&::before': {
                              content: '""',
                              position: 'absolute',
                              left: -2,
                              top: '50%',
                              width: 12,
                              height: 2,
                              bgcolor: 'primary.main',
                            },
                          }}
                        >
                          <Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                                <Typography variant="subtitle1" color="text.primary" sx={{ fontWeight: 500 }}>
                                  {component.component}
                                </Typography>
                                {component.description && (
                                  <Typography variant="body2" color="text.secondary">
                                    - {component.description}
                                  </Typography>
                                )}
                                {!isMapped && (
                                  <Chip
                                    label="미매핑"
                                    size="small"
                                    color="warning"
                                    variant="outlined"
                                  />
                                )}
                              </Box>
                            </Box>
                            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 1 }}>
                              {component.layout && (
                                <Chip
                                  label={component.layout}
                                  size="small"
                                  color="primary"
                                  variant="outlined"
                                />
                              )}
                              {component.partials && component.partials.length > 0 && (
                                component.partials.map((partial) => (
                                  <Chip
                                    key={partial}
                                    label={partial}
                                    size="small"
                                    variant="outlined"
                                  />
                                ))
                              )}
                            </Box>
                            <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                              <Typography variant="caption" color="text.secondary">
                                생성: {component.created_at ? formatDate(component.created_at) : '-'}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                수정: {component.updated_at ? formatDate(component.updated_at) : '-'}
                              </Typography>
                            </Box>
                          </Box>
                        </Paper>
                      );
                    })
                  ) : isLoading ? (
                    <Paper
                      sx={{
                        p: 1.5,
                        borderLeft: '2px solid',
                        borderColor: 'divider',
                        position: 'relative',
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          left: -2,
                          top: '50%',
                          width: 12,
                          height: 2,
                          bgcolor: 'primary.main',
                        },
                      }}
                    >
                      <Typography variant="body2" color="text.secondary">
                        컴포넌트 로딩 중...
                      </Typography>
                    </Paper>
                  ) : (
                    <Paper
                      sx={{
                        p: 1.5,
                        borderLeft: '2px solid',
                        borderColor: 'divider',
                        position: 'relative',
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          left: -2,
                          top: '50%',
                          width: 12,
                          height: 2,
                          bgcolor: 'primary.main',
                        },
                      }}
                    >
                      <Typography variant="body2" color="text.secondary">
                        컴포넌트가 없습니다.
                      </Typography>
                    </Paper>
                  )}
                </Box>
              )}
            </Box>
          );
        })}
      </Stack>

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