import { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  TextField,
  Stack,
} from '@mui/material';

interface Layout {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

interface LayoutFormProps {
  layout?: Layout;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: { name: string; description: string }) => void;
}

export function LayoutForm({
  layout,
  open,
  onOpenChange,
  onSubmit,
}: LayoutFormProps) {
  const [name, setName] = useState(layout?.name || "");
  const [description, setDescription] = useState(layout?.description || "");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ name, description });
  };

  return (
    <Dialog open={open} onClose={() => onOpenChange(false)} maxWidth="sm" fullWidth>
      <DialogTitle>
        {layout ? "레이아웃 수정" : "새 레이아웃"}
      </DialogTitle>
      <DialogContent>
        <DialogContentText sx={{ mb: 2 }}>
          {layout
            ? "레이아웃 정보를 수정합니다."
            : "새로운 레이아웃을 생성합니다."}
        </DialogContentText>
        <form onSubmit={handleSubmit}>
          <Stack spacing={3}>
            <TextField
              label="이름"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              fullWidth
            />
            <TextField
              label="설명"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
              fullWidth
              multiline
              rows={3}
            />
          </Stack>
          <DialogActions sx={{ mt: 2 }}>
            <Button onClick={() => onOpenChange(false)}>취소</Button>
            <Button type="submit" variant="contained">
              {layout ? "수정" : "생성"}
            </Button>
          </DialogActions>
        </form>
      </DialogContent>
    </Dialog>
  );
} 