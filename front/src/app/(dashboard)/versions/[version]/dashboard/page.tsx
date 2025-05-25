'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Box, Typography, Paper, Button, Stack, Dialog, DialogTitle, DialogContent, List, ListItem, ListItemButton, ListItemText, TextField } from '@mui/material';
import { useApi } from '@/lib/api';

export default function DashboardPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApi();
  const [versions, setVersions] = useState<string[]>([]);
  const [filteredVersions, setFilteredVersions] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isVersionDialogOpen, setIsVersionDialogOpen] = useState(false);

  useEffect(() => {
    fetchVersions();
  }, []);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredVersions(versions);
    } else {
      const filtered = versions.filter(version => 
        version.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredVersions(filtered);
    }
  }, [searchQuery, versions]);

  const fetchVersions = async () => {
    try {
      const versions = await api.getVersions();
      // Root 버전을 최상단에 표시하도록 정렬
      const sortedVersions = versions.sort((a, b) => {
        if (a.is_root && !b.is_root) return -1;
        if (!a.is_root && b.is_root) return 1;
        return 0;
      });
      const versionList = sortedVersions.map(v => v.version);
      setVersions(versionList);
      setFilteredVersions(versionList);
    } catch (error) {
      console.error('Failed to fetch versions:', error);
    }
  };

  const handleVersionSelect = async (version: string) => {
    try {
      // 버전 유효성 체크
      await api.getVersion(version);
      
      // 쿠키에 버전 저장
      document.cookie = `version=${version}; path=/`;
      
      // 버전별 대시보드로 이동
      router.push(`/versions/${version}/dashboard`);
      setIsVersionDialogOpen(false);
      setSearchQuery(''); // 검색어 초기화
    } catch (error) {
      console.error('Failed to select version:', error);
      alert('유효하지 않은 버전입니다.');
    }
  };

  const handleDialogClose = () => {
    setIsVersionDialogOpen(false);
    setSearchQuery(''); // 검색어 초기화
  };

  return (
    <Box sx={{ p: 3 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stack spacing={2}>
          <Typography variant="h5" gutterBottom>
            환영합니다
          </Typography>
          <Typography variant="body1">
            왼쪽 메뉴에서 원하는 기능을 선택하세요.
          </Typography>
          <Box>
            <Typography variant="body1" color="text.secondary" gutterBottom>
              현재 버전: {params.version}
            </Typography>
            <Stack direction="row" spacing={2}>
              <Button
                variant="outlined"
                onClick={() => setIsVersionDialogOpen(true)}
              >
                버전 변경
              </Button>
              <Button
                variant="contained"
                onClick={() => router.push('/versions')}
              >
                버전 관리
              </Button>
            </Stack>
          </Box>
        </Stack>
      </Paper>

      {/* 버전 선택 다이얼로그 */}
      <Dialog
        open={isVersionDialogOpen}
        onClose={handleDialogClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>버전 선택</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <TextField
              fullWidth
              size="small"
              placeholder="버전 검색..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              sx={{ mt: 1 }}
            />
          </Box>
          <List>
            {filteredVersions.map((version) => (
              <ListItem key={version} disablePadding>
                <ListItemButton 
                  onClick={() => handleVersionSelect(version)}
                  sx={{
                    backgroundColor: version === params.version ? 'action.selected' : 'transparent',
                    '&:hover': {
                      backgroundColor: version === params.version ? 'action.selected' : 'action.hover',
                    },
                  }}
                >
                  <ListItemText 
                    primary={version}
                    primaryTypographyProps={{
                      fontWeight: version === params.version ? 'bold' : 'normal',
                      color: version === params.version ? 'primary' : 'inherit',
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
            {filteredVersions.length === 0 && (
              <ListItem>
                <ListItemText primary="검색 결과가 없습니다." />
              </ListItem>
            )}
          </List>
        </DialogContent>
      </Dialog>
    </Box>
  );
} 