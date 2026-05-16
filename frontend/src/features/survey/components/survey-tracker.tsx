"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { incrementSurveyNavCount, shouldShowSurvey } from "@/lib/storage/survey";
import { SURVEY_TRIGGER_COUNT } from "@/lib/constants/survey";
import { SurveyPopup } from "./survey-popup";

export function SurveyTracker() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // 1. ページ遷移をカウントする
    const count = incrementSurveyNavCount();
    // 2. 表示条件を確認する（既に開いている場合は重複表示しない）
    if (!isOpen && count >= SURVEY_TRIGGER_COUNT && shouldShowSurvey()) {
      // 3. 少し間を置いてポップアップを表示する
      const timer = setTimeout(() => setIsOpen(true), 800);
      return () => clearTimeout(timer);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname]);

  if (!isOpen) return null;
  return <SurveyPopup onClose={() => setIsOpen(false)} />;
}
