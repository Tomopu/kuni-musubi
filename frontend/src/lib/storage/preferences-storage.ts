import { PREFERENCES_STORAGE_KEY } from "@/lib/constants";

// ユーザー設定の型定義
export type UserPreferences = {
  ageGroup: string | null; // "10s" | "20s" | ... | "60s_plus" | "no_answer"
  supportedPartyId: string | null; // 政党 ID または "none" | "unknown" | "skipped"
  interestedCategoryIds: string[]; // カテゴリ ID の配列
  onboardingCompleted: boolean;
};

// デフォルト値
const DEFAULT_PREFERENCES: UserPreferences = {
  ageGroup: null,
  supportedPartyId: null,
  interestedCategoryIds: [],
  onboardingCompleted: false,
};

// 1. localStorage からユーザー設定を取得する
export function getPreferences(): UserPreferences {
  if (typeof window === "undefined") {
    return { ...DEFAULT_PREFERENCES };
  }
  try {
    const raw = localStorage.getItem(PREFERENCES_STORAGE_KEY);
    if (!raw) return { ...DEFAULT_PREFERENCES };
    const parsed = JSON.parse(raw) as Partial<UserPreferences>;
    return {
      ageGroup: parsed.ageGroup ?? null,
      supportedPartyId: parsed.supportedPartyId ?? null,
      interestedCategoryIds: Array.isArray(parsed.interestedCategoryIds)
        ? parsed.interestedCategoryIds
        : [],
      onboardingCompleted: parsed.onboardingCompleted ?? false,
    };
  } catch {
    return { ...DEFAULT_PREFERENCES };
  }
}

// 2. ユーザー設定を部分的に localStorage に保存する
export function savePreferences(prefs: Partial<UserPreferences>): void {
  if (typeof window === "undefined") return;
  try {
    const current = getPreferences();
    const updated: UserPreferences = { ...current, ...prefs };
    localStorage.setItem(PREFERENCES_STORAGE_KEY, JSON.stringify(updated));
  } catch {
    // localStorage が使用不可の場合は何もしない
  }
}

// 3. ユーザー設定をリセットする
export function resetPreferences(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(PREFERENCES_STORAGE_KEY);
  } catch {
    // localStorage が使用不可の場合は何もしない
  }
}

// 4. オンボーディング完了状態を確認する
export function hasCompletedOnboarding(): boolean {
  return getPreferences().onboardingCompleted;
}
