'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import {
  Box,
  Button,
  Chip,
  Grid,
  List,
  ListItem,
  ListItemText,
  Paper,
  TextField,
  Typography,
} from '@mui/material';
import { useApi } from '@/lib/api';
import { Template } from '@/types/template';
import { useSnackbar } from 'notistack';

export default function TemplateDetailPage() {
  const params = useParams();
  const { enqueueSnackbar } = useSnackbar();
  const [template, setTemplate] = useState<Template | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState('');

  const api = useApi();

  const version = params.version as string;
  const templateName = params.template as string;
  const component = params.component as string;

  useEffect(() => {
    const fetchTemplate = async () => {
      try {
        const data = await api.getTemplate(version, templateName, component);
        setTemplate(data);
        setEditedContent(data.content);
      } catch (error) {
        enqueueSnackbar('템플릿을 불러오는데 실패했습니다.', { variant: 'error' });
      }
    };

    fetchTemplate();
  }, [version, templateName, component, enqueueSnackbar, api]);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedContent(template?.content || '');
  };

  const handleSave = async () => {
    if (!template) return;

    try {
      const updatedTemplate = await api.updateTemplate(version, templateName, component, {
        content: editedContent,
      });
      setTemplate(updatedTemplate);
      setIsEditing(false);
      enqueueSnackbar('템플릿이 성공적으로 수정되었습니다.', { variant: 'success' });
    } catch (error) {
      enqueueSnackbar('템플릿 수정에 실패했습니다.', { variant: 'error' });
    }
  };

  if (!template) {
    return <Typography>로딩 중...</Typography>;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Chip label={template.template} color="primary" />
              <Chip label={template.component} color="secondary" />
            </Box>

            <Typography variant="h6" gutterBottom>
              레이아웃
            </Typography>
            <Typography variant="body1" sx={{ mb: 3 }}>
              {template.layout}
            </Typography>

            <Typography variant="h6" gutterBottom>
              파셜 목록
            </Typography>
            <List>
              {template.partials.map((partial, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body1">{partial}</Typography>
                        {template.dependencies?.includes(partial) && (
                          <Chip
                            size="small"
                            label="의존성"
                            color="warning"
                            variant="outlined"
                            sx={{ ml: 1 }}
                          />
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>

            <Typography variant="h6" gutterBottom>
              내용
            </Typography>
            {isEditing ? (
              <Box sx={{ mb: 2 }}>
                <TextField
                  fullWidth
                  multiline
                  rows={10}
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  sx={{ mb: 2 }}
                />
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button variant="contained" color="primary" onClick={handleSave}>
                    저장
                  </Button>
                  <Button variant="outlined" onClick={handleCancel}>
                    취소
                  </Button>
                </Box>
              </Box>
            ) : (
              <Box sx={{ mb: 2 }}>
                <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                  {template.content}
                </pre>
                <Button variant="contained" color="primary" onClick={handleEdit}>
                  수정
                </Button>
              </Box>
            )}

            <Typography variant="h6" gutterBottom>
              메타 정보
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  생성일: {new Date(template.created_at).toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  생성자: {template.created_by}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  수정일: {new Date(template.updated_at).toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  수정자: {template.updated_by}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
} 