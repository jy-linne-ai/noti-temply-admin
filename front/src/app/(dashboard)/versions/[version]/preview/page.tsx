'use client';

import React, { useState, useEffect, useMemo } from 'react';
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
} from '@mui/material';
import { Search as SearchIcon, Visibility as VisibilityIcon, Close as CloseIcon } from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { TemplateComponent } from '@/types/template';
import Editor from '@monaco-editor/react';
import { Preview } from '@/components/Preview';

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

  // 템플릿 목록 로드
  const loadTemplates = async () => {
    try {
      setIsLoading(true);
      const templateNames = await api.getTemplateComponentCounts(params.version as string);
      setTemplates(templateNames);
    } catch (err) {
      console.error('Error loading templates:', err);
      setError('템플릿 목록을 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // 컴포넌트 로드
  const loadComponents = async (templateName: string) => {
    try {
      setIsLoading(true);
      // 먼저 변수 정보와 스키마 정보를 로드
      const [schema, variables, defaultComponentNames] = await Promise.all([
        api.getTemplateSchema(params.version as string, templateName),
        api.getTemplateVariables(params.version as string, templateName),
        api.getDefaultComponentNames()
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

  // 초기 데이터 로드
  useEffect(() => {
    loadTemplates();
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
      setIsVariablesValid(true);
    } catch (err) {
      setIsVariablesValid(false);
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
        // 선택된 컴포넌트가 없으면 첫 번째 컴포넌트의 탭을 활성화
        const firstComponent = components[0];
        setDrawerActiveTab(firstComponent.component);
        renderComponent(selectedTemplate, firstComponent.component)
          .then(content => {
            if (content) {
              const formattedContent = firstComponent.component.startsWith('TEXT_')
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

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" sx={{ mb: 3 }}>
        템플릿 프리뷰
      </Typography>

      {/* 템플릿 선택 */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Stack spacing={2}>
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
                      onValidate={(markers) => {
                        setIsVariablesValid(markers.length === 0);
                      }}
                    />
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                    <Typography 
                      variant="caption" 
                      color={isVariablesValid ? 'text.secondary' : 'error'}
                      sx={{ alignSelf: 'center' }}
                    >
                      {isVariablesValid ? 'JSON 형식이 올바릅니다' : 'JSON 형식이 올바르지 않습니다'}
                    </Typography>
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
                        flexShrink: 0,
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
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        flex: '1 1 auto',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1
                      }}
                    >
                      {component.component}
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
                          label={`레이아웃: ${component.layout}`}
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
                          label={`파셜: ${partial}`}
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
          sx: {
            width: '80%',
            maxWidth: '1200px',
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
          },
        }}
      >
        <Box sx={{ 
          p: 2, 
          height: '100%', 
          display: 'flex', 
          flexDirection: 'column',
          overflow: 'hidden'
        }}>
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            mb: 2,
            flexShrink: 0
          }}>
            <Typography variant="h5" sx={{ fontWeight: 500 }}>
              {selectedTemplate}
            </Typography>
            <IconButton onClick={() => setPreviewDrawerOpen(false)}>
              <CloseIcon />
            </IconButton>
          </Box>

          {/* 컴포넌트 탭 */}
          <Tabs
            value={drawerActiveTab || false}
            onChange={(_, newValue) => handleDrawerTabChange(newValue)}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ 
              borderBottom: 1, 
              borderColor: 'divider',
              mb: 2,
              flexShrink: 0
            }}
          >
            {components.map((component) => (
              <Tab
                key={component.component}
                label={component.component}
                value={component.component}
              />
            ))}
          </Tabs>

          <Box sx={{ 
            flex: 1, 
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            bgcolor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
          }}>
            {drawerActiveTab && (
              <iframe
                srcDoc={`
                  <!DOCTYPE html>
                  <html>
                    <head>
                      <style>
                        html, body {
                          margin: 0;
                          padding: 0;
                          min-height: 100%;
                          width: 100%;
                        }
                        body {
                          font-family: Arial, sans-serif;
                          font-size: 14px;
                          line-height: 1.5;
                          color: #333;
                        }
                        .container {
                          padding: 20px;
                          box-sizing: border-box;
                        }
                        pre {
                          white-space: pre-wrap;
                          word-break: break-word;
                          font-family: monospace;
                          font-size: 0.875rem;
                          margin: 0;
                        }
                      </style>
                      <script>
                        function updateHeight() {
                          const height = document.documentElement.scrollHeight;
                          window.parent.postMessage({ type: 'resize', height }, '*');
                        }
                        
                        window.addEventListener('load', updateHeight);
                        
                        // MutationObserver 설정을 DOMContentLoaded 이벤트 이후로 이동
                        document.addEventListener('DOMContentLoaded', function() {
                          const observer = new MutationObserver(updateHeight);
                          observer.observe(document.documentElement, {
                            childList: true,
                            subtree: true,
                            characterData: true
                          });
                        });
                        
                        // 이미지 로드 이벤트 리스너
                        document.addEventListener('load', function(e) {
                          if (e.target.tagName === 'IMG') {
                            updateHeight();
                          }
                        }, true);
                      </script>
                    </head>
                    <body>
                      <div class="container">
                        ${drawerRenderedContent}
                      </div>
                    </body>
                  </html>
                `}
                style={{
                  width: '100%',
                  border: 'none',
                  overflow: 'hidden',
                  flex: 1,
                }}
                title="Preview"
              />
            )}
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