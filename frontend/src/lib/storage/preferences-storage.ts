import { PREFERENCES_STORAGE_KEY } from "@/lib/constants";

export type UserPreference = {
  ageGroup: string | null;
  selectedPartyId: string | null;
  interestCategoryIds: string[];
  completedOnboarding: boolean;
};

const defaultPreferences: UserPreference = {
  ageGroup: null,
  selectedPartyId: null,
  interestCategoryIds: [],
  completedOnboarding: false,
};

export function loadPreferences(): UserPreference {
  if (typeof window === "undefined") return defaultPreferences;
  try {
    const raw = localStorage.getItem(PREFERENCES_STORAGE_KEY);
    if (!raw) return defaultPreferences;
    return { ...defaultPreferences, ...JSON.parse(raw) };
  } catch {
    return defaultPreferences;
  }
}

export function savePreferences(preferences: UserPreference): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(PREFERENCES_STORAGE_KEY, JSON.stringify(preferences));
}

export function clearPreferences(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(PREFERENCES_STORAGE_KEY);
}
