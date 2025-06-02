'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useParams } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  Alert,
  Snackbar,
  Stack,
  TextField,
  InputAdornment,
  Button,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Autocomplete,
  Tabs,
  Tab,
  Drawer,
  IconButton,
  Tooltip,
} from '@mui/material';
import { Search as SearchIcon, Visibility as VisibilityIcon, Close as CloseIcon, Add as AddIcon, Refresh as RefreshIcon, CheckCircle as CheckCircleIcon, Cancel as CancelIcon } from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { TemplateComponent } from '@/types/template';
import Editor from '@monaco-editor/react';
import { Preview } from '@/components/Preview';
import Ajv, { JSONSchemaType } from 'ajv';
import addFormats from 'ajv-formats';

// Ajv 인스턴스 생성 및 포맷 추가
const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`template-tabpanel-${index}`}
      aria-labelledby={`template-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `template-tab-${index}`,
    'aria-controls': `template-tabpanel-${index}`,
  };
}

export default function PreviewPage() {
  const params = useParams();
  const api = useApi();
  const [defaultComponentNames, setDefaultComponentNames] = useState<string[]>([]);
  const [templates, setTemplates] = useState<Record<string, number>>({});
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [components, setComponents] = useState<TemplateComponent[]>([]);
  const [schema, setSchema] = useState<Record<string, any>>({});
  const [variables, setVariables] = useState<Record<string, any>>({});
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [componentTabs, setComponentTabs] = useState<Record<string, number>>({});
  const [renderedContents, setRenderedContents] = useState<Record<string, string>>({});
  const [previewDrawerOpen, setPreviewDrawerOpen] = useState(false);
  const [selectedComponent, setSelectedComponent] = useState<TemplateComponent | null>(null);
  const [drawerRenderedContent, setDrawerRenderedContent] = useState<string>('');
  const [drawerActiveTab, setDrawerActiveTab] = useState<string>('');
  const [isVariablesValid, setIsVariablesValid] = useState(true);
  const [selectedTab, setSelectedTab] = useState(0);
  const [mappedComponents, setMappedComponents] = useState<Record<string, boolean>>({});

  // 컴포넌트 로드
  const loadComponents = async (templateName: string) => {
    try {
      setIsLoading(true);
      // 먼저 변수 정보와 스키마 정보를 로드
      const [schema, variables, defaultComponentNames] = await Promise.all([
        api.getTemplateSchema(params.version as string, templateName),
        api.getTemplateVariables(params.version as string, templateName),
        api.getTemplateAvailableComponents()
      ]);
      setSchema(schema);
      setVariables(variables);
      setDefaultComponentNames(defaultComponentNames);

      // 그 다음 컴포넌트 정보를 로드
      const components = await api.getTemplateComponents(params.version as string, templateName);
      
      // defaultComponentNames 순서대로 정렬
      const sortedComponents = defaultComponentNames
        .map(name => components.find(c => c.component === name))
        .filter((c): c is TemplateComponent => !!c);
      
      setComponents(sortedComponents);
      
      // 매핑된 컴포넌트 확인
      const mapped: Record<string, boolean> = {};
      defaultComponentNames.forEach(comp => {
        mapped[comp] = sortedComponents.some(c => c.component === comp);
      });
      setMappedComponents(mapped);
      
      // 각 컴포넌트의 탭 상태 초기화
      const initialTabs: Record<string, number> = {};
      sortedComponents.forEach(component => {
        initialTabs[component.component] = 0;
      });
      setComponentTabs(initialTabs);
    } catch (err) {
      console.error('Error loading components:', err);
      setError('컴포넌트를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // 기본값으로 초기화
  const handleResetVariables = async () => {
    if (!selectedTemplate) return;
    
    try {
      setIsLoading(true);
      const defaultVariables = await api.getTemplateVariables(params.version as string, selectedTemplate);
      setVariables(defaultVariables);
      setError(null);
    } catch (err) {
      console.error('Error resetting variables:', err);
      setError('기본값을 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // 초기 데이터 로드
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setIsLoading(true);
        // 기본 컴포넌트 이름 목록 로드
        const defaultComponents = await api.getTemplateAvailableComponents();
        setDefaultComponentNames(defaultComponents);
        
        // 템플릿 목록 로드
        const templateNames = await api.getTemplateComponentCounts(params.version as string);
        setTemplates(templateNames);
      } catch (err) {
        console.error('Error loading initial data:', err);
        setError('초기 데이터를 불러오는데 실패했습니다.');
      } finally {
        setIsLoading(false);
      }
    };

    loadInitialData();
  }, [params.version]);

  // 템플릿 선택 시 컴포넌트 로드
  useEffect(() => {
    if (selectedTemplate) {
      loadComponents(selectedTemplate);
    }
  }, [selectedTemplate]);

  // 필터링된 컴포넌트 목록
  const filteredComponents = components;

  // 템플릿 카테고리 추출
  const getTemplateCategory = (templateName: string) => {
    const parts = templateName.split(':');
    return parts[0] || '기타';
  };

  // 카테고리별로 템플릿 그룹화
  const groupedTemplates = useMemo(() => {
    const groups: Record<string, string[]> = {};
    Object.keys(templates).forEach(template => {
      const category = getTemplateCategory(template);
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(template);
    });
    // 카테고리 이름으로 정렬
    return Object.fromEntries(
      Object.entries(groups).sort(([a], [b]) => a.localeCompare(b))
    );
  }, [templates]);

  // 카테고리별 템플릿 필터링
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const filteredTemplates = useMemo(() => {
    if (!categoryFilter) return Object.keys(templates);
    return Object.keys(templates).filter((template: string) => 
      getTemplateCategory(template) === categoryFilter
    );
  }, [templates, categoryFilter]);

  // 변수 정보 수정 핸들러
  const handleVariablesChange = (value: string | undefined) => {
    if (!value) return;
    try {
      const parsedValue = JSON.parse(value);
      setVariables(parsedValue);
      
      // JSON Schema 검증
      if (schema && Object.keys(schema).length > 0) {
        const validate = ajv.compile(schema as JSONSchemaType<typeof parsedValue>);
        const isValid = validate(parsedValue);
        setIsVariablesValid(isValid);
        
        if (!isValid) {
          const errors = validate.errors?.map((err: any) => {
            const path = err.instancePath || 'root';
            return `${path}: ${err.message}`;
          }).join('\n');
          setError(`변수 정보가 스키마와 일치하지 않습니다:\n${errors}`);
        } else {
          setError(null);
        }
      } else {
        setIsVariablesValid(true);
      }
    } catch (err) {
      setIsVariablesValid(false);
      setError('JSON 형식이 올바르지 않습니다.');
    }
  };

  // 컴포넌트 렌더링
  const renderComponent = async (templateName: string, componentName: string) => {
    try {
      // 변수 정보가 없으면 렌더링하지 않음
      if (Object.keys(variables).length === 0) {
        return '변수 정보를 불러오는 중입니다...';
      }

      // 이미 렌더링된 결과가 있으면 캐시된 결과 반환
      const cacheKey = `${templateName}/${componentName}`;
      if (renderedContents[cacheKey]) {
        return renderedContents[cacheKey];
      }

      const renderedContent = await api.renderComponent(
        params.version as string,
        templateName,
        componentName,
        variables
      );

      // 렌더링된 결과를 캐시에 저장
      setRenderedContents(prev => ({
        ...prev,
        [cacheKey]: renderedContent
      }));

      return renderedContent;
    } catch (err) {
      console.error('Error rendering component:', err);
      setError('컴포넌트 렌더링에 실패했습니다.');
      return null;
    }
  };

  // 변수가 변경될 때 캐시 초기화
  useEffect(() => {
    setRenderedContents({});
  }, [variables]);

  // Drawer가 열릴 때 렌더링된 결과 로드
  useEffect(() => {
    if (previewDrawerOpen && selectedTemplate) {
      // 선택된 컴포넌트가 있으면 해당 컴포넌트의 탭을 활성화
      if (selectedComponent) {
        setDrawerActiveTab(selectedComponent.component);
        setSelectedTab(defaultComponentNames.findIndex(name => name === selectedComponent.component));
        renderComponent(selectedTemplate, selectedComponent.component)
          .then(content => {
            if (content) {
              const formattedContent = selectedComponent.component.startsWith('TEXT_')
                ? content.replace(/\n/g, '<br>')
                : content;
              setDrawerRenderedContent(formattedContent);
            }
          })
          .catch(err => {
            console.error('Error rendering component for drawer:', err);
            setError('컴포넌트 렌더링에 실패했습니다.');
          });
      } else if (components.length > 0) {
        // 선택된 컴포넌트가 없으면 첫 번째 매핑된 컴포넌트의 탭을 활성화
        const firstMappedComponent = components.find(comp => mappedComponents[comp.component]);
        if (firstMappedComponent) {
          setDrawerActiveTab(firstMappedComponent.component);
          setSelectedTab(defaultComponentNames.findIndex(name => name === firstMappedComponent.component));
          renderComponent(selectedTemplate, firstMappedComponent.component)
            .then(content => {
              if (content) {
                const formattedContent = firstMappedComponent.component.startsWith('TEXT_')
                  ? content.replace(/\n/g, '<br>')
                  : content;
                setDrawerRenderedContent(formattedContent);
              }
            })
            .catch(err => {
              console.error('Error rendering component for drawer:', err);
              setError('컴포넌트 렌더링에 실패했습니다.');
            });
        }
      }
    }
  }, [previewDrawerOpen, selectedTemplate, selectedComponent, components, variables]);

  // Drawer가 닫힐 때 렌더링된 결과 초기화
  useEffect(() => {
    if (!previewDrawerOpen) {
      setDrawerRenderedContent('');
      setDrawerActiveTab('');
      setSelectedComponent(null);
    }
  }, [previewDrawerOpen]);

  // Drawer 탭 변경 시 렌더링
  const handleDrawerTabChange = async (componentName: string) => {
    setDrawerActiveTab(componentName);
    try {
      const content = await renderComponent(selectedTemplate, componentName);
      if (content) {
        const formattedContent = componentName.startsWith('TEXT_')
          ? content.replace(/\n/g, '<br>')
          : content;
        setDrawerRenderedContent(formattedContent);
      }
    } catch (err) {
      console.error('Error rendering component for drawer:', err);
      setError('컴포넌트 렌더링에 실패했습니다.');
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  // 컴포넌트 프리뷰 패널
  const ComponentPreviewPanel = ({ componentName, index }: { componentName: string; index: number }) => {
    const [content, setContent] = useState<string>('');

    useEffect(() => {
      const loadContent = async () => {
        if (mappedComponents[componentName]) {
          const renderedContent = await renderComponent(selectedTemplate, componentName);
          setContent(renderedContent || '');
        }
      };
      loadContent();
    }, [componentName, mappedComponents[componentName], selectedTemplate]);

    return (
      <TabPanel value={selectedTab} index={index}>
        {mappedComponents[componentName] ? (
          <Box sx={{ p: 2 }}>
            {/* <Typography variant="h6" gutterBottom>
              {componentName} 프리뷰
            </Typography> */}
            <Paper 
              sx={{ 
                p: 2, 
                bgcolor: 'background.paper',
                maxHeight: '60vh',
                overflow: 'auto'
              }}
            >
              {componentName.startsWith('TEXT_') ? (
                <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                  {content}
                </Typography>
              ) : (
                <div dangerouslySetInnerHTML={{ __html: content }} />
              )}
            </Paper>
          </Box>
        ) : (
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <Typography color="text.secondary">
              이 컴포넌트는 아직 매핑되지 않았습니다.
            </Typography>
          </Box>
        )}
      </TabPanel>
    );
  };

  // 스키마에서 기본값 생성 함수
  const generateDefaultValues = (schema: any): any => {
    if (!schema) return {};

    // 배열 타입인 경우
    if (schema.type === 'array') {
      if (schema.default) return schema.default;
      if (schema.items) {
        return [generateDefaultValues(schema.items)];
      }
      return [];
    }

    // 객체 타입인 경우
    if (schema.type === 'object') {
      const result: Record<string, any> = {};
      if (schema.properties) {
        Object.entries(schema.properties).forEach(([key, prop]: [string, any]) => {
          // required 필드이거나 default가 있는 경우에만 처리
          if (schema.required?.includes(key) || prop.default !== undefined) {
            result[key] = generateDefaultValues(prop);
          }
        });
      }
      return result;
    }

    // 기본 타입인 경우
    if (schema.default !== undefined) {
      return schema.default;
    }

    // 타입에 따른 기본값
    switch (schema.type) {
      case 'string':
        return '';
      case 'number':
      case 'integer':
        return 0;
      case 'boolean':
        return false;
      case 'null':
        return null;
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" sx={{ mb: 3 }}>
        템플릿 프리뷰
      </Typography>

      {/* 템플릿 선택 */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack spacing={2}>

          {/* 카테고리별 빠른 선택 */}
          <Box>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              카테고리별 빠른 선택
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {Object.entries(groupedTemplates).map(([category, templates]) => (
                <Chip
                  key={category}
                  label={`${category} (${templates.length})`}
                  onClick={() => {
                    if (categoryFilter === category) {
                      setCategoryFilter(''); // 같은 카테고리 클릭시 필터 해제
                    } else {
                      setCategoryFilter(category); // 다른 카테고리 선택시 필터 적용
                    }
                  }}
                  color={categoryFilter === category ? 'primary' : 'default'}
                  variant={categoryFilter === category ? 'filled' : 'outlined'}
                  sx={{ m: 0.5 }}
                />
              ))}
            </Stack>
          </Box>
          
          <FormControl fullWidth>
            <Autocomplete
              options={filteredTemplates}
              value={selectedTemplate}
              onChange={(_, newValue) => setSelectedTemplate(newValue || '')}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="템플릿 선택"
                  placeholder="템플릿을 선택하세요"
                />
              )}
              renderOption={(props, option) => {
                const { key, ...otherProps } = props;
                return (
                  <li key={key} {...otherProps}>
                    <Box>
                      <Typography variant="body1">
                        {option} ({templates[option]}개의 컴포넌트)
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {getTemplateCategory(option)}
                      </Typography>
                    </Box>
                  </li>
                );
              }}
              groupBy={(option) => getTemplateCategory(option)}
              clearOnBlur={false}
              clearOnEscape
              disableClearable={false}
            />
          </FormControl>

        </Stack>
      </Paper>

      {/* 컴포넌트 목록 */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : selectedTemplate ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* 변수 정보와 스키마 정보 */}
          <Paper sx={{ width: '100%', position: 'sticky', top: 24, zIndex: 1 }}>
            <Tabs
              value={activeTab}
              onChange={(_, newValue) => setActiveTab(newValue)}
              sx={{ borderBottom: 1, borderColor: 'divider' }}
            >
              <Tab label="변수 정보" />
              <Tab label="스키마 정보" />
            </Tabs>
            <Box sx={{ p: 2 }}>
              {activeTab === 0 && (
                <Box>
                  <Box sx={{ height: 400, mb: 2 }}>
                    <Editor
                      height="100%"
                      defaultLanguage="json"
                      value={JSON.stringify(variables, null, 2)}
                      onChange={handleVariablesChange}
                      options={{
                        minimap: { enabled: false },
                        scrollBeyondLastLine: false,
                        fontSize: 14,
                        lineNumbers: 'on',
                        wordWrap: 'on',
                        automaticLayout: true,
                      }}
                    />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 1 }}>
                    <Typography 
                      variant="caption" 
                      color={isVariablesValid ? 'success.main' : 'error.main'}
                      sx={{ 
                        alignSelf: 'center',
                        whiteSpace: 'pre-wrap',
                        fontFamily: 'monospace'
                      }}
                    >
                      {isVariablesValid 
                        ? '✓ 변수 정보가 스키마와 일치합니다' 
                        : '✗ 변수 정보가 스키마와 일치하지 않습니다'}
                    </Typography>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={handleResetVariables}
                      disabled={!selectedTemplate || isLoading}
                      startIcon={isLoading ? <CircularProgress size={16} /> : <RefreshIcon />}
                    >
                      기본값으로 초기화
                    </Button>
                  </Box>
                </Box>
              )}
              {activeTab === 1 && (
                <Typography
                  component="pre"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    fontFamily: 'monospace',
                    fontSize: '0.875rem',
                    m: 0,
                  }}
                >
                  {JSON.stringify(schema, null, 2)}
                </Typography>
              )}
            </Box>
          </Paper>

          {/* 왼쪽: 컴포넌트 목록 */}
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Stack spacing={2}>
              {filteredComponents.map((component) => (
                <Paper
                  key={component.component}
                  sx={{
                    p: 2,
                    borderLeft: '4px solid',
                    borderColor: 'primary.main',
                  }}
                >
                  {/* 헤더 영역 */}
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 1, 
                    mb: 2,
                    flexWrap: 'wrap'
                  }}>
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1
                      }}
                    >
                      {component.component}
                      <Button
                        size="small"
                        onClick={() => {
                          setSelectedComponent(component);
                          setPreviewDrawerOpen(true);
                        }}
                        startIcon={<VisibilityIcon />}
                        sx={{ 
                          color: 'primary.main',
                          transition: 'all 0.2s',
                          borderRadius: 2,
                          px: 2,
                          py: 0.5,
                          textTransform: 'none',
                          fontWeight: 500,
                          fontSize: '0.875rem',
                          boxShadow: 'none',
                          '&:hover': {
                            bgcolor: 'action.hover',
                            boxShadow: 1,
                          }
                        }}
                      >
                        프리뷰
                      </Button>
                      {component.description && (
                        <Typography 
                          variant="caption" 
                          color="text.secondary"
                          sx={{ 
                            fontWeight: 'normal',
                            ml: 1
                          }}
                        >
                          - {component.description}
                        </Typography>
                      )}
                    </Typography>
                  </Box>

                  {/* 레이아웃과 파셜 정보 */}
                  <Box sx={{ mb: 2 }}>
                    <Stack 
                      direction="row" 
                      spacing={1} 
                      flexWrap="wrap" 
                      useFlexGap
                      sx={{ gap: 1 }}
                    >
                      {component.layout && (
                        <Chip
                          label={component.layout}
                          size="small"
                          color="primary"
                          variant="outlined"
                          sx={{ 
                            maxWidth: '100%',
                            '& .MuiChip-label': {
                              whiteSpace: 'normal',
                              textAlign: 'left'
                            }
                          }}
                        />
                      )}
                      {component.partials && component.partials.map((partial) => (
                        <Chip
                          key={partial}
                          label={partial}
                          size="small"
                          variant="outlined"
                          sx={{ 
                            maxWidth: '100%',
                            '& .MuiChip-label': {
                              whiteSpace: 'normal',
                              textAlign: 'left'
                            }
                          }}
                        />
                      ))}
                    </Stack>
                  </Box>

                  {/* 소스 코드 영역 */}
                  <Paper 
                    sx={{ 
                      p: 2, 
                      bgcolor: 'grey.50',
                      overflow: 'auto',
                      maxHeight: '300px'
                    }}
                  >
                    <Typography
                      component="pre"
                      sx={{
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                        fontFamily: 'monospace',
                        fontSize: '0.875rem',
                        m: 0,
                      }}
                    >
                      {component.content || '내용이 없습니다.'}
                    </Typography>
                  </Paper>
                </Paper>
              ))}
            </Stack>
          </Box>
        </Box>
      ) : (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="text.secondary">
            템플릿을 선택해주세요.
          </Typography>
        </Paper>
      )}

      {/* 프리뷰 Drawer */}
      <Drawer
        anchor="right"
        open={previewDrawerOpen}
        onClose={() => setPreviewDrawerOpen(false)}
        PaperProps={{
          sx: { width: '80%', maxWidth: '1200px' }
        }}
      >
        <Box sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">
              {selectedTemplate} 프리뷰
            </Typography>
            <IconButton onClick={() => setPreviewDrawerOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>

          <Box sx={{ width: '100%' }}>
            <Box sx={{ 
              borderBottom: 1, 
              borderColor: 'divider',
              bgcolor: 'background.paper',
              position: 'sticky',
              top: 0,
              zIndex: 2
            }}>
              <Tabs 
                value={selectedTab} 
                onChange={handleTabChange}
                variant="scrollable"
                scrollButtons="auto"
                sx={{
                  '& .MuiTabs-flexContainer': {
                    flexWrap: 'wrap',
                    gap: 1,
                    p: 1
                  },
                  '& .MuiTab-root': {
                    minHeight: 48,
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    mx: 0.5,
                    my: 0.5,
                    transition: 'all 0.2s',
                    '&:hover': {
                      bgcolor: 'action.hover',
                      borderColor: 'primary.main',
                    },
                    '&.Mui-selected': {
                      bgcolor: 'primary.main',
                      color: 'primary.contrastText',
                      borderColor: 'primary.main',
                      '& .MuiSvgIcon-root': {
                        color: 'primary.contrastText'
                      }
                    }
                  }
                }}
              >
                {defaultComponentNames.map((componentName, index) => (
                  <Tab
                    key={componentName}
                    label={
                      <Box sx={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: 1,
                        minWidth: 200,
                        justifyContent: 'space-between'
                      }}>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            fontWeight: 500,
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis'
                          }}
                        >
                          {componentName}
                        </Typography>
                        <Tooltip title={mappedComponents[componentName] ? "매핑됨" : "미매핑"}>
                          {mappedComponents[componentName] ? (
                            <CheckCircleIcon 
                              color="success" 
                              fontSize="small"
                              sx={{ 
                                flexShrink: 0,
                                color: selectedTab === index ? 'inherit' : 'success.main'
                              }} 
                            />
                          ) : (
                            <CancelIcon 
                              color="error" 
                              fontSize="small"
                              sx={{ 
                                flexShrink: 0,
                                color: selectedTab === index ? 'inherit' : 'error.main'
                              }} 
                            />
                          )}
                        </Tooltip>
                      </Box>
                    }
                    {...a11yProps(index)}
                  />
                ))}
              </Tabs>
            </Box>
            {defaultComponentNames.map((componentName, index) => (
              <ComponentPreviewPanel 
                key={componentName}
                componentName={componentName}
                index={index}
              />
            ))}
          </Box>
        </Box>
      </Drawer>

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