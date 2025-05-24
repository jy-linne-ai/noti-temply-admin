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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { PartialTemplate } from '@/types/partial';
import { PartialEditor } from '@/components/features/partials/PartialEditor';

export default function PartialPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApi();
  const [partial, setPartial] = useState<PartialTemplate | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  useEffect(() => {
    fetchData();
  }, [params.version, params.layout, params.partial]);

  const fetchData = async () => {
    try {
      const data = await api.getPartial(
        params.version as string,
        params.layout as string,
        params.partial as string
      );
      setPartial(data);
    } catch (err) {
      console.error('Error fetching partial:', err);
      setError('파셜을 불러오는데 실패했습니다.');
    }
  };

  const handleUpdate = async (data: { name: string; description: string; content: string }) => {
    try {
      await api.updatePartial(
        params.version as string,
        params.layout as string,
        params.partial as string,
        data
      );
      setIsEditDialogOpen(false);
      fetchData();
    } catch (err) {
      console.error('Error updating partial:', err);
      setError('파셜 수정에 실패했습니다.');
    }
  };

  const handleDelete = async () => {
    try {
      await api.deletePartial(
        params.version as string,
        params.layout as string,
        params.partial as string
      );
      router.push(`/versions/${params.version}/layouts/${params.layout}/partials`);
    } catch (err) {
      console.error('Error deleting partial:', err);
      setError('파셜 삭제에 실패했습니다.');
    }
  };

  if (!partial) {
    return null;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => router.push(`/versions/${params.version}/layouts/${params.layout}/partials`)}
          >
            목록으로
          </Button>
          <Box>
            <Typography variant="h4" component="h1">
              {partial.name}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
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

      <Paper sx={{ p: 3 }}>
        <Box
          sx={{
            '& img': { maxWidth: '100%' },
            '& table': { borderCollapse: 'collapse', width: '100%' },
            '& th, & td': { border: '1px solid #ddd', padding: '8px' },
            '& th': { backgroundColor: '#f5f5f5' },
          }}
          dangerouslySetInnerHTML={{ __html: partial.content }}
        />
      </Paper>

      {/* 수정 다이얼로그 */}
      <PartialEditor
        partial={partial}
        open={isEditDialogOpen}
        onOpenChange={setIsEditDialogOpen}
        onSubmit={handleUpdate}
      />

      {/* 삭제 확인 다이얼로그 */}
      <Dialog open={isDeleteDialogOpen} onClose={() => setIsDeleteDialogOpen(false)}>
        <DialogTitle>파셜 삭제</DialogTitle>
        <DialogContent>
          <DialogContentText>
            정말로 "{partial.name}" 파셜을 삭제하시겠습니까?
            이 작업은 되돌릴 수 없습니다.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteDialogOpen(false)}>취소</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
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