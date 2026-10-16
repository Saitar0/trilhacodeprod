import type { Review } from "@/types";

export function groupReviews(items: Review[]) {
  const end = new Date();
  end.setHours(23, 59, 59, 999);
  const start = new Date();
  start.setHours(0, 0, 0, 0);
  return {
    overdue: items.filter((review) => new Date(review.due_at) < start),
    today: items.filter((review) => new Date(review.due_at) >= start && new Date(review.due_at) <= end),
    upcoming: items.filter((review) => new Date(review.due_at) > end),
  };
}
