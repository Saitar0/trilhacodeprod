export const TYPED_ACTIVITY_KINDS = [
  "multiple_choice",
  "short_answer",
  "discursive",
  "matching",
  "ordering",
  "review",
] as const;

export type TypedActivityKind = (typeof TYPED_ACTIVITY_KINDS)[number];

export interface PublicActivityReference {
  kind: "internal" | "external" | "obsidian" | "editorial";
  label: string;
  target_ref?: string | null;
  url?: string | null;
  raw_text?: string | null;
}

export interface PublicActivityBase {
  activity_ref: string;
  version_ref: string;
  title: string;
  order: number;
  prompt: string;
  instructions?: string | null;
  references?: PublicActivityReference[];
}

export interface PublicOption {
  option_id: string;
  text: string;
}

export interface PublicActivityItem {
  ref: string;
  text: string;
}

export interface PublicMultipleChoiceActivity extends PublicActivityBase {
  type: "multiple_choice";
  options: PublicOption[];
}

export interface PublicShortAnswerActivity extends PublicActivityBase {
  type: "short_answer";
}

export interface PublicDiscursiveActivity extends PublicActivityBase {
  type: "discursive";
}

export interface PublicMatchingActivity extends PublicActivityBase {
  type: "matching";
  left_items: PublicActivityItem[];
  right_items: PublicActivityItem[];
}

export interface PublicOrderingActivity extends PublicActivityBase {
  type: "ordering";
  items: PublicActivityItem[];
}

export interface PublicReviewActivity extends PublicActivityBase {
  type: "review";
}

export type PublicTypedActivity =
  | PublicMultipleChoiceActivity
  | PublicShortAnswerActivity
  | PublicDiscursiveActivity
  | PublicMatchingActivity
  | PublicOrderingActivity
  | PublicReviewActivity;

const STABLE_ID = /^f(?:[1-9]|10)-[a-z0-9]+(?:-[a-z0-9]+)*$/;
const VERSION_REF = /^question-source-sha256:[0-9a-f]{64}$/;
const OPTION_ID = /^[a-z0-9]+(?:[-_][a-z0-9]+)*$/;
const MAX_SOURCE_TEXT_LENGTH = 100_000;
const BASE_KEYS = [
  "activity_ref",
  "version_ref",
  "title",
  "order",
  "prompt",
  "instructions",
  "references",
] as const;

export class ActivityValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ActivityValidationError";
  }
}

function asRecord(value: unknown, field: string): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new ActivityValidationError(field + " deve ser um objeto.");
  }
  return value as Record<string, unknown>;
}

function allowOnly(
  value: Record<string, unknown>,
  allowed: readonly string[],
  field: string,
): void {
  const unexpected = Object.keys(value).find((key) => !allowed.includes(key));
  if (unexpected) {
    throw new ActivityValidationError(
      field + " contém campo não permitido: " + unexpected + ".",
    );
  }
}

function requiredText(value: unknown, field: string): string {
  if (
    typeof value !== "string" ||
    value.trim().length === 0 ||
    value.length > MAX_SOURCE_TEXT_LENGTH
  ) {
    throw new ActivityValidationError(field + " deve conter texto válido.");
  }
  return value;
}

function optionalText(value: unknown, field: string): string | null | undefined {
  if (value === undefined || value === null) return value;
  if (typeof value !== "string" || value.length > MAX_SOURCE_TEXT_LENGTH) {
    throw new ActivityValidationError(field + " deve ser texto.");
  }
  return value;
}

function assertStableId(value: unknown, field: string): string {
  const text = requiredText(value, field);
  if (!STABLE_ID.test(text)) {
    throw new ActivityValidationError(field + " não é um ID curricular estável.");
  }
  return text;
}

function parseReference(value: unknown, index: number): PublicActivityReference {
  const field = "references[" + index + "]";
  const record = asRecord(value, field);
  allowOnly(record, ["kind", "label", "target_ref", "url", "raw_text"], field);
  const kind = record.kind;
  if (
    kind !== "internal" &&
    kind !== "external" &&
    kind !== "obsidian" &&
    kind !== "editorial"
  ) {
    throw new ActivityValidationError(field + ".kind é inválido.");
  }

  const label = requiredText(record.label, field + ".label");
  const targetRef = optionalText(record.target_ref, field + ".target_ref");
  const url = optionalText(record.url, field + ".url");
  const rawText = optionalText(record.raw_text, field + ".raw_text");

  if (targetRef && !STABLE_ID.test(targetRef)) {
    throw new ActivityValidationError(field + ".target_ref é inválido.");
  }
  if (kind === "internal" && !targetRef) {
    throw new ActivityValidationError(field + " interno exige target_ref.");
  }
  if (kind !== "internal" && targetRef !== undefined && targetRef !== null) {
    throw new ActivityValidationError(field + " não interno não aceita target_ref.");
  }
  if (kind === "external") {
    if (!url) throw new ActivityValidationError(field + " externo exige URL.");
    try {
      const parsedUrl = new URL(url);
      if (parsedUrl.protocol !== "http:" && parsedUrl.protocol !== "https:") {
        throw new Error("protocol");
      }
    } catch {
      throw new ActivityValidationError(field + ".url deve usar HTTP ou HTTPS.");
    }
  } else if (url !== undefined && url !== null) {
    throw new ActivityValidationError(field + " não externo não aceita URL.");
  }
  if ((kind === "obsidian" || kind === "editorial") && !rawText) {
    throw new ActivityValidationError(field + " exige raw_text.");
  }

  return {
    kind,
    label,
    ...(targetRef !== undefined ? { target_ref: targetRef } : {}),
    ...(url !== undefined ? { url } : {}),
    ...(rawText !== undefined ? { raw_text: rawText } : {}),
  };
}

function parseReferences(value: unknown): PublicActivityReference[] | undefined {
  if (value === undefined) return undefined;
  if (!Array.isArray(value)) {
    throw new ActivityValidationError("references deve ser uma lista.");
  }
  return value.map((item, index) => parseReference(item, index));
}

function parseItems(value: unknown, field: string): PublicActivityItem[] {
  if (!Array.isArray(value) || value.length > 100) {
    throw new ActivityValidationError(field + " deve ser uma lista válida.");
  }
  const items = value.map((item, index) => {
    const itemField = field + "[" + index + "]";
    const record = asRecord(item, itemField);
    allowOnly(record, ["ref", "text"], itemField);
    return {
      ref: requiredText(record.ref, itemField + ".ref"),
      text: requiredText(record.text, itemField + ".text"),
    };
  });
  const refs = items.map((item) => item.ref);
  if (new Set(refs).size !== refs.length) {
    throw new ActivityValidationError(field + " contém referências duplicadas.");
  }
  return items;
}

function parseBase(record: Record<string, unknown>): PublicActivityBase {
  const activityRef = assertStableId(record.activity_ref, "activity_ref");
  const versionRef = requiredText(record.version_ref, "version_ref");
  if (!VERSION_REF.test(versionRef)) {
    throw new ActivityValidationError("version_ref possui formato inválido.");
  }
  if (
    typeof record.order !== "number" ||
    !Number.isInteger(record.order) ||
    record.order < 0
  ) {
    throw new ActivityValidationError("order deve ser um inteiro não negativo.");
  }

  const instructions = optionalText(record.instructions, "instructions");
  return {
    activity_ref: activityRef,
    version_ref: versionRef,
    title: requiredText(record.title, "title"),
    order: record.order,
    prompt: requiredText(record.prompt, "prompt"),
    ...(instructions !== undefined ? { instructions } : {}),
    ...(record.references !== undefined
      ? { references: parseReferences(record.references) }
      : {}),
  };
}

/** Validates and copies only the student-facing allowlist. */
export function parsePublicTypedActivity(value: unknown): PublicTypedActivity {
  const record = asRecord(value, "activity");
  const rawType = record.type;
  if (
    typeof rawType !== "string" ||
    !TYPED_ACTIVITY_KINDS.includes(rawType as TypedActivityKind)
  ) {
    throw new ActivityValidationError("Tipo de atividade desconhecido.");
  }
  const type = rawType as TypedActivityKind;

  const typeKeys: Record<TypedActivityKind, readonly string[]> = {
    multiple_choice: ["options"],
    short_answer: [],
    discursive: [],
    matching: ["left_items", "right_items"],
    ordering: ["items"],
    review: [],
  };
  allowOnly(record, [...BASE_KEYS, "type", ...typeKeys[type]], "activity");
  const base = parseBase(record);

  switch (type) {
    case "multiple_choice": {
      if (
        !Array.isArray(record.options) ||
        record.options.length < 2 ||
        record.options.length > 100
      ) {
        throw new ActivityValidationError(
          "Múltipla escolha exige de 2 a 100 alternativas.",
        );
      }
      const options = record.options.map((item, index) => {
        const field = "options[" + index + "]";
        const option = asRecord(item, field);
        allowOnly(option, ["option_id", "text"], field);
        return {
          option_id: requiredText(option.option_id, field + ".option_id"),
          text: requiredText(option.text, field + ".text"),
        };
      });
      const ids = options.map((option) => option.option_id);
      if (new Set(ids).size !== ids.length) {
        throw new ActivityValidationError("As alternativas possuem IDs duplicados.");
      }
      return { ...base, type, options };
    }
    case "short_answer":
      return { ...base, type };
    case "discursive":
      return { ...base, type };
    case "matching":
      return {
        ...base,
        type,
        left_items: parseItems(record.left_items, "left_items"),
        right_items: parseItems(record.right_items, "right_items"),
      };
    case "ordering":
      return { ...base, type, items: parseItems(record.items, "items") };
    case "review":
      return { ...base, type };
  }
}

export function isPublicTypedActivity(value: unknown): value is PublicTypedActivity {
  try {
    parsePublicTypedActivity(value);
    return true;
  } catch {
    return false;
  }
}