"use client";

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  Snackbar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
} from '@mui/material';
import { useApi } from '@/lib/api';
import { PartialTemplate } from '@/types/partial';
import { PartialEditor } from '@/components/features/partials/PartialEditor';

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
    <Dialog
      open={true}
      onClose={() => router.push(`/versions/${params.version}/partials`)}
      maxWidth="md"
      fullWidth
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
          open={true}
          onOpenChange={(open) => {
            if (!open) router.push(`/versions/${params.version}/partials`);
          }}
          onSubmit={handleSave}
          version={params.version as string}
        />
      </DialogContent>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
    </Dialog>
  );
} 