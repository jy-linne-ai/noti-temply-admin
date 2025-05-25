import React, { useState, useEffect } from 'react';
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
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Divider,
} from '@mui/material';
import { 
  Close as CloseIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { PartialTemplate } from '@/types/partial';
import { HtmlEditor } from '@/components/Editor';
import { useApi } from '@/lib/api';
import { formatDate } from '@/lib/utils';

interface PartialDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  selectedPartial: PartialTemplate | null;
  version: string;
  onPartialChange?: (partial: PartialTemplate) => void;
}

export function PartialDrawer({
  isOpen,
  onClose,
  selectedPartial,
  version,
  onPartialChange,
}: PartialDrawerProps) {
  const router = useRouter();
  const api = useApi();
  const [contentTab, setContentTab] = useState(0);
  const [childPartials, setChildPartials] = useState<PartialTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentPartial, setCurrentPartial] = useState<PartialTemplate | null>(null);

  // selectedPartial이 변경될 때마다 currentPartial 업데이트
  useEffect(() => {
    if (selectedPartial) {
      setCurrentPartial(selectedPartial);
    }
  }, [selectedPartial]);

  // 자식 파셜 목록 로드
  const loadChildPartials = async (partialName: string) => {
    try {
      setIsLoading(true);
      const children = await api.getPartialChildren(version, partialName);
      // 자기 자신을 제외한 파셜만 표시
      const filteredChildren = children.filter(child => child.name !== partialName);
      setChildPartials(filteredChildren);
    } catch (err) {
      console.error('Error loading child partials:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // 선택된 파셜이 변경될 때마다 자식 파셜 목록 로드
  useEffect(() => {
    if (currentPartial) {
      loadChildPartials(currentPartial.name);
    }
  }, [currentPartial?.name]);

  // 파셜 클릭 핸들러 (자식 파셜과 의존성 모두에서 사용)
  const handlePartialClick = async (partialName: string) => {
    try {
      setIsLoading(true);
      const updatedPartial = await api.getPartial(version, partialName);
      if (updatedPartial) {
        setCurrentPartial(updatedPartial);
        if (onPartialChange) {
          onPartialChange(updatedPartial);
        }
        await loadChildPartials(updatedPartial.name);
      }
    } catch (err) {
      console.error('Error loading partial:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen || !currentPartial) return null;

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
            {currentPartial.name}
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
                {currentPartial.description || '설명이 없습니다.'}
              </Typography>

              {/* 의존성 */}
              <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                의존성
              </Typography>
              <Box>
                {currentPartial.dependencies && currentPartial.dependencies.length > 0 ? (
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {currentPartial.dependencies.map(dep => (
                      <Chip
                        key={dep}
                        label={dep}
                        variant="outlined"
                        size="small"
                        color="warning"
                        onClick={() => handlePartialClick(dep)}
                        sx={{ cursor: 'pointer' }}
                      />
                    ))}
                  </Box>
                ) : (
                  <Typography color="text.secondary" variant="body2">의존성 없음</Typography>
                )}
              </Box>

              {/* 참조하는 파셜 */}
              <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                참조하는 파셜
              </Typography>
              <Box>
                {isLoading ? (
                  <Typography>로딩 중...</Typography>
                ) : childPartials.length > 0 ? (
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {childPartials.map(child => (
                      <Chip
                        key={child.name}
                        label={child.name}
                        variant="outlined"
                        size="small"
                        color="info"
                        onClick={() => handlePartialClick(child.name)}
                        sx={{ cursor: 'pointer' }}
                      />
                    ))}
                  </Box>
                ) : (
                  <Typography color="text.secondary" variant="body2">이 파셜을 참조하는 파셜이 없습니다.</Typography>
                )}
              </Box>

              {/* 생성/수정 정보 */}
              <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                생성
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Typography variant="body2">
                  {formatDate(currentPartial.created_at)}
                </Typography>
              </Box>

              <Typography variant="subtitle2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                수정
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Typography variant="body2">
                  {formatDate(currentPartial.updated_at)}
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
                  value={currentPartial.content}
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
                        ${currentPartial.content}
                      </body>
                    </html>
                  `}
                  style={{
                    width: '100%',
                    height: '100%',
                    border: 'none',
                  }}
                  title="파셜 프리뷰"
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
                router.push(`/versions/${version}/partials/${currentPartial.name}`);
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