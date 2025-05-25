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
  TextField,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Chip,
} from '@mui/material';
import { 
  Close as CloseIcon,
  Save as SaveIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { Layout } from '@/types/layout';
import { HtmlEditor } from '@/components/Editor';
import { Preview } from '@/components/Preview';
import { formatDate } from '@/lib/utils';
import { useApi } from '@/lib/api';

interface LayoutDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  selectedLayout: Layout | null;
  onLayoutClick: (layout: Layout) => void;
  version: string;
  onSave: (layout: Layout) => Promise<void>;
  onNew?: () => void;
  onDelete?: (layout: Layout) => void;
}

export function LayoutDrawer({
  isOpen,
  onClose,
  selectedLayout,
  onLayoutClick,
  version,
  onSave,
  onNew,
  onDelete,
}: LayoutDrawerProps) {
  const [contentTab, setContentTab] = useState(0);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [sourceContent, setSourceContent] = useState('');
  const [previewContent, setPreviewContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [showUnsavedDialog, setShowUnsavedDialog] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const api = useApi();

  // 초기 데이터 로드
  useEffect(() => {
    if (selectedLayout) {
      setName(selectedLayout.name);
      setDescription(selectedLayout.description || '');
      setSourceContent(selectedLayout.content || '');
      setPreviewContent(selectedLayout.content || '');
      setHasChanges(false);
    } else {
      setName('');
      setDescription('');
      setSourceContent('');
      setPreviewContent('');
      setHasChanges(false);
    }
  }, [selectedLayout]);

  // 변경사항 체크
  useEffect(() => {
    if (!selectedLayout) return;
    
    const hasDescriptionChanged = description !== (selectedLayout.description || '');
    const hasContentChanged = sourceContent !== (selectedLayout.content || '');
    
    setHasChanges(hasDescriptionChanged || hasContentChanged);
  }, [name, description, sourceContent, selectedLayout]);

  // 소스 변경 시 프리뷰 업데이트
  useEffect(() => {
    setPreviewContent(sourceContent);
  }, [sourceContent]);

  const handleDrawerClose = () => {
    onClose();
  };

  const handleClose = () => {
    if (hasChanges) {
      setShowUnsavedDialog(true);
    } else {
      // 포커스를 Drawer 외부로 이동
      const activeElement = document.activeElement as HTMLElement;
      if (activeElement) {
        activeElement.blur();
      }
      // 약간의 지연 후 Drawer 닫기
      requestAnimationFrame(() => {
        handleDrawerClose();
      });
    }
  };

  const handleSave = async () => {
    if (!name.trim()) {
      setError('이름을 입력해주세요.');
      return;
    }

    setShowSaveDialog(true);
  };

  const handleSaveConfirm = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const layoutData: Partial<Layout> = {
        name: name.trim(),
        description: description.trim() || undefined,
        content: sourceContent,
      };

      if (selectedLayout) {
        delete layoutData.name;
        const updatedLayout = await api.updateLayout(version, selectedLayout.name, layoutData);
        await onSave(updatedLayout);
      } else {
        const newLayout = await api.createLayout(version, layoutData);
        await onSave(newLayout);
      }
      setHasChanges(false);
      setShowSaveDialog(false);
      
      // 포커스를 Drawer 외부로 이동
      const activeElement = document.activeElement as HTMLElement;
      if (activeElement) {
        activeElement.blur();
      }
      // 약간의 지연 후 Drawer 닫기
      requestAnimationFrame(() => {
        onClose();
      });
    } catch (err) {
      console.error('Error saving layout:', err);
      setError('레이아웃 저장에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = () => {
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = () => {
    if (selectedLayout && onDelete) {
      // 포커스를 Drawer 외부로 이동
      const activeElement = document.activeElement as HTMLElement;
      if (activeElement) {
        activeElement.blur();
      }
      // 약간의 지연 후 삭제 실행 및 Drawer 닫기
      requestAnimationFrame(() => {
        onDelete(selectedLayout);
        setShowDeleteDialog(false);
        onClose();
      });
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <Drawer
        anchor="right"
        open={isOpen}
        onClose={handleDrawerClose}
        keepMounted
        PaperProps={{
          sx: { width: '80%', maxWidth: '1200px' },
          elevation: 8
        }}
      >
        <Box 
          sx={{ 
            p: 3, 
            height: '100%', 
            display: 'flex', 
            flexDirection: 'column',
            '&:focus': {
              outline: 'none'
            }
          }}
          role="dialog"
          aria-modal="true"
          aria-labelledby="drawer-title"
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5" component="h2" id="drawer-title">
              {selectedLayout ? '레이아웃 수정' : '레이아웃 추가'}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
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
                    onNew();
                  }}
                  disabled={isLoading}
                >
                  새로 만들기
                </Button>
              )}
              <IconButton 
                onClick={handleClose} 
                size="small"
                aria-label="닫기"
              >
                <CloseIcon />
              </IconButton>
            </Box>
          </Box>

          <Stack spacing={3} sx={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>

            <TextField
              label="이름"
              value={name}
              onChange={(e) => setName(e.target.value)}
              error={!!error}
              helperText={error}
              disabled={isLoading || !!selectedLayout}
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
            {/* 기본 정보 */}
            {selectedLayout && (
              <Paper variant="outlined" sx={{ p: 2 }}>
                <Box sx={{ display: 'grid', gridTemplateColumns: '100px 1fr', gap: 1 }}>
                  
                  {/* 생성/수정 정보 */}
                  <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                    생성
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                    <Typography variant="body2">
                      {formatDate(selectedLayout.created_at)}
                    </Typography>
                    {selectedLayout.created_by && (
                      <Chip
                        label={`by ${selectedLayout.created_by}`}
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
                      {formatDate(selectedLayout.updated_at)}
                    </Typography>
                    {selectedLayout.updated_by && (
                      <Chip
                        label={`by ${selectedLayout.updated_by}`}
                        size="small"
                        variant="outlined"
                        color="primary"
                      />
                    )}
                  </Box>
                </Box>
              </Paper>
            )}

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
                      type="layout"
                      height="100%"
                    />
                  </Paper>
                </Box>
              )}

              {contentTab === 1 && (
                <Box sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
                  <Preview
                    content={previewContent}
                    title="레이아웃 프리뷰"
                    type="layout"
                  />
                </Box>
              )}
            </Box>

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 'auto' }}>
              <Button
                variant="outlined"
                onClick={handleClose}
                disabled={isLoading}
              >
                취소
              </Button>
              {selectedLayout && onDelete && (
                <Button
                  variant="outlined"
                  color="error"
                  onClick={handleDelete}
                  disabled={isLoading}
                  startIcon={<DeleteIcon />}
                >
                  삭제
                </Button>
              )}
              <Button
                variant="contained"
                onClick={handleSave}
                disabled={isLoading}
                startIcon={isLoading ? <CircularProgress size={20} /> : <SaveIcon />}
              >
                저장
              </Button>
            </Box>
          </Stack>
        </Box>
      </Drawer>

      {/* 저장되지 않은 변경사항 확인 다이얼로그 */}
      <Dialog
        open={showUnsavedDialog}
        onClose={() => setShowUnsavedDialog(false)}
      >
        <DialogTitle>저장되지 않은 변경사항</DialogTitle>
        <DialogContent>
          <DialogContentText>
            저장되지 않은 변경사항이 있습니다. 정말로 닫으시겠습니까?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowUnsavedDialog(false)}>
            취소
          </Button>
          <Button 
            onClick={() => {
              setShowUnsavedDialog(false);
              onClose();
            }} 
            color="error"
          >
            닫기
          </Button>
        </DialogActions>
      </Dialog>

      {/* 저장 확인 다이얼로그 */}
      <Dialog
        open={showSaveDialog}
        onClose={() => setShowSaveDialog(false)}
      >
        <DialogTitle>레이아웃 저장</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {selectedLayout 
              ? '레이아웃을 저장하시겠습니까?' 
              : '새로운 레이아웃을 생성하시겠습니까?'}
          </DialogContentText>
          {hasChanges && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2" color="warning.main">
                * 변경사항이 있습니다.
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setShowSaveDialog(false)}
            disabled={isLoading}
          >
            취소
          </Button>
          <Button 
            onClick={handleSaveConfirm}
            color="primary"
            disabled={isLoading}
            startIcon={isLoading ? <CircularProgress size={20} /> : null}
          >
            저장
          </Button>
        </DialogActions>
      </Dialog>

      {/* 삭제 확인 다이얼로그 */}
      <Dialog
        open={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
      >
        <DialogTitle>레이아웃 삭제</DialogTitle>
        <DialogContent>
          <DialogContentText>
            정말로 이 레이아웃을 삭제하시겠습니까?
            이 작업은 되돌릴 수 없습니다.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setShowDeleteDialog(false)}
            disabled={isLoading}
          >
            취소
          </Button>
          <Button 
            onClick={handleDeleteConfirm}
            color="error"
            disabled={isLoading}
          >
            삭제
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

