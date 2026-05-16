export const SURVEY_URL = "https://forms.gle/4AYd2c97n37boVG49";

export const SURVEY_STORAGE_KEYS = {
  navCount: "km_survey_nav_count",
  dismissedAtCount: "km_survey_dismissed_at_count",
  permanentDismiss: "km_survey_permanent_dismiss",
} as const;

// 3回のページ遷移後に表示する
export const SURVEY_TRIGGER_COUNT = 3;

// 閉じた場合は6回のページ遷移後に再表示する
export const SURVEY_DISMISS_NAV_COUNT = 6;
