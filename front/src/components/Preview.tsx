import React from 'react';
import { Box, Typography } from '@mui/material';

interface PreviewProps {
  content: string;
  title?: string;
  type?: 'layout' | 'template' | 'partial';
}

const PREVIEW_STYLES = {
  layout: {
    body: {
      margin: '0',
      padding: '0',
      fontFamily: 'Arial, sans-serif',
      fontSize: '14px',
      lineHeight: '1.5',
      color: '#333',
    },
    container: {
      maxWidth: '100%',
      margin: '0 auto',
      padding: '20px',
    },
  },
  template: {
    body: {
      margin: '0',
      padding: '0',
      fontFamily: 'Arial, sans-serif',
      fontSize: '14px',
      lineHeight: '1.5',
      color: '#333',
    },
    container: {
      maxWidth: '100%',
      margin: '0 auto',
      padding: '20px',
    },
  },
  partial: {
    body: {
      margin: '0',
      padding: '0',
      fontFamily: 'Arial, sans-serif',
      fontSize: '14px',
      lineHeight: '1.5',
      color: '#333',
    },
    container: {
      maxWidth: '100%',
      margin: '0 auto',
      padding: '20px',
    },
  },
};

export function Preview({ content, title, type = 'template' }: PreviewProps) {
  const styles = PREVIEW_STYLES[type];

  return (
    // <Box sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
    //   {title && (
    //     <Typography variant="subtitle1" color="text.secondary" gutterBottom>
    //       {title}
    //     </Typography>
    //   )}
      <Box
        sx={{
          flex: 1,
          minHeight: 0,
          overflow: 'auto',
          bgcolor: 'background.paper',
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 1,
        }}
      >
        <Box
          sx={{
            ...styles.body,
            ...styles.container,
            height: '100%',
            overflow: 'auto',
          }}
          dangerouslySetInnerHTML={{ __html: content }}
        />
      </Box>
    // </Box>
  );
} 