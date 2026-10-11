import { useMemo } from "react";
import { Lock, ProgressRecord, Relation, Track, TreeNode, TreeResponse } from "@/types";
import { buildTree, flatten, isLearnable } from "@/lib/tree";

export interface ViewModel {
  track: Track;
  tree: TreeNode[];
  flat: TreeNode[];
  learnables: TreeNode[];
  byId: Map<string, TreeNode>;
  relations: Relation[];
  blockCounts: Record<string, number>;
  lastKind: string;
  statuses: Record<string, ProgressRecord>;
  locks: Record<string, Lock>;
  label: (kind: string) => string;
}

const NO_LOCKS: Record<string, Lock> = {};

export function useViewModel(data: TreeResponse | undefined, statuses: Record<string, ProgressRecord>, hideArchived: boolean,
  locks: Record<string, Lock> = NO_LOCKS) {
  return useMemo<ViewModel | null>(() => {
    if (!data) return null;
    const nodes = hideArchived ? data.nodes.filter((n) => n.status !== "archived") : data.nodes;
    const tree = buildTree(nodes);
    const flat = flatten(tree);
    const lastKind = data.track.hierarchy[data.track.hierarchy.length - 1];
    return {
      track: data.track, tree, flat, relations: data.relations, blockCounts: data.block_counts, lastKind, statuses, locks,
      learnables: flat.filter((n) => isLearnable(n, lastKind, data.block_counts)),
      byId: new Map(flat.map((n) => [n.id, n])),
      label: (k: string) => data.track.level_labels[k] || k,
    };
  }, [data, statuses, hideArchived, locks]);
}

export function nextLearnable(vm: ViewModel, afterId?: string) {
  const start = afterId ? vm.learnables.findIndex((n) => n.id === afterId) + 1 : 0;
  const open = (n: TreeNode) => vm.statuses[n.id]?.status !== "completed" && !vm.locks[n.id];
  return vm.learnables.slice(start).find(open) || vm.learnables.find(open);
}
