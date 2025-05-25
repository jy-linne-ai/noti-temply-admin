import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  IconButton,
  Chip,
  Drawer,
  Button,
  Stack,
  Tabs,
  Tab,
  CircularProgress,
  TextField,
} from '@mui/material';
import { 
  Edit as EditIcon,
  Close as CloseIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import { Template } from '@/types/template';
import { HtmlEditor } from '@/components/Editor';
import { Preview } from '@/components/Preview';
import { useApi } from '@/lib/api';
import { formatDate } from '@/lib/utils';

interface TemplateDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  selectedComponent: Template | null;
  selectedTemplateName: string;
  selectedComponentName: string;
  drawerComponents: Template[];
  onComponentClick: (template: string, component: Template) => void;
  version: string;
}

export function TemplateDrawer({
  isOpen,
  onClose,
  selectedComponent,
  selectedTemplateName,
  selectedComponentName,
  drawerComponents,
  onComponentClick,
  version,
}: TemplateDrawerProps) {
  const router = useRouter();
  const [contentTab, setContentTab] = React.useState(0);
  const [componentListTab, setComponentListTab] = React.useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [allComponents, setAllComponents] = useState<string[]>([]);
  const [mappedComponents, setMappedComponents] = useState<Template[]>([]);
  const [componentTypes, setComponentTypes] = useState<string[]>([]);
  const [previewContent, setPreviewContent] = useState<string>('');
  
  // 메모리 캐시를 위한 ref
  const cacheRef = useRef<{
    components: string[];
    mapped: Template[];
    types: string[];
    lastVersion: string;
    lastTemplate: string;
    isLoading: boolean;
  }>({
    components: [],
    mapped: [],
    types: [],
    lastVersion: '',
    lastTemplate: '',
    isLoading: false
  });

  // selectedComponent가 변경될 때 previewContent 업데이트
  useEffect(() => {
    if (selectedComponent) {
      setPreviewContent(selectedComponent.content || '');
    } else {
      setPreviewContent('');
    }
  }, [selectedComponent]);

  const api = useApi();

  // 컴포넌트 목록 로드
  useEffect(() => {
    const loadComponents = async () => {
      if (!isOpen) return;
      
      // 이미 로딩 중이면 중복 호출 방지
      if (cacheRef.current.isLoading) return;
      
      // 캐시된 데이터가 있고, 버전과 템플릿이 동일한 경우 캐시 사용
      if (
        cacheRef.current.components.length > 0 &&
        cacheRef.current.lastVersion === version &&
        cacheRef.current.lastTemplate === selectedTemplateName
      ) {
        setAllComponents(cacheRef.current.components);
        setMappedComponents(cacheRef.current.mapped);
        setComponentTypes(cacheRef.current.types);
        setIsLoading(false);
        return;
      }
      
      cacheRef.current.isLoading = true;
      setIsLoading(true);
      setError(null);
      
      try {
        // 병렬로 API 요청 실행
        const [componentNames, components] = await Promise.all([
          api.getAllTemplateComponents(),
          api.getTemplateComponents(version, selectedTemplateName)
        ]);
        
        const mapped = components.filter(comp => comp.content && comp.content.trim() !== '');
        
        // 컴포넌트 타입 추출 (예: HTML_EMAIL, TEXT_EMAIL)
        const types = new Set<string>();
        componentNames.forEach(name => {
          const type = name.split('_')[0];
          if (type) types.add(type);
        });
        
        // 캐시 업데이트
        cacheRef.current = {
          components: componentNames,
          mapped,
          types: Array.from(types).sort(),
          lastVersion: version,
          lastTemplate: selectedTemplateName,
          isLoading: false
        };
        
        // 상태 업데이트
        setAllComponents(componentNames);
        setMappedComponents(mapped);
        setComponentTypes(Array.from(types).sort());
        
        // 선택된 컴포넌트의 인덱스로 탭 설정
        const selectedIndex = componentNames.indexOf(selectedComponentName);
        if (selectedIndex !== -1) {
          setComponentListTab(selectedIndex);
          // 선택된 컴포넌트가 매핑되어 있으면 해당 컴포넌트 사용
          const selectedComponent = mapped.find(c => c.component === selectedComponentName);
          if (selectedComponent) {
            onComponentClick(selectedTemplateName, selectedComponent);
          } else {
            // 매핑되지 않은 컴포넌트인 경우 빈 컴포넌트 객체 생성
            const emptyComponent = {
              template: selectedTemplateName,
              component: selectedComponentName,
              content: '',
              description: null,
              partials: [],
              created_at: null,
              created_by: null,
              updated_at: null,
              updated_by: null,
              layout: null,
              isMapped: false
            };
            onComponentClick(selectedTemplateName, emptyComponent);
          }
        }
      } catch (err) {
        console.error('Error loading components:', err);
        setError('컴포넌트 목록을 불러오는데 실패했습니다.');
      } finally {
        cacheRef.current.isLoading = false;
        setIsLoading(false);
      }
    };

    loadComponents();
  }, [isOpen, version, selectedTemplateName, selectedComponentName, onComponentClick, api]);

  // 탭 변경 시 컴포넌트 선택
  const handleTabChange = useCallback((event: React.SyntheticEvent, newValue: number) => {
    setComponentListTab(newValue);
    const componentName = allComponents[newValue];
    
    // 매핑된 컴포넌트에서 찾기
    const component = mappedComponents.find(comp => comp.component === componentName);
    
    if (component) {
      onComponentClick(selectedTemplateName, component);
    } else {
      // 매핑되지 않은 컴포넌트인 경우 빈 컴포넌트 객체 생성
      const emptyComponent = {
        template: selectedTemplateName,
        component: componentName,
        content: '',
        description: null,
        partials: [],
        created_at: null,
        created_by: null,
        updated_at: null,
        updated_by: null,
        layout: null,
        isMapped: false
      };
      onComponentClick(selectedTemplateName, emptyComponent);
    }
  }, [allComponents, mappedComponents, onComponentClick, selectedTemplateName]);

  // Drawer가 닫힐 때 캐시 유지 (다음 열 때 재사용)
  useEffect(() => {
    if (!isOpen) {
      setIsLoading(true);
    }
  }, [isOpen]);

  // Drawer가 열릴 때 선택된 컴포넌트로 탭 이동
  useEffect(() => {
    if (isOpen && selectedComponentName) {
      const index = allComponents.indexOf(selectedComponentName);
      if (index !== -1) {
        setComponentListTab(index);
      }
    }
  }, [isOpen, selectedComponentName, allComponents]);

  // 탭 렌더링을 메모이제이션
  const renderTab = useCallback((componentName: string) => {
    const component = mappedComponents.find(comp => comp.component === componentName);
    const isMapped = !!component;
    return (
      <Tab 
        key={componentName}
        label={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography sx={{ fontSize: '0.875rem' }}>{componentName}</Typography>
            {isMapped ? (
              <CheckCircleIcon 
                sx={{ 
                  fontSize: '1rem',
                  color: 'success.main',
                  opacity: 0.8
                }} 
              />
            ) : (
              <WarningIcon 
                sx={{ 
                  fontSize: '1rem',
                  color: 'warning.main',
                  opacity: 0.8
                }} 
              />
            )}
          </Box>
        }
        sx={{
          color: isMapped ? 'text.primary' : 'text.secondary',
          '&.Mui-selected': {
            color: 'primary.main',
            fontWeight: 600
          },
          minHeight: '48px',
          py: 0.5
        }}
      />
    );
  }, [mappedComponents]);

  const handleSave = async () => {
    try {
      setIsLoading(true);
      const updatedComponent = await api.updateTemplateComponent(
        version,
        selectedTemplateName,
        selectedComponentName,
        {
          content: previewContent,
          description: selectedComponent?.description?.trim() || undefined,
        }
      );
      onComponentClick(selectedTemplateName, updatedComponent);
      onClose();
    } catch (err) {
      console.error('Error saving component:', err);
      setError('컴포넌트 저장에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Drawer
      anchor="right"
      open={isOpen}
      onClose={onClose}
      PaperProps={{
        sx: { width: '80%', maxWidth: '1200px' }
      }}
    >
      <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" component="h2">
            {selectedTemplateName}
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Box sx={{ p: 2 }}>
            <Typography color="error">{error}</Typography>
          </Box>
        ) : (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            height: 'calc(100% - 80px)',
            overflow: 'hidden'
          }}>
            {/* 컴포넌트 탭 */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
              <Tabs 
                value={componentListTab}
                onChange={handleTabChange}
                aria-label="컴포넌트 탭"
                variant="scrollable"
                scrollButtons="auto"
              >
                {allComponents.map(renderTab)}
              </Tabs>
            </Box>

            {/* 컴포넌트 상세 정보 */}
            <Box sx={{ 
              flex: 1, 
              overflow: 'auto',
              display: 'flex',
              flexDirection: 'column'
            }}>
              {selectedComponent && (
                <Stack spacing={3} sx={{ flex: 1, minHeight: 0 }}>
                  {/* 기본 정보 테이블 */}
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Box sx={{ display: 'grid', gridTemplateColumns: '100px 1fr', gap: 1 }}>
                      {/* 설명 */}
                      <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                        설명
                      </Typography>
                      <Typography>
                        {selectedComponent.description || '설명이 없습니다.'}
                      </Typography>

                      {/* 생성/수정 정보 */}
                      <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                        생성
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        <Typography variant="body2">
                          {selectedComponent ? formatDate(selectedComponent.created_at) : '-'}
                        </Typography>
                        {selectedComponent?.created_by && (
                          <Chip
                            label={`by ${selectedComponent.created_by}`}
                            size="small"
                            variant="outlined"
                            color="primary"
                          />
                        )}
                      </Box>

                      <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                        수정
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        <Typography variant="body2">
                          {selectedComponent ? formatDate(selectedComponent.updated_at) : '-'}
                        </Typography>
                        {selectedComponent?.updated_by && (
                          <Chip
                            label={`by ${selectedComponent.updated_by}`}
                            size="small"
                            variant="outlined"
                            color="primary"
                          />
                        )}
                      </Box>

                      {/* 레이아웃 */}
                      <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                        레이아웃
                      </Typography>
                      <Box>
                        {selectedComponent.layout ? (
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                            <Chip
                              label={selectedComponent.layout}
                              color="primary"
                              variant="outlined"
                              size="small"
                              sx={{ alignSelf: 'flex-start' }}
                            />
                          </Box>
                        ) : (
                          <Typography color="text.secondary" variant="body2">레이아웃이 없습니다.</Typography>
                        )}
                      </Box>

                      {/* 파셜 */}
                      <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                        파셜
                      </Typography>
                      <Box>
                        {selectedComponent.partials && selectedComponent.partials.length > 0 ? (
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {selectedComponent.partials.map(partial => (
                              <Chip
                                key={partial}
                                label={partial}
                                variant="outlined"
                                size="small"
                              />
                            ))}
                          </Box>
                        ) : (
                          <Typography color="text.secondary" variant="body2">사용된 파셜이 없습니다.</Typography>
                        )}
                      </Box>
                    </Box>
                  </Paper>

                  {selectedComponent.content && selectedComponent.content.trim() !== '' && (
                    <>
                      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                        <Tabs 
                          value={contentTab}
                          onChange={(_, newValue: number) => setContentTab(newValue)}
                          aria-label="컨텐츠 탭"
                        >
                          <Tab label="소스" />
                          <Tab label="프리뷰" />
                        </Tabs>
                      </Box>

                      {contentTab === 0 && (
                        <Box sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
                          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                            소스
                          </Typography>
                          <Paper 
                            variant="outlined" 
                            sx={{ 
                              flex: 1,
                              minHeight: 0,
                              overflow: 'hidden'
                            }}
                          >
                            {selectedComponent && (
                              <HtmlEditor
                                key={selectedComponent.component}
                                value={selectedComponent.content}
                                onChange={(value) => {
                                  setPreviewContent(value);
                                }}
                                type="template"
                                height="100%"
                              />
                            )}
                          </Paper>
                        </Box>
                      )}

                      {contentTab === 1 && (
                        <Box sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
                          <Preview
                            content={previewContent}
                            title="템플릿 프리뷰"
                            type="template"
                          />
                        </Box>
                      )}

                      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
                        <Button
                          variant="outlined"
                          startIcon={<EditIcon />}
                          onClick={() => {
                            onClose();
                            router.push(`/versions/${version}/templates/${selectedTemplateName}/components/${selectedComponent.component}`);
                          }}
                        >
                          수정하기
                        </Button>
                      </Box>
                    </>
                  )}
                </Stack>
              )}
            </Box>
          </Box>
        )}
      </Box>
    </Drawer>
  );
} 