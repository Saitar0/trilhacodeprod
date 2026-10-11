import React from "react";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription,
  AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "@/components/ui/alert-dialog";

export function ConfirmDialog({ open, onOpenChange, title, description, confirmLabel = "Confirmar", onConfirm }: {
  open: boolean; onOpenChange: (v: boolean) => void; title: string; description?: string;
  confirmLabel?: string; onConfirm: () => void;
}) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent data-testid="confirm-dialog" className="border-slate-800 bg-slate-900">
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          {description && <AlertDialogDescription>{description}</AlertDialogDescription>}
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel data-testid="confirm-dialog-cancel">Cancelar</AlertDialogCancel>
          <AlertDialogAction data-testid="confirm-dialog-confirm" onClick={onConfirm}
            className="bg-rose-600 text-white hover:bg-rose-500">{confirmLabel}</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
