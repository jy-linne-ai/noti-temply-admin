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
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useApi } from '@/lib/api';
import { PartialTemplate } from '@/types/partial';
import { PartialEditor } from '@/components/partials/PartialEditor';

export default function PartialsPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApi();
  const [partials, setPartials] = useState<PartialTemplate[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  useEffect(() => {
    fetchPartials();
  }, [params.version]);

  const fetchPartials = async () => {
    try {
      const data = await api.getPartials(params.version as string);
      setPartials(data);
    } catch (err) {
      console.error('Error fetching partials:', err);
      setError('파셜 목록을 불러오는데 실패했습니다.');
    }
  };

  const handleCreate = async (partial: Partial<PartialTemplate>) => {
    try {
      const createdPartial = await api.createPartial(params.version as string, partial);
      setIsCreateDialogOpen(false);
      fetchPartials();
      router.push(`/versions/${params.version}/partials/${createdPartial.name}`);
    } catch (err) {
      console.error('Error creating partial:', err);
      setError('파셜 생성에 실패했습니다.');
    }
  };

  const handleCloseDialog = () => {
    setIsCreateDialogOpen(false);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          파셜 목록
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setIsCreateDialogOpen(true)}
        >
          파셜 추가
        </Button>
      </Box>

      <Stack spacing={2}>
        {partials.map((partial) => (
          <Paper
            key={partial.name}
            onClick={() => router.push(`/versions/${params.version}/partials/${partial.name}`)}
            sx={{
              p: 2,
              cursor: 'pointer',
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                bgcolor: 'action.hover',
                transform: 'translateY(-2px)',
                boxShadow: (theme) => theme.shadows[4],
              },
            }}
          >
            <Box>
              <Typography variant="h6">{partial.name}</Typography>
              <Typography variant="body2" color="text.secondary">
                {partial.description}
              </Typography>
            </Box>
          </Paper>
        ))}
      </Stack>

      {/* 생성 다이얼로그 */}
      <Dialog
        open={isCreateDialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
        keepMounted={false}
        disablePortal
        disableEnforceFocus
        disableAutoFocus
      >
        <DialogTitle>파셜 생성</DialogTitle>
        <DialogContent dividers>
          <PartialEditor
            isNew={true}
            partial={{
              id: '',
              name: '',
              description: '',
              content: '',
              dependencies: [],
              version: params.version as string,
              layout: '',
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            }}
            onSave={handleCreate}
            onCancel={handleCloseDialog}
          />
        </DialogContent>
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