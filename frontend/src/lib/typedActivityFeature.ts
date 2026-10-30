export function isTypedActivitiesEnabled(
  value: string | undefined = (
    import.meta.env as ImportMetaEnv & {
      readonly VITE_TYPED_ACTIVITIES_ENABLED?: string;
    }
  ).VITE_TYPED_ACTIVITIES_ENABLED,
): boolean {
  return value === "true";
}