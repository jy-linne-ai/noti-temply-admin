"use client";

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  Snackbar,
  Alert,
} from '@mui/material';
import { useApi } from '@/lib/api';
import { PartialTemplate } from '@/types/partial';
import { PartialEditor } from '@/components/partials/PartialEditor';

export default function NewPartialPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApi();
  const [error, setError] = useState<string | null>(null);

  const handleSave = async (partial: Partial<PartialTemplate>) => {
    try {
      const createdPartial = await api.createPartial(params.version as string, partial);
      router.push(`/versions/${params.version}/partials/${createdPartial.name}`);
    } catch (err) {
      console.error('Error creating partial:', err);
      setError('파셜 생성에 실패했습니다.');
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1">
          파셜 생성
        </Typography>
      </Box>

      <Paper sx={{ p: 3 }}>
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
          onSave={handleSave}
          onCancel={() => router.push(`/versions/${params.version}/partials`)}
        />
      </Paper>

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