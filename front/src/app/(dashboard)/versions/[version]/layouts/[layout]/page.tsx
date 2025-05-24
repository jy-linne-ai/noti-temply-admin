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
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { Layout } from '@/types/layout';
import { LayoutEditor } from '@/components/features/layouts/LayoutEditor';
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

export default function LayoutDetailPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApi();
  const [layout, setLayout] = useState<Layout | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    fetchData();
  }, [params.version, params.layout]);

    const fetchData = async () => {
    try {
      const layoutData = await api.getLayout(params.version as string, params.layout as string);
      setLayout(layoutData);
    } catch (err) {
      console.error('Error fetching layout:', err);
      setError('레이아웃 정보를 불러오는데 실패했습니다.');
    }
  };

  const handleEdit = async (data: { name: string; description: string; content: string }) => {
    try {
      const updatedLayout = await api.updateLayout(
        params.version as string,
        params.layout as string,
        {
          description: data.description,
          content: data.content,
        }
      );
      setLayout(updatedLayout);
      setIsEditDialogOpen(false);
      setError(null);
    } catch (err) {
      console.error('Error updating layout:', err);
      setError('레이아웃 수정에 실패했습니다.');
    }
  };

  const handleDelete = async () => {
    try {
      await api.deleteLayout(params.version as string, params.layout as string);
      setIsDeleteDialogOpen(false);
      setError(null);
      setTimeout(() => {
        router.push(`/versions/${params.version}/layouts`);
      }, 100);
    } catch (err: any) {
      console.error('Error deleting layout:', err);
      if (err.response?.status === 404) {
        setError('레이아웃이 이미 삭제되었습니다.');
        setTimeout(() => {
          router.push(`/versions/${params.version}/layouts`);
        }, 1000);
      } else {
        setError('레이아웃 삭제에 실패했습니다.');
        }
      setIsDeleteDialogOpen(false);
      }
    };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (!layout) {
    return null;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton 
            onClick={() => router.push(`/versions/${params.version}/layouts`)}
            color="primary"
            sx={{ mr: 1 }}
          >
            <ArrowBackIcon />
          </IconButton>
          <Box>
            <Typography variant="h4" component="h1">
              {params.layout}
      </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
        {layout.description}
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
        <Box>
          <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
              레이아웃 상세 정보
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              생성일: {new Date(layout.created_at).toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              수정일: {new Date(layout.updated_at).toLocaleString()}
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                컨텐츠
        </Typography>
              <Box sx={{ border: '1px solid #ccc', borderRadius: 1 }}>
                <Tabs value={tabValue} onChange={handleTabChange}>
                  <Tab label="소스" />
                  <Tab label="프리뷰" />
                </Tabs>
                <TabPanel value={tabValue} index={0}>
                  <HtmlEditor
                    value={layout.content}
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
                    <div
                      dangerouslySetInnerHTML={{ __html: layout.content }}
                      style={{
                        width: '100%',
                        minHeight: '500px',
                        backgroundColor: 'white'
                      }}
                    />
                  </Box>
                </TabPanel>
              </Box>
            </Box>
          </Paper>
        </Box>
      </Box>

      {/* 수정 다이얼로그 */}
      <LayoutEditor
        layout={layout}
        open={isEditDialogOpen}
        onOpenChange={setIsEditDialogOpen}
        onSubmit={handleEdit}
      />

      {/* 삭제 확인 다이얼로그 */}
      <Dialog 
        open={isDeleteDialogOpen} 
        onClose={() => setIsDeleteDialogOpen(false)}
        aria-labelledby="delete-dialog-title"
      >
        <DialogTitle id="delete-dialog-title">레이아웃 삭제</DialogTitle>
        <DialogContent>
          <Typography>
            정말로 이 레이아웃을 삭제하시겠습니까?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteDialogOpen(false)}>취소</Button>
          <Button 
            onClick={handleDelete} 
            variant="contained" 
            color="error"
          >
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