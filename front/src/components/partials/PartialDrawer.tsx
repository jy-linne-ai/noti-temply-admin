import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Drawer,
  IconButton,
  Button,
  Stack,
  Tabs,
  Tab,
  Chip,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Divider,
  TextField,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  OutlinedInput,
  Autocomplete,
  Snackbar,
  Alert,
} from '@mui/material';
import { 
  Close as CloseIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { PartialTemplate } from '@/types/partial';
import { HtmlEditor } from '@/components/Editor';
import { Preview } from '@/components/Preview';
import { useApi } from '@/lib/api';
import { formatDate } from '@/lib/utils';

interface PartialDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  selectedPartial: PartialTemplate | null;
  version: string;
  onPartialChange?: (partial: PartialTemplate) => void;
  onDelete?: () => void;
  onSave?: (partial: Partial<PartialTemplate>) => Promise<void>;
  onNew?: () => void;
}

export function PartialDrawer({
  isOpen,
  onClose,
  selectedPartial,
  version,
  onPartialChange,
  onDelete,
  onSave,
  onNew,
}: PartialDrawerProps) {
  const router = useRouter();
  const api = useApi();
  const [contentTab, setContentTab] = useState(0);
  const [childPartials, setChildPartials] = useState<PartialTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPartial, setCurrentPartial] = useState<PartialTemplate | null>(null);
  const [sourceContent, setSourceContent] = useState('');
  const [previewContent, setPreviewContent] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [dependencyError, setDependencyError] = useState('');
  const [hasChanges, setHasChanges] = useState(false);
  const [availablePartials, setAvailablePartials] = useState<PartialTemplate[]>([]);
  const [selectedDependency, setSelectedDependency] = useState<string>('');
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success'
  });

  // selectedPartial이 변경될 때마다 currentPartial 업데이트
  useEffect(() => {
    if (selectedPartial) {
      setCurrentPartial(selectedPartial);
      setSourceContent(selectedPartial.content || '');
      setPreviewContent(selectedPartial.content || '');
      setName(selectedPartial.name);
      setDescription(selectedPartial.description || '');
      // 파셜 목록 로드 - 초기 로드 시에만 실행
      if (availablePartials.length === 0) {
        loadAvailablePartials();
      }
    } else {
      // 새로 만들기 시 상태 초기화
      setCurrentPartial({
        name: '',
        description: '',
        content: '',
        dependencies: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        version: version,
        layout: 'default'
      });
      setSourceContent('');
      setPreviewContent('');
      setName('');
      setDescription('');
      setError('');
      setDependencyError('');
      setSelectedDependency('');
      setChildPartials([]);
      // 새로 만들기 시에도 의존성 리스트는 초기 로드 시에만 실행
      if (availablePartials.length === 0) {
        loadAvailablePartials();
      }
    }
  }, [selectedPartial, version]);

  // 의존성 추가/제거 시에만 파셜 목록 업데이트
  useEffect(() => {
    if (currentPartial?.dependencies) {
      setAvailablePartials(prev => 
        prev.map(p => ({
          ...p,
          isAdded: currentPartial.dependencies?.includes(p.name) || false
        }))
      );
    }
  }, [currentPartial?.dependencies]);

  // 소스 변경 시 프리뷰 업데이트
  useEffect(() => {
    setPreviewContent(sourceContent);
  }, [sourceContent]);

  // 자식 파셜 목록 로드
  const loadChildPartials = async (partialName: string) => {
    try {
      // 빈 이름인 경우 조회하지 않음
      if (!partialName) return;

      setIsLoading(true);
      const children = await api.getPartialChildren(version, partialName);
      // 자기 자신을 제외한 파셜만 표시
      const filteredChildren = children.filter(child => child.name !== partialName);
      setChildPartials(filteredChildren);
    } catch (err) {
      console.error('Error loading child partials:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 선택된 파셜이 변경될 때마다 자식 파셜 목록 로드
  useEffect(() => {
    if (currentPartial?.name) {
      loadChildPartials(currentPartial.name);
    }
  }, [currentPartial?.name]);

  // 사용 가능한 파셜 목록 로드
  const loadAvailablePartials = async () => {
    try {
      console.log('=== 파셜 목록 로드 시작 ===');
      // 루트 파셜 목록 가져오기 (is_root=true인 파셜만)
      const rootPartials = await api.getPartials(version, true);
      console.log('루트 파셜 목록:', rootPartials);
      
      // 재귀적으로 자식 파셜을 로드하는 함수
      const loadChildrenRecursively = async (partial: PartialTemplate, depth: number = 0, rootName: string): Promise<Array<PartialTemplate & { depth: number; root_name: string }>> => {
        try {
          console.log(`[${depth}단계] ${partial.name}의 자식 파셜 로드 시작`);
          // 최대 깊이 제한 (무한 루프 방지)
          if (depth > 10) {
            console.warn(`Maximum depth reached for partial: ${partial.name}`);
            return [];
          }

          // 자식 파셜 목록 조회
          const children = await api.getPartialChildren(version, partial.name);
          console.log(`[${depth}단계] ${partial.name}의 자식 파셜:`, children);
          
          // 각 자식 파셜에 대해 재귀적으로 하위 파셜 로드
          const childrenWithSubChildren = await Promise.all(
            children.map(child => loadChildrenRecursively(child, depth + 1, rootName))
          );

          // 현재 파셜과 모든 하위 파셜을 하나의 배열로 합침
          const result = [
            { ...partial, depth, root_name: rootName },
            ...childrenWithSubChildren.flat()
          ];
          console.log(`[${depth}단계] ${partial.name}의 전체 하위 파셜:`, result);
          return result;
        } catch (err) {
          console.error(`Error loading children for ${partial.name}:`, err);
          return [{ ...partial, depth, root_name: rootName }];
        }
      };

      // 모든 루트 파셜의 하위 파셜을 재귀적으로 로드
      const allPartials = await Promise.all(
        rootPartials.map(partial => loadChildrenRecursively(partial, 0, partial.name))
      );
      console.log('모든 파셜 목록:', allPartials);

      // 중복 제거 및 필터링 (자기 자신만 제외)
      const uniquePartials = Array.from(
        new Map(
          allPartials.flat()
            .filter(p => p.name !== currentPartial?.name) // 자기 자신만 제외
            .map(p => [p.name, p])
        ).values()
      );
      console.log('중복 제거 후 파셜 목록:', uniquePartials);

      // 현재 의존성 상태에 따라 isAdded 설정
      const partialsWithAddedState = uniquePartials.map(p => ({
        ...p,
        isAdded: currentPartial?.dependencies?.includes(p.name) || false
      }));
      console.log('최종 파셜 목록:', partialsWithAddedState);

      setAvailablePartials(partialsWithAddedState);
    } catch (err) {
      console.error('Error loading available partials:', err);
    }
  };

  // 파셜 클릭 핸들러 (자식 파셜과 의존성 모두에서 사용)
  const handlePartialClick = async (partialName: string) => {
    try {
      setIsLoading(true);
      // 파셜 정보와 자식 파셜 목록을 병렬로 로드
      const [updatedPartial, children] = await Promise.all([
        api.getPartial(version, partialName),
        api.getPartialChildren(version, partialName)
      ]);

      if (updatedPartial) {
        // 현재 파셜 정보 업데이트
        setCurrentPartial(updatedPartial);
        // 컨텐츠 업데이트
        setSourceContent(updatedPartial.content || '');
        setPreviewContent(updatedPartial.content || '');
        setName(updatedPartial.name);
        setDescription(updatedPartial.description || '');
        setHasChanges(false);
        
        // 부모 컴포넌트에 변경 알림
        if (onPartialChange) {
          onPartialChange(updatedPartial);
        }
        
        // 자기 자신을 제외한 파셜만 표시
        const filteredChildren = children.filter(child => child.name !== partialName);
        setChildPartials(filteredChildren);

        // 의존성 목록 다시 로드
        await loadAvailablePartials();
      }
    } catch (err) {
      console.error('Error loading partial:', err);
      setError('파셜을 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // 의존성 추가
  const handleAddDependency = () => {
    if (!selectedDependency) return;
    
    // 이미 추가된 파셜인지 확인
    if (currentPartial?.dependencies?.includes(selectedDependency)) {
      setDependencyError('이미 추가된 파셜입니다.');
      return;
    }

    const updatedDependencies = [
      ...(currentPartial?.dependencies || []),
      selectedDependency
    ];

    setCurrentPartial(prev => prev ? {
      ...prev,
      dependencies: updatedDependencies
    } : null);

    // 선택된 의존성의 상태만 업데이트
    setAvailablePartials(prev => 
      prev.map(p => ({
        ...p,
        isAdded: p.name === selectedDependency ? true : p.isAdded
      }))
    );
    setSelectedDependency('');
    setDependencyError('');
  };

  // 의존성 제거
  const handleRemoveDependency = (dependencyName: string) => {
    const updatedDependencies = currentPartial?.dependencies?.filter(
      dep => dep !== dependencyName
    ) || [];

    setCurrentPartial(prev => prev ? {
      ...prev,
      dependencies: updatedDependencies
    } : null);

    // 제거된 의존성의 상태만 업데이트
    setAvailablePartials(prev => 
      prev.map(p => ({
        ...p,
        isAdded: p.name === dependencyName ? false : p.isAdded
      }))
    );
  };

  // 파셜 삭제 시 상태 초기화
  const handleDelete = () => {
    if (onDelete) {
      if (window.confirm('정말로 이 파셜을 삭제하시겠습니까?')) {
        // 의존성 목록 초기화
        setAvailablePartials(prev => 
          prev.map(p => ({
            ...p,
            isAdded: false
          }))
        );
        onDelete();
      }
    }
  };

  // 새로고침 시 상태 초기화
  const handleRefresh = async () => {
    try {
      setIsLoading(true);
      // 현재 선택된 파셜이 있는 경우, 해당 파셜의 정보를 다시 로드
      if (selectedPartial) {
        const updatedPartial = await api.getPartial(version, selectedPartial.name);
        setCurrentPartial(updatedPartial);
        setName(updatedPartial.name);
        setDescription(updatedPartial.description || '');
        setSourceContent(updatedPartial.content || '');
        setPreviewContent(updatedPartial.content || '');
      }
      // 의존성 목록 다시 로드
      await loadAvailablePartials();
      setSnackbar({
        open: true,
        message: "새로고침이 완료되었습니다.",
        severity: "success"
      });
    } catch (err) {
      console.error('Error refreshing:', err);
      setSnackbar({
        open: true,
        message: "새로고침에 실패했습니다.",
        severity: "error"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    onClose();
  };

  const handleSave = async () => {
    // 필수 필드 검증
    if (!name.trim()) {
      setError('이름은 필수 입력 항목입니다.');
      return;
    }
    if (!sourceContent.trim()) {
      setError('소스 내용은 필수 입력 항목입니다.');
      return;
    }

    if (currentPartial) {
      try {
        setIsLoading(true);
        const updatedPartial = {
          ...currentPartial,
          name,
          description,
          content: sourceContent,
        };
        
        if (onSave) {
          await onSave(updatedPartial);
        } else {
          await api.updatePartial(version, currentPartial.name, updatedPartial);
          if (onPartialChange) {
            onPartialChange(updatedPartial);
          }
        }
        onClose();
      } catch (err) {
        console.error('Error updating partial:', err);
        setError('파셜을 저장하는 동안 오류가 발생했습니다.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  if (!isOpen) return null;

  return (
    <Drawer
      anchor="right"
      open={isOpen}
      onClose={handleClose}
      PaperProps={{
        sx: { width: '80%', maxWidth: '1200px' },
        elevation: 8
      }}
    >
      <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">
            {selectedPartial ? '파셜 수정' : '새 파셜 만들기'}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={handleRefresh}
              disabled={isLoading}
            >
              새로고침
            </Button>
            {selectedPartial && (
              <Button
                variant="outlined"
                color="error"
                startIcon={<DeleteIcon />}
                onClick={handleDelete}
                disabled={isLoading}
              >
                삭제
              </Button>
            )}
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSave}
              disabled={isLoading}
            >
              저장
            </Button>
            {onNew && (
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={() => {
                  setName('');
                  setDescription('');
                  setSourceContent('');
                  setPreviewContent('');
                  setHasChanges(false);
                  setError('');
                  setDependencyError('');
                  setSelectedDependency('');
                  setChildPartials([]);
                  setAvailablePartials([]);
                  onNew();
                }}
                disabled={isLoading}
              >
                새로 만들기
              </Button>
            )}
            <Button
              variant="outlined"
              onClick={onClose}
            >
              닫기
            </Button>
          </Box>
        </Box>

        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          height: 'calc(100% - 80px)',
          overflow: 'auto',
          pt: 2
        }}>

          <TextField
            label="이름"
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={!!error}
            helperText={error}
            disabled={isLoading || !!currentPartial?.name}
            required
            fullWidth
            sx={{ 
              mb: 2,
              '& .MuiInputLabel-root': {
                fontSize: '1rem',
                fontWeight: 500,
                color: 'text.primary',
                '&.Mui-focused': {
                  color: 'primary.main',
                },
              },
              '& .MuiOutlinedInput-root': {
                '&:hover fieldset': {
                  borderColor: 'primary.main',
                },
                '&.Mui-focused fieldset': {
                  borderColor: 'primary.main',
                  borderWidth: 2,
                },
              },
            }}
          />

          <TextField
            label="설명"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={2}
            disabled={isLoading}
            fullWidth
            sx={{ 
              mb: 2,
              '& .MuiInputLabel-root': {
                fontSize: '1rem',
                fontWeight: 500,
                color: 'text.primary',
                '&.Mui-focused': {
                  color: 'primary.main',
                },
              },
              '& .MuiOutlinedInput-root': {
                '&:hover fieldset': {
                  borderColor: 'primary.main',
                },
                '&.Mui-focused fieldset': {
                  borderColor: 'primary.main',
                  borderWidth: 2,
                },
              },
            }}
          />

          {/* 기본 정보 테이블 */}
          <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {/* 의존성 */}
              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  의존성
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                  <Autocomplete
                    value={selectedDependency}
                    onChange={(_, newValue) => {
                      if (newValue && currentPartial?.dependencies?.includes(newValue)) {
                        setDependencyError('이미 추가된 파셜입니다.');
                        return;
                      }
                      if (newValue === currentPartial?.name) {
                        setDependencyError('자기 자신은 의존성으로 추가할 수 없습니다.');
                        return;
                      }
                      setSelectedDependency(newValue || '');
                      setDependencyError('');
                    }}
                    options={availablePartials
                      .filter(p => p.name !== currentPartial?.name) // 자기 자신 제외
                      .map(p => p.name)}
                    disabled={availablePartials.length === 0}
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label="의존성 추가"
                        size="small"
                        fullWidth
                        error={!!dependencyError}
                        helperText={dependencyError}
                      />
                    )}
                    renderOption={(props, option) => {
                      const partial = availablePartials.find(p => p.name === option);
                      const isAdded = currentPartial?.dependencies?.includes(option);
                      if (!partial) return null;

                      // key를 제외한 나머지 props
                      const { key, ...otherProps } = props;

                      return (
                        <li 
                          key={key}
                          {...otherProps}
                          style={{ 
                            opacity: isAdded ? 0.5 : 1,
                            pointerEvents: isAdded ? 'none' : 'auto'
                          }}
                        >
                          <Box sx={{ 
                            display: 'flex', 
                            flexDirection: 'column', 
                            width: '100%',
                            pl: ((partial.depth || 0) * 2) + 2,
                          }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                              {(partial.depth || 0) > 0 && (
                                <Box 
                                  component="span" 
                                  sx={{ 
                                    width: '12px', 
                                    height: '1px', 
                                    bgcolor: 'divider',
                                    mr: 1,
                                    position: 'relative',
                                    '&::before': {
                                      content: '""',
                                      position: 'absolute',
                                      left: 0,
                                      top: 0,
                                      width: '1px',
                                      height: '100%',
                                      bgcolor: 'divider',
                                    }
                                  }} 
                                />
                              )}
                              <Typography 
                                variant="body2" 
                                sx={{ 
                                  fontWeight: 500,
                                  color: isAdded ? 'text.secondary' : 'text.primary',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 0.5
                                }}
                              >
                                {partial.name}
                                {isAdded && (
                                  <Typography 
                                    component="span" 
                                    variant="caption" 
                                    color="success.main"
                                    sx={{ ml: 1 }}
                                  >
                                    (추가됨)
                                  </Typography>
                                )}
                              </Typography>
                              <Typography 
                                variant="caption" 
                                color="text.secondary"
                                sx={{ ml: 'auto' }}
                              >
                                {partial.name}
                              </Typography>
                            </Box>
                            {partial.description && (
                              <Typography 
                                variant="caption" 
                                color="text.secondary"
                                sx={{ 
                                  pl: (partial.depth || 0) > 0 ? '24px' : 0,
                                  mt: 0.5
                                }}
                              >
                                {partial.description}
                              </Typography>
                            )}
                          </Box>
                        </li>
                      );
                    }}
                    filterOptions={(options, { inputValue }) => {
                      const searchTerm = inputValue.toLowerCase();
                      return options.filter(option => {
                        const partial = availablePartials.find(p => p.name === option);
                        if (!partial) return false;
                        
                        return (
                          partial.name.toLowerCase().includes(searchTerm) ||
                          (partial.description || '').toLowerCase().includes(searchTerm)
                        );
                      });
                    }}
                    isOptionEqualToValue={(option, value) => option === value}
                    getOptionLabel={(option) => option}
                    sx={{ flex: 1 }}
                  />
                  <Button
                    variant="contained"
                    onClick={handleAddDependency}
                    disabled={!selectedDependency || !!dependencyError}
                    sx={{ minWidth: '100px' }}
                  >
                    추가
                  </Button>
                </Box>
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  {currentPartial?.dependencies && currentPartial.dependencies.length > 0 ? (
                    currentPartial.dependencies.map(dep => (
                      <Chip
                        key={dep}
                        label={dep}
                        variant="outlined"
                        size="small"
                        color="warning"
                        onClick={() => handlePartialClick(dep)}
                        onDelete={() => handleRemoveDependency(dep)}
                        sx={{ cursor: 'pointer' }}
                      />
                    ))
                  ) : (
                    <Typography color="text.secondary" variant="body2">의존성 없음</Typography>
                  )}
                </Box>
              </Box>

              {/* 참조하는 파셜 - 수정 시에만 표시 */}
              {selectedPartial && (
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    이 파셜을 참조하는 파셜들
                  </Typography>
                  {isLoading ? (
                    <Typography>로딩 중...</Typography>
                  ) : childPartials.length > 0 ? (
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {childPartials.map(child => (
                        <Chip
                          key={child.name}
                          label={child.name}
                          variant="outlined"
                          size="small"
                          color="info"
                          onClick={() => handlePartialClick(child.name)}
                          sx={{ cursor: 'pointer' }}
                        />
                      ))}
                    </Box>
                  ) : (
                    <Typography color="text.secondary" variant="body2">이 파셜을 참조하는 파셜이 없습니다.</Typography>
                  )}
                </Box>
              )}

              {/* 생성/수정 정보 - 수정 시에만 표시 */}
              {selectedPartial && (
                <Box sx={{ display: 'flex', gap: 4 }}>
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      생성
                    </Typography>
                    <Typography variant="body2">
                      {formatDate(currentPartial?.created_at || null)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {currentPartial?.created_by || '알 수 없음'}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      수정
                    </Typography>
                    <Typography variant="body2">
                      {formatDate(currentPartial?.updated_at || null)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {currentPartial?.updated_by || '알 수 없음'}
                    </Typography>
                  </Box>
                </Box>
              )}
            </Box>
          </Paper>
          {/* 컨텐츠 탭 */}
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
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
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    flex: 1,
                    minHeight: 0,
                    overflow: 'hidden'
                  }}
                >
                  <HtmlEditor
                    value={sourceContent}
                    onChange={(newContent) => {
                      setSourceContent(newContent);
                    }}
                    type="partial"
                    height="100%"
                  />
                </Paper>
              </Box>
            )}

            {contentTab === 1 && (
              <Box sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
                <Preview
                  content={previewContent}
                  title="파셜 프리뷰"
                  type="partial"
                />
              </Box>
            )}
          </Box>
        </Box>
      </Box>

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
    </Drawer>
  );
} 