'use client';

import React, { useState } from 'react';
import { Box, Paper, TextField, Button, Typography, Grid } from '@mui/material';
import { Preview as PreviewIcon } from '@mui/icons-material';

interface TemplateVariable {
  name: string;
  type: string;
  description: string;
}

interface TemplatePreviewProps {
  template: {
    content: string;
    variables: TemplateVariable[];
  };
}

export default function TemplatePreview({ template }: TemplatePreviewProps) {
  const [previewData, setPreviewData] = useState<Record<string, any>>({});
  const [previewResult, setPreviewResult] = useState<string>('');

  const handleVariableChange = (name: string, value: string) => {
    setPreviewData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePreview = async () => {
    try {
      const response = await fetch('/api/templates/preview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template: template.content,
          variables: previewData,
        }),
      });

      if (!response.ok) {
        throw new Error('템플릿 프리뷰 생성 실패');
      }

      const result = await response.text();
      setPreviewResult(result);
    } catch (error) {
      console.error('템플릿 프리뷰 에러:', error);
      setPreviewResult('템플릿 프리뷰 생성 중 오류가 발생했습니다.');
    }
  };

  return (
    <Box>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              변수 입력
            </Typography>
            {template.variables.map((variable) => (
              <TextField
                key={variable.name}
                fullWidth
                label={`${variable.name} (${variable.type})`}
                helperText={variable.description}
                value={previewData[variable.name] || ''}
                onChange={(e) => handleVariableChange(variable.name, e.target.value)}
                margin="normal"
              />
            ))}
            <Button
              variant="contained"
              startIcon={<PreviewIcon />}
              onClick={handlePreview}
              sx={{ mt: 2 }}
            >
              프리뷰
            </Button>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              프리뷰 결과
            </Typography>
            <Box
              sx={{
                p: 2,
                bgcolor: 'grey.100',
                borderRadius: 1,
                whiteSpace: 'pre-wrap',
                minHeight: '200px',
              }}
            >
              {previewResult || '변수를 입력하고 프리뷰 버튼을 클릭하세요.'}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
} 