import * as Icons from "lucide-react";
import type { LucideIcon } from "lucide-react";

export function IconCatalog({ name, className }: { name?: string; className?: string }) {
  const Icon = ((name && (Icons as unknown as Record<string, LucideIcon>)[name]) || Icons.Square) as LucideIcon;
  return <Icon className={className} />;
}
