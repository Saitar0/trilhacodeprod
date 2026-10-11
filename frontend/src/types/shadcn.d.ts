declare module "@/components/ui/button" {
  import * as React from "react";
  export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
    size?: "default" | "sm" | "lg" | "icon";
    asChild?: boolean;
  }
  export const Button: React.ForwardRefExoticComponent<ButtonProps & React.RefAttributes<HTMLButtonElement>>;
}

declare module "@/components/ui/input" {
  import * as React from "react";
  export const Input: React.ForwardRefExoticComponent<React.InputHTMLAttributes<HTMLInputElement> & React.RefAttributes<HTMLInputElement>>;
}

declare module "@/components/ui/textarea" {
  import * as React from "react";
  export const Textarea: React.ForwardRefExoticComponent<React.TextareaHTMLAttributes<HTMLTextAreaElement> & React.RefAttributes<HTMLTextAreaElement>>;
}

declare module "@/components/ui/label" {
  import * as L from "@radix-ui/react-label";
  export const Label: typeof L.Root;
}

declare module "@/components/ui/switch" {
  import * as S from "@radix-ui/react-switch";
  export const Switch: typeof S.Root;
}

declare module "@/components/ui/checkbox" {
  import * as C from "@radix-ui/react-checkbox";
  export const Checkbox: typeof C.Root;
}

declare module "@/components/ui/select" {
  import * as S from "@radix-ui/react-select";
  export const Select: typeof S.Root;
  export const SelectTrigger: typeof S.Trigger;
  export const SelectValue: typeof S.Value;
  export const SelectContent: typeof S.Content;
  export const SelectItem: typeof S.Item;
}

declare module "@/components/ui/tabs" {
  import * as T from "@radix-ui/react-tabs";
  export const Tabs: typeof T.Root;
  export const TabsList: typeof T.List;
  export const TabsTrigger: typeof T.Trigger;
  export const TabsContent: typeof T.Content;
}

declare module "@/components/ui/dialog" {
  import * as React from "react";
  import * as D from "@radix-ui/react-dialog";
  export const Dialog: typeof D.Root;
  export const DialogContent: typeof D.Content;
  export const DialogTitle: typeof D.Title;
  export const DialogDescription: typeof D.Description;
  export const DialogHeader: React.FC<React.HTMLAttributes<HTMLDivElement>>;
  export const DialogFooter: React.FC<React.HTMLAttributes<HTMLDivElement>>;
}

declare module "@/components/ui/alert-dialog" {
  import * as React from "react";
  import * as A from "@radix-ui/react-alert-dialog";
  export const AlertDialog: typeof A.Root;
  export const AlertDialogContent: typeof A.Content;
  export const AlertDialogTitle: typeof A.Title;
  export const AlertDialogDescription: typeof A.Description;
  export const AlertDialogAction: typeof A.Action;
  export const AlertDialogCancel: typeof A.Cancel;
  export const AlertDialogHeader: React.FC<React.HTMLAttributes<HTMLDivElement>>;
  export const AlertDialogFooter: React.FC<React.HTMLAttributes<HTMLDivElement>>;
}

declare module "@/components/ui/sheet" {
  import * as React from "react";
  import * as D from "@radix-ui/react-dialog";
  export const Sheet: typeof D.Root;
  export const SheetContent: React.ForwardRefExoticComponent<D.DialogContentProps & { side?: "top" | "bottom" | "left" | "right" } & React.RefAttributes<HTMLDivElement>>;
  export const SheetTitle: typeof D.Title;
  export const SheetDescription: typeof D.Description;
  export const SheetHeader: React.FC<React.HTMLAttributes<HTMLDivElement>>;
}

declare module "@/components/ui/dropdown-menu" {
  import * as M from "@radix-ui/react-dropdown-menu";
  export const DropdownMenu: typeof M.Root;
  export const DropdownMenuTrigger: typeof M.Trigger;
  export const DropdownMenuContent: typeof M.Content;
  export const DropdownMenuItem: typeof M.Item;
  export const DropdownMenuLabel: typeof M.Label;
  export const DropdownMenuSeparator: typeof M.Separator;
}
