"use client";

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  Button,
  Snackbar,
  Alert,
  Tabs,
  Tab,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Chip,
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { PartialTemplate } from '@/types/partial';
import { PartialEditor } from '@/components/features/partials/PartialEditor';
import { HtmlEditor } from '@/components/Editor';

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
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
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

export default function PartialDetailPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApi();
  const [partial, setPartial] = useState<PartialTemplate | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    fetchPartial();
  }, [params.version, params.partial]);

  const fetchPartial = async () => {
    try {
      const response = await api.getPartial(params.version as string, params.partial as string);
      setPartial(response);
    } catch (err) {
      console.error('Error fetching partial:', err);
      setError('파셜을 불러오는데 실패했습니다.');
    }
  };

  const handleEdit = async (data: Partial<PartialTemplate>) => {
    try {
      const updatedPartial = await api.updatePartial(
        params.version as string,
        params.partial as string,
        data
      );
      setPartial(updatedPartial);
      setIsEditDialogOpen(false);
      setError(null);
    } catch (err) {
      console.error('Error updating partial:', err);
      setError('파셜 수정에 실패했습니다.');
    }
  };

  const handleDelete = async () => {
    try {
      await api.deletePartial(params.version as string, params.partial as string);
      setIsDeleteDialogOpen(false);
      setError(null);
      setTimeout(() => {
        router.push(`/versions/${params.version}/partials`);
      }, 100);
    } catch (err: any) {
      console.error('Error deleting partial:', err);
      if (err.response?.status === 404) {
        setError('파셜이 이미 삭제되었습니다.');
        setTimeout(() => {
          router.push(`/versions/${params.version}/partials`);
        }, 1000);
      } else {
        setError('파셜 삭제에 실패했습니다.');
      }
      setIsDeleteDialogOpen(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleCloseEditDialog = () => {
    setIsEditDialogOpen(false);
  };

  const handleCloseDeleteDialog = () => {
    setIsDeleteDialogOpen(false);
  };

  if (!partial) {
    return null;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton 
            onClick={() => router.push(`/versions/${params.version}/partials`)}
            color="primary"
            sx={{ mr: 1 }}
          >
            <ArrowBackIcon />
          </IconButton>
          <Box>
            <Typography variant="h4" component="h1">
              {partial.name}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
              {partial.description}
            </Typography>
          </Box>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            color="error"
            onClick={() => setIsDeleteDialogOpen(true)}
          >
            삭제
          </Button>
          <Button
            variant="contained"
            onClick={() => setIsEditDialogOpen(true)}
          >
            수정
          </Button>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            파셜 상세 정보
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            생성일: {new Date(partial.created_at).toLocaleString('ko-KR', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            수정일: {new Date(partial.updated_at).toLocaleString('ko-KR', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </Typography>
        </Paper>

        <Paper sx={{ p: 3, bgcolor: 'background.default' }}>
          <Typography variant="h6" gutterBottom>
            의존성
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {partial.dependencies?.length > 0 ? (
              partial.dependencies.map((dep) => (
                <Chip
                  key={dep}
                  label={dep}
                  variant="outlined"
                  color="primary"
                  onClick={() => router.push(`/versions/${params.version}/partials/${dep}`)}
                  sx={{ cursor: 'pointer' }}
                />
              ))
            ) : (
              <Typography variant="body2" color="text.secondary">
                의존성 없음
              </Typography>
            )}
          </Box>
        </Paper>

        <Paper>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab label="소스" />
            <Tab label="프리뷰" />
          </Tabs>
          <TabPanel value={tabValue} index={0}>
            <HtmlEditor
              value={partial.content}
              onChange={() => {}}
              readOnly
            />
          </TabPanel>
          <TabPanel value={tabValue} index={1}>
            <Box
              sx={{
                p: 2,
                minHeight: '500px',
                border: '1px solid #eee',
                borderRadius: 1,
                bgcolor: 'background.paper',
              }}
            >
              <div dangerouslySetInnerHTML={{ __html: partial.content }} />
            </Box>
          </TabPanel>
        </Paper>
      </Box>

      {/* 수정 다이얼로그 */}
      <Dialog
        open={isEditDialogOpen}
        onClose={handleCloseEditDialog}
        maxWidth="md"
        fullWidth
        keepMounted={false}
        disablePortal
        disableEnforceFocus
        disableAutoFocus
      >
        <DialogTitle>파셜 수정</DialogTitle>
        <DialogContent dividers>
          <Box sx={{ mt: 2 }}>
            <PartialEditor
              partial={partial}
              open={isEditDialogOpen}
              onOpenChange={setIsEditDialogOpen}
              onSubmit={handleEdit}
              version={params.version as string}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* 삭제 확인 다이얼로그 */}
      <Dialog
        open={isDeleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        keepMounted={false}
        disablePortal
        disableEnforceFocus
        disableAutoFocus
      >
        <DialogTitle>파셜 삭제</DialogTitle>
        <DialogContent>
          <Typography>
            정말로 이 파셜을 삭제하시겠습니까?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog}>
            취소
          </Button>
          <Button onClick={handleDelete} color="error">
            삭제
          </Button>
        </DialogActions>
      </Dialog>

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