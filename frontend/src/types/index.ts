export type Role = "admin" | "editor" | "student";
export type EditorialStatus = "draft" | "published" | "archived";
export type ProgressStatus = "not_started" | "in_progress" | "completed";

export interface User {
  id: string;
  email: string;
  name: string;
  role: Role;
  permissions: string[];
  profile?: { bio?: string; goals?: string; preferences?: Record<string, unknown> };
  created_at?: string;
}

export interface Track {
  id: string;
  title: string;
  slug: string;
  subtitle: string;
  description: string;
  cover_url: string;
  status: EditorialStatus;
  visibility: "public" | "private";
  audience: string[];
  difficulty: string;
  tag_ids: string[];
  hierarchy: string[];
  level_labels: Record<string, string>;
  settings: { enforce_prerequisites?: boolean; unlock_strategy?: string; visual_style?: string };
  version: number;
  order: number;
  derived_from?: string | null;
  published_at?: string | null;
  updated_at?: string;
  counts?: Record<string, number>;
}

export interface TrackNode {
  id: string;
  track_id: string;
  parent_id: string | null;
  kind: string;
  title: string;
  summary: string;
  description: string;
  notes: string;
  guidance: string;
  pedagogical_type: string;
  requirement: string;
  depth: string;
  status: EditorialStatus;
  estimated_minutes: number;
  tag_ids: string[];
  order: number;
  release?: { available_from?: string };
  updated_at?: string;
  meta?: Record<string, unknown>;
}

export interface TreeNode extends TrackNode {
  children: TreeNode[];
  level: number;
}

export interface Relation {
  id: string;
  track_id: string;
  node_id: string;
  target_id: string;
  type: string;
  enforced: boolean;
  note: string;
  direction?: "outgoing" | "incoming";
  other?: { id: string; title: string; kind: string };
}

export interface ContentBlock {
  id: string;
  node_id: string;
  type: string;
  title: string;
  data: Record<string, any>;
  status: EditorialStatus;
  order: number;
  activity?: PublishedActivity;
}

export interface PublishedActivity {
  activity_id: string;
  activity_schema_version: number;
  published_version_id: string;
  activity_revision: number;
  prompt: string;
  options: { id: string; label: string }[];
  completion_policy: "responded";
  max_attempts: number;
  evaluator_version: string;
}

export interface ActivityAttempt {
  id: string;
  user_id: string;
  track_id: string;
  node_id: string;
  activity_id: string;
  published_version_id: string;
  activity_revision: number;
  attempt_number: number;
  state: "draft" | "submitted" | "evaluated";
  response: { selected_option_id: string | null } | null;
  revision: number;
  result: { is_correct: boolean; score: number; evaluator_version: string } | null;
  feedback: string | null;
  projection_status: "pending" | "complete";
  created_at: string;
  updated_at: string;
  submitted_at?: string | null;
  evaluated_at?: string | null;
  activity: PublishedActivity;
}

export interface ActivityAttemptList {
  items: ActivityAttempt[];
  limit: number;
  skip: number;
  total: number;
}

export type FieldType = "text" | "textarea" | "markdown" | "code" | "url" | "number" | "select" | "list" | "boolean";

export interface BlockField {
  name: string;
  label: string;
  type: FieldType;
  options?: string[];
}

export interface BlockType {
  id: string;
  key: string;
  label: string;
  category: string;
  icon: string;
  description: string;
  fields: BlockField[];
  capabilities?: string[];
  enabled: boolean;
}

export interface TaxonomyItem {
  id: string;
  group: string;
  key: string;
  label: string;
  description: string;
  color: string;
  order: number;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
  color: string;
}

export interface Meta {
  taxonomies: Record<string, TaxonomyItem[]>;
  block_types: BlockType[];
  tags: Tag[];
  statuses: EditorialStatus[];
  progress_statuses: ProgressStatus[];
  roles: Role[];
  default_hierarchy: string[];
  default_labels: Record<string, string>;
}

export interface TreeResponse {
  track: Track;
  nodes: TrackNode[];
  relations: Relation[];
  block_counts: Record<string, number>;
}

export interface NodeDetail {
  node: TrackNode;
  blocks: ContentBlock[];
  relations: Relation[];
  ancestors: { id: string; title: string; kind: string }[];
  lock: Lock | null;
}

export interface ProgressRecord {
  node_id: string;
  block_id: string | null;
  status: ProgressStatus;
  revision?: number;
  attempts?: number;
  started_at?: string | null;
  completed_at?: string | null;
  updated_at?: string;
  data?: Record<string, any>;
}

export interface TrackProgress {
  nodes: Record<string, ProgressRecord>;
  blocks: Record<string, ProgressRecord>;
  state: { last_node_id?: string; last_node_title?: string; last_at?: string } | null;
  locks: Record<string, Lock>;
}

export interface HistoryItem {
  id: string;
  entity: string;
  entity_id: string;
  action: string;
  summary: string;
  user_name: string;
  at: string;
}

export interface TrackVersion {
  id: string;
  version: number;
  snapshot_complete?: boolean;
  kind?: "publish" | "backup" | "restore";
  restored_from_version?: number;
  note: string;
  stats: { nodes: number; blocks: number; relations?: number };
  packed_bytes?: number;
  raw_bytes?: number;
  created_by_name: string;
  created_at: string;
}

export interface Lock {
  pending: string[];
  via: string | null;
}

export type SubmissionStatus = "draft" | "submitted" | "in_review" | "graded" | "returned";

export interface CriterionGrade {
  criterion: string;
  met: boolean | null;
  comment: string;
  score?: number | null;
}

export interface Submission {
  id: string;
  user_id: string;
  user_name: string;
  track_id: string;
  node_id: string;
  node_title: string;
  block_id: string;
  block_type: string;
  block_title: string;
  attempt: number;
  status: SubmissionStatus;
  answer: { text?: string; code?: string; choice?: number };
  grading: null | {
    result: "approved" | "rejected" | "returned";
    feedback: string;
    criteria: CriterionGrade[];
    score?: number | null;
    graded_by_name: string;
    graded_at: string;
  };
  history?: { status: string; at: string; by_name: string; result?: string }[];
  reviewer_name?: string;
  orphaned?: boolean;
  submitted_at?: string | null;
  updated_at: string;
}

export interface StudyNote {
  id: string;
  node_id: string;
  block_id: string | null;
  track_id: string;
  body: string;
  version: number;
  deleted?: boolean;
  updated_at: string;
  node_title?: string;
  track_title?: string;
}

export interface Review {
  id: string;
  node_id: string;
  block_id: string | null;
  track_id: string;
  due_at: string;
  bucket: string;
  status: "pending" | "done" | "dismissed";
  note: string;
  review_count: number;
  last_reviewed_at: string | null;
  node_title?: string;
  track_title?: string;
}

export interface FieldChange {
  field: string;
  from: unknown;
  to: unknown;
}

export interface DiffItem {
  id: string;
  title: string;
  kind?: string;
  type?: string;
  parent?: string;
  node?: string;
  changes?: FieldChange[];
}

export interface DiffGroup {
  added: DiffItem[];
  removed: DiffItem[];
  changed: DiffItem[];
}

export interface CompareResult {
  base: string;
  target: string;
  track: FieldChange[];
  nodes: DiffGroup;
  blocks: DiffGroup;
  relations: DiffGroup;
  total_changes: number;
}
