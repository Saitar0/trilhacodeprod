export function isQuizApiEnabled(value: string | undefined = import.meta.env.VITE_QUIZ_API_ENABLED): boolean {
  return value === "true";
}

export type QuizBlockMode = "legacy" | "api" | "hidden" | "unavailable";

export function quizBlockMode(
  blockType: string,
  blockId: string,
  apiEnabled: boolean,
  apiAnchorId: string | null,
): QuizBlockMode {
  if (blockType !== "quiz") return "legacy";
  if (!apiEnabled) return blockId === apiAnchorId ? "unavailable" : "hidden";
  return blockId === apiAnchorId ? "api" : "hidden";
}
