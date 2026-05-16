import {
  SURVEY_STORAGE_KEYS,
  SURVEY_DISMISS_NAV_COUNT,
} from "@/lib/constants/survey";

function safeGet(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function safeSet(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {}
}

export function getSurveyNavCount(): number {
  return Number(safeGet(SURVEY_STORAGE_KEYS.navCount) ?? "0");
}

export function incrementSurveyNavCount(): number {
  const next = getSurveyNavCount() + 1;
  safeSet(SURVEY_STORAGE_KEYS.navCount, String(next));
  return next;
}

export function isSurveyPermanentlyDismissed(): boolean {
  return safeGet(SURVEY_STORAGE_KEYS.permanentDismiss) === "true";
}

export function setSurveyPermanentDismiss(): void {
  safeSet(SURVEY_STORAGE_KEYS.permanentDismiss, "true");
}

export function isSurveyTemporarilyDismissed(): boolean {
  const dismissedAt = Number(safeGet(SURVEY_STORAGE_KEYS.dismissedAtCount) ?? "-1");
  if (dismissedAt < 0) return false;
  return getSurveyNavCount() - dismissedAt < SURVEY_DISMISS_NAV_COUNT;
}

export function setSurveyTemporaryDismiss(): void {
  safeSet(
    SURVEY_STORAGE_KEYS.dismissedAtCount,
    String(getSurveyNavCount()),
  );
}

// 遷移回数チェックを除いた表示可否判定（回数チェックは呼び出し側で行う）
export function shouldShowSurvey(): boolean {
  if (isSurveyPermanentlyDismissed()) return false;
  if (isSurveyTemporarilyDismissed()) return false;
  return true;
}
