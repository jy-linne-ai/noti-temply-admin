'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Snackbar,
} from '@mui/material';
import { templateService } from '@/services/templateService';
import { Template } from '@/types/template';

export default function TemplatesPage() {
  const params = useParams();
  const router = useRouter();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTemplates();
  }, [params.version]);

  const fetchTemplates = async () => {
    try {
      const data = await templateService.getTemplates(params.version as string);
      setTemplates(data);
    } catch (err) {
      setError('템플릿 목록을 불러오는데 실패했습니다.');
    }
  };

  const handleTemplateClick = (template: Template) => {
    router.push(`/versions/${params.version}/templates/${template.name}`);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          템플릿 관리
        </Typography>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>이름</TableCell>
              <TableCell>설명</TableCell>
              <TableCell>레이아웃</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {templates.map((template) => (
              <TableRow
                key={template.name}
                hover
                onClick={() => handleTemplateClick(template)}
                sx={{ cursor: 'pointer' }}
              >
                <TableCell>{template.name}</TableCell>
                <TableCell>{template.description}</TableCell>
                <TableCell>{template.layout}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

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