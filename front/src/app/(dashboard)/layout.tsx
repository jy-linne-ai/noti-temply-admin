'use client';

import React, { useState, useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery,
  Chip,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  ViewModule as ViewModuleIcon,
  Description as DescriptionIcon,
  Code as CodeIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { useApi } from '@/lib/api';

const drawerWidth = 240;

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isCheckingVersion, setIsCheckingVersion] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'info' | 'warning' | 'error' }>({
    open: false,
    message: '',
    severity: 'info'
  });
  const pathname = usePathname();
  const router = useRouter();
  const api = useApi();

  const version = pathname.split('/')[2];
  const isVersionPage = pathname === '/versions';

  useEffect(() => {
    if (isVersionPage) {
      return;
    }
    if (isCheckingVersion) {
      return;
    }
    const loaded_version = localStorage.getItem('version');
    if (loaded_version !== version) {
      setIsCheckingVersion(true);
      const checkVersion = async () => {
        try {
          const versions = await api.getVersions();
          if (versions.length > 0 && versions.find((v) => v.version === version)) {
            localStorage.setItem('version', version);
            setIsCheckingVersion(false);
            return;
          }
            setSnackbar({
              open: true,
              message: '유효하지 않은 버전입니다. 버전을 선택해주세요.',
              severity: 'warning'
            });
            setTimeout(() => {
              router.push('/versions');
            }, 2000);
        } catch (error) {
          console.error('Error checking version:', error);
          setIsCheckingVersion(false);
        }
      };
      checkVersion();
    }
  }, [version, router, isVersionPage, api, isCheckingVersion]);

  
  const menuItems = isVersionPage ? [
    { text: '버전 관리', icon: <CodeIcon />, path: '/versions' },
  ] : version ? [
    { text: '대시보드', icon: <DashboardIcon />, path: `/versions/${version}/dashboard` },
    { text: '레이아웃', icon: <ViewModuleIcon />, path: `/versions/${version}/layouts` },
    { text: '파셜', icon: <CodeIcon />, path: `/versions/${version}/partials` },
    { text: '템플릿', icon: <DescriptionIcon />, path: `/versions/${version}/templates` },
    { text: '프리뷰', icon: <VisibilityIcon />, path: `/versions/${version}/preview` },
  ] : [];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenuClick = (path: string) => {
    router.push(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const handleVersionClick = () => {
    router.push('/versions');
  };

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Noti Temply Admin
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={pathname === item.path}
              onClick={() => handleMenuClick(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  );

  return (
    <>
      <Box sx={{ display: 'flex' }}>
          <AppBar
            position="fixed"
            sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
            }}
          >
            <Toolbar>
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
              >
                <MenuIcon />
              </IconButton>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {version && !isVersionPage && (
                  <Chip
                label={
                  <Box component="span" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Box component="span" sx={{ fontSize: '0.9rem' }}>Version:</Box>
                    <Box 
                      component="span" 
                    sx={{
                        color: '#FFD700',
                        fontWeight: 'bold',
                      fontSize: '1.1rem',
                        textShadow: '0 0 2px rgba(0,0,0,0.3)',
                        letterSpacing: '0.5px'
                      }}
                    >
                      {version}
                    </Box>
                  </Box>
                }
                color="primary"
                size="small"
                onClick={handleVersionClick}
                    sx={{
                  backgroundColor: theme.palette.primary.main,
                  color: theme.palette.primary.contrastText,
                  fontWeight: 'bold',
                  padding: '0 12px',
                      height: '32px',
                      '&:hover': {
                    backgroundColor: theme.palette.primary.dark,
                  },
                  cursor: 'pointer',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                  transition: 'all 0.2s ease-in-out',
                  '&:active': {
                    transform: 'scale(0.95)',
                      },
                    }}
                  />
                )}
                <Typography variant="h6" noWrap component="div">
              {menuItems.find((item) => item.path === pathname)?.text || 'Noti Temply Admin'}
                </Typography>
              </Box>
            </Toolbar>
          </AppBar>

      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
          <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
            disableEnforceFocus: true,
            disableAutoFocus: true,
            disableRestoreFocus: true,
          }}
            sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              },
            }}
          >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
              sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
          open
        >
          {drawer}
          </Drawer>
      </Box>

          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
              mt: '64px',
            }}
          >
            {children}
          </Box>
        </Box>
        
        <Snackbar
          open={snackbar.open}
          autoHideDuration={3000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        >
          <Alert 
            onClose={() => setSnackbar({ ...snackbar, open: false })} 
            severity={snackbar.severity}
            sx={{ width: '100%' }}
          >
            {snackbar.message}
          </Alert>
        </Snackbar>
      </>
  );
}
