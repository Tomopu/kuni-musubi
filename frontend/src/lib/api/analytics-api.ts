import { API_BASE_URL } from "@/lib/constants";

// オンボーディングイベントのペイロード（backend スキーマに合わせる）
export type OnboardingEventPayload = {
  age_group: string | null;
  selected_party_id: string | null;
  selected_party_status: "none" | "unknown" | "skipped" | "selected" | null;
  interest_category_ids: string[];
};

// 記事イベントのペイロード（backend スキーマに合わせる）
export type ArticleEventPayload = {
  event_type: "card_click" | "detail_view" | "helpful_click" | "source_click";
  article_id: string;
  surface: "home" | "party_tab" | "party_detail" | "article_detail";
};

// 1. オンボーディングイベントを送信する（失敗しても UX を壊さない）
export async function postOnboardingEvent(
  payload: OnboardingEventPayload,
): Promise<void> {
  try {
    const res = await fetch(`${API_BASE_URL}/analytics/onboarding`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      console.warn(`POST /analytics/onboarding failed: ${res.status}`);
    }
  } catch (err) {
    console.warn("Failed to post onboarding event:", err);
  }
}

// 2. 記事イベントを送信する（失敗しても UX を壊さない）
export async function postArticleEvent(
  payload: ArticleEventPayload,
): Promise<void> {
  try {
    const res = await fetch(`${API_BASE_URL}/analytics/article-event`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      console.warn(`POST /analytics/article-event failed: ${res.status}`);
    }
  } catch (err) {
    console.warn("Failed to post article event:", err);
  }
}
