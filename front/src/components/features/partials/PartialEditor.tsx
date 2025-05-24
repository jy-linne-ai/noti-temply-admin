import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
} from '@mui/material';
import { PartialTemplate } from '@/types/partial';
import { HtmlEditor } from '@/components/Editor';

interface PartialEditorProps {
  partial: PartialTemplate;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: { name: string; description: string; content: string }) => void;
  isNew?: boolean;
}

export function PartialEditor({ partial, open, onOpenChange, onSubmit, isNew = false }: PartialEditorProps) {
  const [formData, setFormData] = useState({
    name: partial.name,
    description: partial.description || '',
    content: partial.content || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Dialog open={open} onClose={() => onOpenChange(false)} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>{isNew ? '새 파셜 생성' : '파셜 수정'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="이름"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              disabled={!isNew}
              fullWidth
            />
            <TextField
              label="설명"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              fullWidth
              multiline
              rows={2}
            />
            <Box sx={{ mt: 2 }}>
              <HtmlEditor
                value={formData.content}
                onChange={(value) => setFormData({ ...formData, content: value })}
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => onOpenChange(false)}>취소</Button>
          <Button type="submit" variant="contained" color="primary">
            저장
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
} 