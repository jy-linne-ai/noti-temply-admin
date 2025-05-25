'use client';

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
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
  Collapse,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  Drawer,
  Button,
  Stack,
  Tabs,
  Tab,
  Autocomplete,
} from '@mui/material';
import { 
  ExpandMore, 
  ExpandLess, 
  Search,
  Edit as EditIcon,
  Close as CloseIcon,
  ViewList as ViewListIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { Template } from '@/types/template';
import { HtmlEditor } from '@/components/Editor';
import { TemplateDrawer } from '@/components/templates/TemplateDrawer';
import { formatDate } from '@/lib/utils';

export default function TemplatesPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApi();
  const [templates, setTemplates] = useState<string[]>([]);
  const [expandedTemplates, setExpandedTemplates] = useState<Record<string, boolean>>({});
  const [templateComponents, setTemplateComponents] = useState<Record<string, Template[]>>({});
  const [error, setError] = useState<string | null>(null);
  const [allComponents, setAllComponents] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const isInitialMount = useRef(true);
  const processedTemplates = useRef<Set<string>>(new Set());
  const loadingTemplates = useRef<Set<string>>(new Set());
  const versionRef = useRef(params.version);
  const abortControllerRef = useRef<AbortController | null>(null);
  const isDataLoaded = useRef(false);
  const componentLoadQueue = useRef<Set<string>>(new Set());
  const isProcessingQueue = useRef(false);
  const loadAttemptRef = useRef(0);
  const initialLoadPromise = useRef<Promise<void> | null>(null);
  const [templateCounts, setTemplateCounts] = useState<Record<string, number>>({});
  
  // 필터링 상태
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLayout, setSelectedLayout] = useState<string>('');
  const [selectedPartial, setSelectedPartial] = useState<string>('');
  const [availableLayouts, setAvailableLayouts] = useState<string[]>([]);
  const [availablePartials, setAvailablePartials] = useState<string[]>([]);

  // 상세 정보 상태
  const [selectedComponent, setSelectedComponent] = useState<Template | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [selectedTemplateName, setSelectedTemplateName] = useState<string>('');
  const [contentTab, setContentTab] = useState(0);
  const [drawerComponents, setDrawerComponents] = useState<Template[]>([]);

  // 컴포넌트 로드 큐 처리
  const processComponentLoadQueue = useCallback(async () => {
    if (isProcessingQueue.current || componentLoadQueue.current.size === 0) {
      return;
    }
    
    isProcessingQueue.current = true;
    const queue = Array.from(componentLoadQueue.current);
    componentLoadQueue.current.clear();
    
    try {
      // 큐를 5개씩 나누어 처리
      const BATCH_SIZE = 5;
      for (let i = 0; i < queue.length; i += BATCH_SIZE) {
        const batch = queue.slice(i, i + BATCH_SIZE);
        
        // 현재 배치의 템플릿 컴포넌트를 병렬로 로드
        const loadPromises = batch.map(async (templateName) => {
          if (processedTemplates.current.has(templateName) || loadingTemplates.current.has(templateName)) {
            return;
          }
          
          loadingTemplates.current.add(templateName);
          
          try {
            const components = await api.getTemplateComponents(
              params.version as string,
              templateName
            );
            
            if (!Array.isArray(components)) {
              throw new Error('Invalid API response');
            }
            
            // API에서 받은 컴포넌트로 맵 생성
            const componentMap = new Map(
              components.map(comp => [comp.component, comp])
            );
            
            // 매핑된 컴포넌트만 필터링하고 API 순서 유지
            const mappedComponents = allComponents
              .reduce((acc: Template[], componentName) => {
                const apiComponent = componentMap.get(componentName);
                if (apiComponent && apiComponent.content && apiComponent.content.trim() !== '') {
                  acc.push({
                    ...apiComponent,
                    isMapped: true
                  });
                }
                return acc;
              }, []);
            
            return {
              templateName,
              components: mappedComponents,
              count: mappedComponents.length
            };
          } catch (err) {
            console.error(`Error loading components for template ${templateName}:`, err);
            return {
              templateName,
              components: [],
              count: 0
            };
          } finally {
            loadingTemplates.current.delete(templateName);
          }
        });

        // 현재 배치의 로드 완료 대기
        const results = await Promise.all(loadPromises);
        
        // 결과를 한 번에 상태 업데이트
        setTemplateComponents(prev => {
          const newComponents = { ...prev };
          results.forEach(result => {
            if (result) {
              newComponents[result.templateName] = result.components;
              processedTemplates.current.add(result.templateName);
            }
          });
          return newComponents;
        });

        setTemplateCounts(prev => {
          const newCounts = { ...prev };
          results.forEach(result => {
            if (result) {
              newCounts[result.templateName] = result.count;
            }
          });
          return newCounts;
        });
        
        // 다음 배치 전에 잠시 대기 (서버 부하 방지)
        if (i + BATCH_SIZE < queue.length) {
          await new Promise(resolve => setTimeout(resolve, 100));
        }
      }
    } finally {
      isProcessingQueue.current = false;
      // 큐에 새로운 항목이 추가되었다면 다시 처리
      if (componentLoadQueue.current.size > 0) {
        processComponentLoadQueue();
      }
    }
  }, [params.version, allComponents]);

  // allComponents가 변경될 때마다 컴포넌트 매핑 수행
  useEffect(() => {
    if (allComponents.length > 0 && templates.length > 0 && !isDataLoaded.current) {
      // 큐 초기화
      componentLoadQueue.current.clear();
      processedTemplates.current.clear();
      loadingTemplates.current.clear();
      
      // 템플릿을 순차적으로 처리
      for (const templateName of templates) {
        if (!processedTemplates.current.has(templateName)) {
          componentLoadQueue.current.add(templateName);
        }
      }
      
      // 큐 처리 시작
      processComponentLoadQueue();
    }
  }, [allComponents, templates, processComponentLoadQueue]);

  // 초기 데이터 로드
  useEffect(() => {
    const loadInitialData = async () => {
      if (isDataLoaded.current || isLoading) {
        return;
      }
      
      if (versionRef.current !== params.version || isInitialMount.current) {
        if (abortControllerRef.current) {
          abortControllerRef.current.abort();
        }
        abortControllerRef.current = new AbortController();
        
        try {
          setIsLoading(true);
          isDataLoaded.current = true;
          versionRef.current = params.version;
          processedTemplates.current.clear();
          loadingTemplates.current.clear();
          componentLoadQueue.current.clear();
          loadAttemptRef.current = 0;
          setTemplateCounts({});
          setTemplateComponents({});
          
          if (initialLoadPromise.current) {
            await initialLoadPromise.current;
            return;
          }
          
          initialLoadPromise.current = (async () => {
            try {
              // 1. 먼저 템플릿 이름을 가져옵니다
              const templateNames = await api.getTemplateNames(params.version as string);
              setTemplates(templateNames);
              const initialExpanded = templateNames.reduce((acc, name) => ({ ...acc, [name]: false }), {});
              setExpandedTemplates(initialExpanded);

              // 2. 그 다음 컴포넌트 목록을 가져옵니다
              const componentNames = await api.getAllTemplateComponents();
              setAllComponents(componentNames);
            } finally {
              initialLoadPromise.current = null;
            }
          })();
          
          await initialLoadPromise.current;
        } catch (err) {
          if (err instanceof Error && err.name === 'AbortError') {
            return;
          }
          console.error('Error loading templates:', err);
          setError('템플릿 목록을 불러오는데 실패했습니다.');
        } finally {
          setIsLoading(false);
          isInitialMount.current = false;
        }
      }
    };

    loadInitialData();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      isDataLoaded.current = false;
    };
  }, [params.version, isDataLoaded.current]);

  // 새로고침 함수
  const handleRefresh = useCallback(() => {
    isDataLoaded.current = false;
    isInitialMount.current = true;
    processedTemplates.current.clear();
    loadingTemplates.current.clear();
    componentLoadQueue.current.clear();
    loadAttemptRef.current = 0;
    setTemplateCounts({});
    setTemplateComponents({});
    setTemplates([]);
    setAllComponents([]);
    setExpandedTemplates({});
    setError(null);
  }, []);

  // 버전이 변경될 때 상태 초기화
  useEffect(() => {
    if (versionRef.current !== params.version) {
      isDataLoaded.current = false;
      isInitialMount.current = true;
      processedTemplates.current.clear();
      loadingTemplates.current.clear();
      componentLoadQueue.current.clear();
      loadAttemptRef.current = 0;
      versionRef.current = params.version;
    }
  }, [params.version]);

  // 레이아웃과 파셜 목록 업데이트
  useEffect(() => {
    const layouts = new Set<string>();
    const partials = new Set<string>();

    Object.values(templateComponents).forEach(components => {
      components.forEach(component => {
        if (component.layout) {
          layouts.add(component.layout);
        }
        if (component.partials) {
          component.partials.forEach(partial => partials.add(partial));
        }
      });
    });

    setAvailableLayouts(Array.from(layouts).sort());
    setAvailablePartials(Array.from(partials).sort());
  }, [templateComponents]);

  // 템플릿 확장 시 컴포넌트 로드
  const handleTemplateClick = useCallback(async (templateName: string) => {
    // 먼저 확장 상태를 변경
    setExpandedTemplates(prev => ({
      ...prev,
      [templateName]: !prev[templateName]
    }));

    // 확장된 경우에만 컴포넌트 로드
    if (!expandedTemplates[templateName] && !processedTemplates.current.has(templateName) && !loadingTemplates.current.has(templateName)) {
      componentLoadQueue.current.add(templateName);
      await processComponentLoadQueue();
    }
  }, [processComponentLoadQueue, expandedTemplates]);

  // 컴포넌트 클릭 시 상세 정보 로드
  const handleComponentClick = async (template: string, component: Template) => {
    try {
      // 먼저 선택된 컴포넌트 상태를 업데이트
      setSelectedComponent(component);
      setSelectedTemplateName(template);
      setIsDrawerOpen(true);

      // 이미 로드된 컴포넌트가 있으면 재사용
      const existingComponents = templateComponents[template] || [];
      const existingComponent = existingComponents.find(comp => comp.component === component.component);
      
      if (existingComponent) {
        setDrawerComponents(existingComponents);
        return;
      }

      // 저장된 컴포넌트와 API 컴포넌트를 매핑
      const mappedComponents = allComponents.map(componentName => {
        // 저장된 컴포넌트 찾기
        const savedComponent = templateComponents[template]?.find(
          saved => saved.component === componentName
        );

        if (savedComponent) {
          // 저장된 컴포넌트가 있으면 저장된 값 사용
          return {
            ...savedComponent,
            isMapped: true
          } as Template;
        } else {
          // 저장된 컴포넌트가 없으면 기본 정보만 사용
          return {
            template: template,
            component: componentName,
            content: '',
            description: '',
            partials: [],
            created_at: null,
            created_by: null,
            updated_at: null,
            updated_by: null,
            layout: '',
            isMapped: false
          } as Template;
        }
      });

      setDrawerComponents(mappedComponents);

      try {
        // API로 상세 정보 조회 시도
        const componentDetail = await api.getTemplateComponent(
          params.version as string,
          template,
          component.component
        );
        // API 호출 성공 시 매핑된 컴포넌트로 처리
        const updatedComponent = {
          ...componentDetail,
          isMapped: true
        };
        setSelectedComponent(updatedComponent);

        // 템플릿 컴포넌트 목록 업데이트
        setTemplateComponents(prev => ({
          ...prev,
          [template]: prev[template]?.map(comp => 
            comp.component === component.component ? updatedComponent : comp
          ) || [updatedComponent]
        }));
      } catch (err) {
        // 404 등 API 호출 실패 시 미매핑된 컴포넌트로 처리
        const unmappedComponent = {
          ...component,
          isMapped: false
        };
        setSelectedComponent(unmappedComponent);

        // 템플릿 컴포넌트 목록에서 해당 컴포넌트 제거 (미매핑 상태로)
        setTemplateComponents(prev => ({
          ...prev,
          [template]: prev[template]?.filter(comp => 
            comp.component !== component.component
          ) || []
        }));
      }
    } catch (err) {
      console.error('Error handling component click:', err);
      // API 호출 실패 시 기존 데이터로 표시
      setSelectedComponent(component);
      setSelectedTemplateName(template);
      setIsDrawerOpen(true);
      setDrawerComponents(templateComponents[template] || []);
    }
  };

  // 필터링된 템플릿 목록
  const filteredTemplates = useMemo(() => {
    return templates.filter(templateName => {
      const components = templateComponents[templateName] || [];
      
      // 템플릿 이름 검색
      const matchesSearch = templateName.toLowerCase().includes(searchQuery.toLowerCase());
      
      // 레이아웃 필터
      const matchesLayout = !selectedLayout || components.some(comp => comp.layout === selectedLayout);
      
      // 파셜 필터
      const matchesPartial = !selectedPartial || components.some(comp => 
        comp.partials?.includes(selectedPartial)
      );

      return matchesSearch && matchesLayout && matchesPartial;
    });
  }, [templates, templateComponents, searchQuery, selectedLayout, selectedPartial]);

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          템플릿 관리
        </Typography>
        <Button
          variant="outlined"
          onClick={handleRefresh}
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
                  <Search />
                </InputAdornment>
              ),
            }}
          />
          <Autocomplete
            size="small"
            options={availableLayouts}
            value={selectedLayout}
            onChange={(_, newValue) => setSelectedLayout(newValue || '')}
            renderInput={(params) => (
              <TextField
                {...params}
                label="레이아웃"
                placeholder="레이아웃 검색..."
                sx={{ width: 200 }}
              />
            )}
            freeSolo
            disableClearable
          />
          <Autocomplete
            size="small"
            options={availablePartials}
            value={selectedPartial}
            onChange={(_, newValue) => setSelectedPartial(newValue || '')}
            renderInput={(params) => (
              <TextField
                {...params}
                label="파셜"
                placeholder="파셜 검색..."
                sx={{ width: 200 }}
              />
            )}
            freeSolo
            disableClearable
          />
          {(selectedLayout || selectedPartial || searchQuery) && (
                <Button
              size="small"
              onClick={() => {
                setSelectedLayout('');
                setSelectedPartial('');
                setSearchQuery('');
              }}
                >
              필터 초기화
                </Button>
          )}
        </Stack>
      </Paper>

      {/* 템플릿 목록 */}
      <Stack spacing={0.5}>
        {filteredTemplates.map((templateName) => {
          const components = templateComponents[templateName] || [];
          const isExpanded = expandedTemplates[templateName];
          
          return (
            <Box key={templateName}>
              <Paper
                onClick={() => handleTemplateClick(templateName)}
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
                        handleTemplateClick(templateName);
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
                        label={`${templateCounts[templateName] || 0}개의 컴포넌트`}
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
                          onClick={() => handleComponentClick(templateName, component)}
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
                        컴포넌트 로딩 중...
                      </Typography>
                    </Paper>
                  )}
                </Box>
              )}
            </Box>
          );
        })}
      </Stack>

      {/* 상세 정보 Drawer */}
      <TemplateDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        selectedComponent={selectedComponent}
        selectedTemplateName={selectedTemplateName}
        selectedComponentName={selectedComponent?.component || ''}
        drawerComponents={drawerComponents}
        onComponentClick={handleComponentClick}
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