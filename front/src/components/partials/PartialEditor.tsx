import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Stack,
  Typography,
  Chip,
  IconButton,
  Autocomplete,
} from '@mui/material';
import { Add as AddIcon, Close as CloseIcon } from '@mui/icons-material';
import { PartialTemplate } from '@/types/partial';
import { CodeEditor } from '@/components/CodeEditor';
import { useApi } from '@/lib/api';

interface PartialEditorProps {
  isNew?: boolean;
  partial?: PartialTemplate;
  version: string;
  onSave: (partial: Partial<PartialTemplate>) => Promise<void>;
  onCancel: () => void;
}

export function PartialEditor({ isNew = false, partial, version, onSave, onCancel }: PartialEditorProps) {
  const api = useApi();
  const [name, setName] = useState(partial?.name || '');
  const [description, setDescription] = useState(partial?.description || '');
  const [content, setContent] = useState(partial?.content || '');
  const [dependencies, setDependencies] = useState<string[]>(partial?.dependencies || []);
  const [newDependency, setNewDependency] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [availablePartials, setAvailablePartials] = useState<string[]>([]);
  const [selectedPartial, setSelectedPartial] = useState<string | null>(null);

  useEffect(() => {
    if (partial) {
      setName(partial.name || '');
      setDescription(partial.description || '');
      setContent(partial.content || '');
      setDependencies(partial.dependencies || []);
    }
    fetchAvailablePartials();
  }, [partial, version]);

  const fetchAvailablePartials = async () => {
    try {
      const data = await api.getAllPartials(version);
      // 현재 파셜과 이미 의존성으로 추가된 파셜을 제외한 목록을 만듭니다
      const available = data
        .map(p => p.name)
        .filter(name => name !== partial?.name && !dependencies?.includes(name));
      setAvailablePartials(available);
    } catch (err) {
      console.error('Error fetching available partials:', err);
    }
  };

  const handleAddDependency = () => {
    if (!selectedPartial) return;

    setDependencies([...dependencies, selectedPartial]);
    setSelectedPartial(null);
  };

  const handleRemoveDependency = (dependency: string) => {
    setDependencies(dependencies.filter(d => d !== dependency));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !content) return;

    setIsSaving(true);
    try {
      const partialData: Partial<PartialTemplate> = {
        name,
        description,
        content,
        dependencies,
      };
      await onSave(partialData);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Stack spacing={3}>
        <TextField
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              이름
              <Typography component="span" color="error" sx={{ ml: 0.5 }}>
                *
              </Typography>
            </Box>
          }
          value={name}
          onChange={(e) => setName(e.target.value)}
          disabled={!isNew}
          fullWidth
        />

        <TextField
          label="설명"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
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
            {dependencies.map((dependency) => (
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
          <CodeEditor
            value={content}
            onChange={setContent}
            language="html"
            height="400px"
          />
        </Box>

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            onClick={onCancel}
            disabled={isSaving}
          >
            취소
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={!name.trim() || !content.trim() || isSaving}
          >
            {isSaving ? '저장 중...' : '저장'}
          </Button>
        </Box>
      </Stack>
    </Box>
  );
} 