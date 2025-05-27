import React, { useState, useEffect, useRef } from 'react';
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
  Refresh as RefreshIcon,
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
  const drawerRef = useRef<HTMLDivElement>(null);

  // Drawer가 열릴 때 레이아웃 상세 정보 불러오기
  useEffect(() => {
    if (isOpen && selectedLayout) {
      const fetchLayoutDetail = async () => {
        try {
          setIsLoading(true);
          const layoutDetail = await api.getLayout(version, selectedLayout.name);
          setName(layoutDetail.name);
          setDescription(layoutDetail.description || '');
          setSourceContent(layoutDetail.content || '');
          setHasChanges(false);
        } catch (err) {
          console.error('Error fetching layout detail:', err);
          setError('레이아웃 상세 정보를 불러오는데 실패했습니다.');
        } finally {
          setIsLoading(false);
        }
      };
      fetchLayoutDetail();
    } else if (isOpen && !selectedLayout) {
      // 새 레이아웃 생성 시 초기화
      setName('');
      setDescription('');
      setSourceContent('');
      setHasChanges(false);
    }
  }, [isOpen, selectedLayout, version]);

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
      handleDrawerClose();
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

      let updatedLayout;
      if (selectedLayout) {
        delete layoutData.name;
        updatedLayout = await api.updateLayout(version, selectedLayout.name, layoutData);
      } else {
        updatedLayout = await api.createLayout(version, layoutData);
      }
      setHasChanges(false);
      setShowSaveDialog(false);
      
      handleDrawerClose();
      onSave(updatedLayout);
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
      handleDrawerClose();
      onDelete(selectedLayout);
      setShowDeleteDialog(false);
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
        ref={drawerRef}
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
              {selectedLayout && (
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={() => {
                    const fetchLayoutDetail = async () => {
                      try {
                        setIsLoading(true);
                        const layoutDetail = await api.getLayout(version, selectedLayout.name);
                        setName(layoutDetail.name);
                        setDescription(layoutDetail.description || '');
                        setSourceContent(layoutDetail.content || '');
                        setHasChanges(false);
                      } catch (err) {
                        console.error('Error fetching layout detail:', err);
                        setError('레이아웃 상세 정보를 불러오는데 실패했습니다.');
                      } finally {
                        setIsLoading(false);
                      }
                    };
                    fetchLayoutDetail();
                  }}
                  disabled={isLoading}
                >
                  새로고침
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
                variant="outlined"
                onClick={handleClose}
                disabled={isLoading}
              >
                취소
              </Button>
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
          </Stack>
        </Box>
      </Drawer>

      {showSaveDialog && (
        <Dialog
          open={showSaveDialog}
          onClose={() => setShowSaveDialog(false)}
          container={document.body}
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
      )}

      {showDeleteDialog && (
        <Dialog
          open={showDeleteDialog}
          onClose={() => setShowDeleteDialog(false)}
          container={document.body}
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
      )}

      {showUnsavedDialog && (
        <Dialog
          open={showUnsavedDialog}
          onClose={() => setShowUnsavedDialog(false)}
          container={document.body}
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
                handleDrawerClose();
              }} 
              color="error"
            >
              닫기
            </Button>
          </DialogActions>
        </Dialog>
      )}
    </>
  );
}

