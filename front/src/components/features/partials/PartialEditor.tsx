import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Stack,
  Typography,
  Chip,
  Autocomplete,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { PartialTemplate } from '@/types/partial';
import { HtmlEditor } from '@/components/Editor';
import { useApi } from '@/lib/api';

interface PartialEditorProps {
  partial: PartialTemplate;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: { name: string; description: string; content: string; dependencies: string[] }) => void;
  isNew?: boolean;
  version: string;
}

export function PartialEditor({ partial, open, onOpenChange, onSubmit, isNew = false, version }: PartialEditorProps) {
  const api = useApi();
  const [formData, setFormData] = useState({
    name: partial.name,
    description: partial.description || '',
    content: partial.content || '',
    dependencies: partial.dependencies || [],
  });
  const [availablePartials, setAvailablePartials] = useState<string[]>([]);
  const [selectedPartial, setSelectedPartial] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      fetchAvailablePartials();
    }
  }, [open, version]);

  const fetchAvailablePartials = async () => {
    try {
      const data = await api.getAllPartials(version);
      const available = data
        .map(p => p.name)
        .filter(name => name !== partial?.name && !formData.dependencies?.includes(name));
      setAvailablePartials(available);
    } catch (err) {
      console.error('Error fetching available partials:', err);
    }
  };

  const handleAddDependency = () => {
    if (!selectedPartial) return;
    setFormData({
      ...formData,
      dependencies: [...formData.dependencies, selectedPartial],
    });
    setSelectedPartial(null);
  };

  const handleRemoveDependency = (dependency: string) => {
    setFormData({
      ...formData,
      dependencies: formData.dependencies.filter(d => d !== dependency),
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <Dialog open={open} onClose={() => onOpenChange(false)} maxWidth="md" fullWidth>
      <form onSubmit={handleSubmit}>
        <DialogTitle>{isNew ? '새 파셜 생성' : '파셜 수정'}</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2 }}>
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

            <Box>
              <Typography variant="subtitle1" gutterBottom>
                의존성
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <Autocomplete
                  options={availablePartials}
                  value={selectedPartial}
                  onChange={(_, newValue) => setSelectedPartial(newValue)}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="의존성 추가"
                      variant="outlined"
                      size="small"
                      sx={{ minWidth: 200 }}
                    />
                  )}
                />
                <Button
                  variant="contained"
                  onClick={handleAddDependency}
                  disabled={!selectedPartial}
                >
                  추가
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {formData.dependencies.map((dependency) => (
                  <Chip
                    key={dependency}
                    label={dependency}
                    onDelete={() => handleRemoveDependency(dependency)}
                    deleteIcon={<CloseIcon />}
                  />
                ))}
              </Box>
            </Box>

            <Box>
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
          </Stack>
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