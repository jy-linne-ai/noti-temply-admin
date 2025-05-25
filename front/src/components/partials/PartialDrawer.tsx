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
} from '@mui/material';
import { 
  Close as CloseIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
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
}

export function PartialDrawer({
  isOpen,
  onClose,
  selectedPartial,
  version,
  onPartialChange,
  onDelete,
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

  // selectedPartial이 변경될 때마다 currentPartial 업데이트
  useEffect(() => {
    if (selectedPartial) {
      setCurrentPartial(selectedPartial);
      setSourceContent(selectedPartial.content || '');
      setPreviewContent(selectedPartial.content || '');
      setName(selectedPartial.name);
      setDescription(selectedPartial.description || '');
    }
  }, [selectedPartial]);

  // 소스 변경 시 프리뷰 업데이트
  useEffect(() => {
    setPreviewContent(sourceContent);
  }, [sourceContent]);

  // 자식 파셜 목록 로드
  const loadChildPartials = async (partialName: string) => {
    try {
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
    if (currentPartial) {
      loadChildPartials(currentPartial.name);
    }
  }, [currentPartial?.name]);

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
        setCurrentPartial(updatedPartial);
        if (onPartialChange) {
          onPartialChange(updatedPartial);
        }
        // 자기 자신을 제외한 파셜만 표시
        const filteredChildren = children.filter(child => child.name !== partialName);
        setChildPartials(filteredChildren);
        setName(updatedPartial.name);
        setDescription(updatedPartial.description || '');
      }
    } catch (err) {
      console.error('Error loading partial:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    onClose();
  };

  const handleDelete = () => {
    if (onDelete) {
      onDelete();
    }
  };

  const handleSave = async () => {
    if (currentPartial) {
      try {
        setIsLoading(true);
        const updatedPartial = {
          ...currentPartial,
          name,
          description,
        };
        await api.updatePartial(version, currentPartial.name, updatedPartial);
        if (onPartialChange) {
          onPartialChange(updatedPartial);
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

  if (!isOpen || !currentPartial) return null;

  return (
    <Drawer
      anchor="right"
      open={isOpen}
      onClose={handleClose}
      PaperProps={{
        sx: { 
          width: {
            xs: '100%',    // 모바일에서는 전체 너비
            sm: '90%',     // 태블릿에서는 90%
            md: '85%',     // 작은 데스크톱에서는 85%
            lg: '80%',     // 큰 데스크톱에서는 80%
            xl: '75%'      // 매우 큰 화면에서는 75%
          },
          maxWidth: '1600px'  // 최대 너비 제한
        }
      }}
      keepMounted={false}
      disablePortal={false}
      disableEnforceFocus={false}
      disableAutoFocus={false}
      sx={{
        '& .MuiDrawer-paper': {
          position: 'absolute',
          height: '100%',
          transition: 'width 0.3s ease-in-out',
        },
        '& .MuiBackdrop-root': {
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
        }
      }}
    >
      <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" component="h2">
            {currentPartial.name}
          </Typography>
          <IconButton onClick={handleClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          height: 'calc(100% - 80px)',
          overflow: 'hidden'
        }}>
          {/* 기본 정보 테이블 */}
          <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: 'grid', gridTemplateColumns: '100px 1fr', gap: 1 }}>
              {/* 설명 */}
              <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                설명
              </Typography>
              <Typography>
                {currentPartial.description || '설명이 없습니다.'}
              </Typography>

              {/* 의존성 */}
              <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                의존성
              </Typography>
              <Box>
                {currentPartial.dependencies && currentPartial.dependencies.length > 0 ? (
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {currentPartial.dependencies.map(dep => (
                      <Chip
                        key={dep}
                        label={dep}
                        variant="outlined"
                        size="small"
                        color="warning"
                        onClick={() => handlePartialClick(dep)}
                        sx={{ cursor: 'pointer' }}
                      />
                    ))}
                  </Box>
                ) : (
                  <Typography color="text.secondary" variant="body2">의존성 없음</Typography>
                )}
              </Box>

              {/* 참조하는 파셜 */}
              <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                참조하는 파셜
              </Typography>
              <Box>
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

              {/* 생성/수정 정보 */}
              <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                생성
              </Typography>
              <Typography variant="body2">
                {formatDate(currentPartial.created_at)}
              </Typography>

              <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                수정
              </Typography>
              <Typography variant="body2">
                {formatDate(currentPartial.updated_at)}
              </Typography>
            </Box>
          </Paper>

          <TextField
            label="이름"
            value={name}
            onChange={(e) => setName(e.target.value)}
            error={!!error}
            helperText={error}
            disabled={isLoading || !!currentPartial}
            fullWidth
          />

          <TextField
            label="설명"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            multiline
            rows={2}
            disabled={isLoading}
            fullWidth
          />

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

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
            <Button
              variant="outlined"
              onClick={() => {
                onClose();
                router.push(`/versions/${version}/partials/${currentPartial.name}`);
              }}
              startIcon={<EditIcon />}
            >
              수정하기
            </Button>
          </Box>
        </Box>
      </Box>
    </Drawer>
  );
} 