import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from '@mui/material';
import { Layout } from "@/types/layout";

interface DeleteLayoutDialogProps {
  layout?: Layout;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
}

export function DeleteLayoutDialog({
  layout,
  open,
  onOpenChange,
  onConfirm,
}: DeleteLayoutDialogProps) {
  if (!layout) return null;

  return (
    <Dialog open={open} onClose={() => onOpenChange(false)}>
      <DialogTitle>레이아웃 삭제</DialogTitle>
      <DialogContent>
        <DialogContentText>
          정말로 "{layout.name}" 레이아웃을 삭제하시겠습니까?
          이 작업은 되돌릴 수 없습니다.
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => onOpenChange(false)}>취소</Button>
        <Button onClick={onConfirm} color="error" variant="contained">
          삭제
        </Button>
      </DialogActions>
    </Dialog>
  );
} 