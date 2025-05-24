'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  InputAdornment,
  List,
  ListItem,
  ListItemText,
  Paper,
  TextField,
  Typography,
  Chip,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Lock as LockIcon,
} from '@mui/icons-material';

interface Version {
  version: string;
  is_root: boolean;
}

export default function VersionSelectPage() {
  const [versions, setVersions] = useState<Version[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [newVersion, setNewVersion] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [versionToDelete, setVersionToDelete] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchVersions();
  }, []);

  const fetchVersions = async () => {
    try {
      const response = await api.get('/api/v1/versions');
      setVersions(response.data);
    } catch (error) {
      console.error('Failed to fetch versions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVersionSelect = async (version: string) => {
    try {
      // 버전 유효성 체크
      await api.get(`/api/v1/versions/${version}`);
      
      // 쿠키에 버전 저장
      document.cookie = `version=${version}; path=/`;
      
      // 버전별 대시보드로 이동
      router.push(`/versions/${version}/dashboard`);
    } catch (error) {
      console.error('Failed to select version:', error);
      alert('유효하지 않은 버전입니다.');
    }
  };

  const handleCreateVersion = async () => {
    if (!newVersion.trim()) {
      alert('버전을 입력해주세요.');
      return;
    }

    try {
      await api.post('/api/v1/versions', { version: newVersion });
      setNewVersion('');
      setIsCreating(false);
      await fetchVersions();
    } catch (error) {
      console.error('Failed to create version:', error);
      alert('버전 생성에 실패했습니다.');
    }
  };

  const handleDeleteClick = (version: string, isRoot: boolean) => {
    if (isRoot) {
      alert('Root 버전은 삭제할 수 없습니다.');
      return;
    }
    setVersionToDelete(version);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!versionToDelete) return;

    try {
      await api.delete(`/api/v1/versions/${versionToDelete}`);
      await fetchVersions();
    } catch (error) {
      console.error('Failed to delete version:', error);
      alert('버전 삭제에 실패했습니다.');
    } finally {
      setDeleteDialogOpen(false);
      setVersionToDelete(null);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box textAlign="center" mb={4}>
        <Typography variant="h3" component="h1" gutterBottom>
          Noti Temply Admin
        </Typography>
        <Typography variant="h6" color="text.secondary">
          버전을 선택하거나 관리해주세요
        </Typography>
      </Box>

      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" component="h2">
              버전 목록
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setIsCreating(true)}
            >
              새 버전 생성
            </Button>
          </Box>

          {isCreating && (
            <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
              <Box display="flex" gap={1}>
                <TextField
                  fullWidth
                  value={newVersion}
                  onChange={(e) => setNewVersion(e.target.value)}
                  placeholder="새 버전을 입력하세요"
                  variant="outlined"
                  size="small"
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          size="small"
                          onClick={() => {
                            setIsCreating(false);
                            setNewVersion('');
                          }}
                        >
                          <CloseIcon />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
                <Button
                  variant="contained"
                  color="success"
                  startIcon={<CheckIcon />}
                  onClick={handleCreateVersion}
                >
                  생성
                </Button>
              </Box>
            </Paper>
          )}

          <List>
            {versions.map((version) => (
              <ListItem
                key={version.version}
                onClick={() => handleVersionSelect(version.version)}
                sx={{
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 1,
                  mb: 1,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease-in-out',
                  '&:hover': {
                    bgcolor: 'action.hover',
                    transform: 'translateY(-2px)',
                    boxShadow: 1,
                  },
                }}
                secondaryAction={
                  <Tooltip title={version.is_root ? "Root 버전은 삭제할 수 없습니다" : "삭제"}>
                    <span>
                      <IconButton
                        edge="end"
                        color="error"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteClick(version.version, version.is_root);
                        }}
                        disabled={version.is_root}
                      >
                        {version.is_root ? <LockIcon /> : <DeleteIcon />}
                      </IconButton>
                    </span>
                  </Tooltip>
                }
              >
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="h6">{version.version}</Typography>
                      {version.is_root && (
                        <Chip
                          label="Root"
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>

      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>버전 삭제</DialogTitle>
        <DialogContent>
          <Typography>
            정말로 {versionToDelete} 버전을 삭제하시겠습니까?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>취소</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            삭제
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
} 