import { API_BASE_URL } from "@/lib/constants";

export type OnboardingEventPayload = {
  age_group: string | null;
  selected_party_id: string | null;
  interest_category_ids: string[];
};

export type ArticleEventPayload = {
  event_type: "impression" | "click" | "detail_view" | "helpful_click";
  article_id: string;
  surface: "home" | "party" | "category";
};

export async function postOnboardingEvent(
  payload: OnboardingEventPayload
): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/analytics/onboarding`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok)
    throw new Error(`POST /analytics/onboarding failed: ${res.status}`);
}

export async function postArticleEvent(
  payload: ArticleEventPayload
): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/analytics/article-event`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok)
    throw new Error(`POST /analytics/article-event failed: ${res.status}`);
}
