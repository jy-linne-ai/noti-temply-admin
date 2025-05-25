import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Drawer,
  IconButton,
  Button,
  Stack,
  Tabs,
  Tab,
  Chip,
} from '@mui/material';
import { 
  Close as CloseIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { Layout } from '@/types/layout';
import { HtmlEditor } from '@/components/Editor';
import { formatDate } from '@/lib/utils';

interface LayoutDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  selectedLayout: Layout | null;
  version: string;
}

export function LayoutDrawer({
  isOpen,
  onClose,
  selectedLayout,
  version,
}: LayoutDrawerProps) {
  const router = useRouter();
  const [contentTab, setContentTab] = useState(0);

  if (!isOpen || !selectedLayout) return null;

  return (
    <Drawer
      anchor="right"
      open={isOpen}
      onClose={onClose}
      PaperProps={{
        sx: { width: '80%', maxWidth: '1200px' }
      }}
    >
      <Box sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" component="h2">
            {selectedLayout.name}
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'column', height: 'calc(100% - 80px)' }}>
          {/* 기본 정보 테이블 */}
          <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: 'grid', gridTemplateColumns: '100px 1fr', gap: 1 }}>
              {/* 설명 */}
              <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                설명
              </Typography>
              <Typography>
                {selectedLayout.description || '설명이 없습니다.'}
              </Typography>

              {/* 생성/수정 정보 */}
              <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                생성
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Typography variant="body2">
                  {selectedLayout ? formatDate(selectedLayout.created_at) : '-'}
                </Typography>
              </Box>

              <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                수정
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Typography variant="body2">
                  {selectedLayout ? formatDate(selectedLayout.updated_at) : '-'}
                </Typography>
              </Box>
            </Box>
          </Paper>

          {/* 컨텐츠 탭 */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs 
              value={contentTab}
              onChange={(_, newValue: number) => setContentTab(newValue)}
              aria-label="컨텐츠 탭"
            >
              <Tab label="소스" />
              <Tab label="프리뷰" />
            </Tabs>
          </Box>

          {contentTab === 0 && (
            <Box sx={{ flex: 1, overflow: 'hidden' }}>
              <Paper 
                variant="outlined" 
                sx={{ 
                  height: '100%',
                  overflow: 'hidden'
                }}
              >
                <HtmlEditor
                  value={selectedLayout.content}
                  onChange={() => {}}
                  readOnly
                />
              </Paper>
            </Box>
          )}

          {contentTab === 1 && (
            <Box sx={{ flex: 1, overflow: 'hidden' }}>
              <Paper 
                variant="outlined" 
                sx={{ 
                  height: '100%',
                  overflow: 'hidden',
                  bgcolor: 'white'
                }}
              >
                <iframe
                  srcDoc={`
                    <!DOCTYPE html>
                    <html>
                      <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <style>
                          body {
                            margin: 0;
                            padding: 16px;
                            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                            line-height: 1.5;
                            color: #333;
                          }
                          img {
                            max-width: 100%;
                            height: auto;
                          }
                          table {
                            border-collapse: collapse;
                            width: 100%;
                          }
                          th, td {
                            border: 1px solid #ddd;
                            padding: 8px;
                          }
                          th {
                            background-color: #f5f5f5;
                          }
                        </style>
                      </head>
                      <body>
                        ${selectedLayout.content}
                      </body>
                    </html>
                  `}
                  style={{
                    width: '100%',
                    height: '100%',
                    border: 'none',
                  }}
                  title="레이아웃 프리뷰"
                />
              </Paper>
            </Box>
          )}

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              onClick={() => {
                onClose();
                router.push(`/versions/${version}/layouts/${selectedLayout.name}`);
              }}
            >
              수정하기
            </Button>
          </Box>
        </Box>
      </Box>
    </Drawer>
  );
}
