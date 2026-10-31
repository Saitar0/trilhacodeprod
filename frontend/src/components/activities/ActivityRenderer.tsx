import type { PublishedActivity } from "@/types";
import { MultipleChoiceActivity } from "./MultipleChoiceActivity";

export function ActivityRenderer({
  activity,
  blockId,
  trackId,
}: {
  activity: PublishedActivity;
  blockId: string;
  trackId: string;
}) {
  if (activity.activity_schema_version !== 1) {
    return <p role="status" className="text-sm text-slate-400">Esta atividade usa uma versão que o aplicativo não reconhece.</p>;
  }
  return <MultipleChoiceActivity activity={activity} blockId={blockId} trackId={trackId} />;
}
