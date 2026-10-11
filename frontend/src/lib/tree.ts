import { ProgressStatus, TrackNode, TreeNode } from "@/types";

export function buildTree(nodes: TrackNode[]): TreeNode[] {
  const map = new Map<string, TreeNode>();
  nodes.forEach((n) => map.set(n.id, { ...n, children: [], level: 0 }));
  const roots: TreeNode[] = [];
  map.forEach((n) => {
    const parent = n.parent_id ? map.get(n.parent_id) : undefined;
    if (parent) parent.children.push(n);
    else if (!n.parent_id) roots.push(n);
  });
  const walk = (list: TreeNode[], level: number) => {
    list.sort((a, b) => a.order - b.order);
    list.forEach((n) => {
      n.level = level;
      walk(n.children, level + 1);
    });
  };
  walk(roots, 0);
  return roots;
}

export function flatten(tree: TreeNode[]): TreeNode[] {
  const out: TreeNode[] = [];
  const walk = (list: TreeNode[]): void => list.forEach((n) => { out.push(n); walk(n.children); });
  walk(tree);
  return out;
}

export function isLearnable(n: TreeNode, lastKind: string, blockCounts: Record<string, number>) {
  return n.children.length === 0 && (n.kind === lastKind || (blockCounts[n.id] || 0) > 0);
}

export function learnablesOf(n: TreeNode, lastKind: string, blockCounts: Record<string, number>): TreeNode[] {
  return flatten([n]).filter((x) => isLearnable(x, lastKind, blockCounts));
}

export function progressFor(items: TreeNode[], statuses: Record<string, { status: ProgressStatus }>) {
  const total = items.length;
  const completed = items.filter((i) => statuses[i.id]?.status === "completed").length;
  return { total, completed, pct: total ? Math.round((completed / total) * 100) : 0 };
}

export function filterTree(tree: TreeNode[], keep: (n: TreeNode) => boolean): TreeNode[] {
  return tree
    .map((n) => {
      const children = filterTree(n.children, keep);
      if (children.length || (n.children.length === 0 && keep(n))) return { ...n, children };
      return null;
    })
    .filter(Boolean) as TreeNode[];
}

export function findNode(tree: TreeNode[], id?: string | null): TreeNode | undefined {
  return id ? flatten(tree).find((n) => n.id === id) : undefined;
}
