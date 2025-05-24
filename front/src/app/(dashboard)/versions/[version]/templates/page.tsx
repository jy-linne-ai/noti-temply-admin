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
  Chip,
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
    router.push(`/versions/${params.version}/templates/${template.template}/comports/${template.component}`);
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
              <TableCell>템플릿</TableCell>
              <TableCell>컴포넌트</TableCell>
              <TableCell>레이아웃</TableCell>
              <TableCell>파셜</TableCell>
              <TableCell>내용</TableCell>
              <TableCell>생성일</TableCell>
              <TableCell>수정일</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {templates.map((template) => (
              <TableRow
                key={`${template.template}-${template.component}`}
                hover
                onClick={() => handleTemplateClick(template)}
                sx={{ cursor: 'pointer' }}
              >
                <TableCell>{template.template}</TableCell>
                <TableCell>{template.component}</TableCell>
                <TableCell>
                  {template.layout ? (
                    <Chip label={template.layout} size="small" color="primary" />
                  ) : (
                    '-'
                  )}
                </TableCell>
                <TableCell>
                  {template.partials && template.partials.length > 0 ? (
                    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {template.partials.map((partial) => (
                        <Chip key={partial} label={partial} size="small" />
                      ))}
                    </Box>
                  ) : (
                    '-'
                  )}
                </TableCell>
                <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {template.content}
                </TableCell>
                <TableCell>{template.created_at ? new Date(template.created_at).toLocaleDateString() : '-'}</TableCell>
                <TableCell>{template.updated_at ? new Date(template.updated_at).toLocaleDateString() : '-'}</TableCell>
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