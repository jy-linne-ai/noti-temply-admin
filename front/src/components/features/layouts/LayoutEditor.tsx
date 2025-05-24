import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
} from '@mui/material';
import { Layout } from '@/types/layout';
import { HtmlEditor } from '@/components/Editor';

interface LayoutEditorProps {
  layout: Layout;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: { name: string; description: string; content: string }) => void;
  isNew?: boolean;
}

export function LayoutEditor({ layout, open, onOpenChange, onSubmit, isNew = false }: LayoutEditorProps) {
  const [formData, setFormData] = useState({
    name: layout.name,
    description: layout.description || '',
    content: layout.content || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Dialog open={open} onClose={() => onOpenChange(false)} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>{isNew ? '새 레이아웃 생성' : '레이아웃 수정'}</DialogTitle>
      <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  이름
                  <Typography component="span" color="error" sx={{ ml: 0.5 }}>
                    *
                  </Typography>
                </Box>
              }
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
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                <Typography variant="subtitle1">내용</Typography>
                <Typography component="span" color="error">
                  *
                </Typography>
              </Box>
              <HtmlEditor
                value={formData.content}
                onChange={(value) => setFormData({ ...formData, content: value })}
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
            <Button onClick={() => onOpenChange(false)}>취소</Button>
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={!formData.name.trim() || !formData.content.trim()}
          >
            저장
            </Button>
          </DialogActions>
        </form>
    </Dialog>
  );
} 