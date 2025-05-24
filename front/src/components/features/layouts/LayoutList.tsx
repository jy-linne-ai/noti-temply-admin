import { Box, Typography, IconButton, Paper, Stack } from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { Layout } from "@/types/layout";

interface LayoutListProps {
  layouts: Layout[];
  onEdit: (layout: Layout) => void;
  onDelete: (layout: Layout) => void;
}

export function LayoutList({ layouts, onEdit, onDelete }: LayoutListProps) {
  if (layouts.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography color="text.secondary">레이아웃이 없습니다.</Typography>
      </Box>
    );
  }

  return (
    <Stack spacing={2}>
      {layouts.map((layout) => (
        <Paper
          key={layout.id}
          sx={{
            p: 2,
            '&:hover': {
              bgcolor: 'action.hover',
            },
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h6">{layout.name}</Typography>
              <Typography color="text.secondary">{layout.description}</Typography>
            </Box>
            <Box>
              <IconButton onClick={() => onEdit(layout)} size="small">
                <EditIcon />
              </IconButton>
              <IconButton onClick={() => onDelete(layout)} size="small" color="error">
                <DeleteIcon />
              </IconButton>
            </Box>
          </Box>
        </Paper>
      ))}
    </Stack>
  );
} 