import { DynamicIcon, iconNames } from "lucide-react/dynamic";
import { Square } from "lucide-react";

const ICON_NAMES_BY_COMPONENT_NAME = new Map(
  iconNames.map((iconName) => [
    iconName
      .split("-")
      .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
      .join(""),
    iconName,
  ]),
);
export function IconCatalog({ name, className }: { name?: string; className?: string }) {
  const iconName = name ? ICON_NAMES_BY_COMPONENT_NAME.get(name) : undefined;

  if (!iconName) {
    return <Square className={className} data-icon="Square" />;
  }

  const LoadingIcon = () => <Square className={className} data-icon={name} />;

  return (
    <DynamicIcon
      name={iconName}
      fallback={LoadingIcon}
      className={className}
      data-icon={name}
    />
  );
}
