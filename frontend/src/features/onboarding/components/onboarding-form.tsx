"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { savePreferences } from "@/lib/storage/preferences-storage";
import { postOnboardingEvent } from "@/lib/api/analytics-api";
import {
  AGE_GROUP_OPTIONS,
  PARTY_OPTIONS,
  CATEGORY_OPTIONS,
} from "@/lib/constants/parties";
import { Button } from "@/components/ui/button";

// 番号付きバッジ（緑丸 + 白数字）
function NumberBadge({ n }: { n: number }) {
  return (
    <span
      className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
      style={{ backgroundColor: "var(--color-brand-primary)", color: "#ffffff" }}
      aria-hidden="true"
    >
      {n}
    </span>
  );
}

// オンボーディングフォーム（1画面縦スクロール）
// ステップ分割なし: 年代・支持政党・関心テーマを一度に表示する
export function OnboardingForm() {
  const router = useRouter();
  const [ageGroup, setAgeGroup] = useState<string | null>(null);
  const [supportedPartyId, setSupportedPartyId] = useState<string | null>(null);
  const [interestedCategoryIds, setInterestedCategoryIds] = useState<string[]>([]);

  // 1. オンボーディングを完了してホームへ遷移する
  const handleComplete = () => {
    savePreferences({
      ageGroup,
      supportedPartyId,
      interestedCategoryIds,
      onboardingCompleted: true,
    });

    const partyStatus =
      supportedPartyId === "none" || supportedPartyId === "other"
        ? "none"
        : supportedPartyId === "unknown"
          ? "unknown"
          : supportedPartyId === null
            ? "skipped"
            : "selected";

    void postOnboardingEvent({
      age_group: ageGroup,
      selected_party_id: partyStatus === "selected" ? supportedPartyId : null,
      selected_party_status: partyStatus,
      interest_category_ids: interestedCategoryIds,
    });

    router.push("/");
  };

  // 2. スキップしてホームへ遷移する
  const handleSkip = () => {
    savePreferences({ onboardingCompleted: true });
    router.push("/");
  };

  // 3. 関心テーマのトグル処理
  const toggleCategory = (id: string) => {
    setInterestedCategoryIds((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id],
    );
  };

  return (
    <div className="flex flex-col gap-8">
      {/* ① 年代 */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <NumberBadge n={1} />
          <h2
            className="text-base font-semibold"
            style={{ color: "var(--color-text-primary)" }}
          >
            年代を教えてください
          </h2>
          <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
            （任意です）
          </span>
        </div>
        <div className="flex flex-wrap gap-2">
          {AGE_GROUP_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => setAgeGroup(option.value)}
              className="px-4 py-2 rounded-full text-sm border transition-colors duration-150"
              style={{
                borderColor:
                  ageGroup === option.value
                    ? "var(--color-brand-primary)"
                    : "var(--color-border)",
                backgroundColor:
                  ageGroup === option.value ? "var(--color-brand-primary)" : "transparent",
                color:
                  ageGroup === option.value ? "#ffffff" : "var(--color-text-primary)",
              }}
            >
              {option.label}
            </button>
          ))}
        </div>
      </section>

      {/* ② 支持政党 */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <NumberBadge n={2} />
          <h2
            className="text-base font-semibold"
            style={{ color: "var(--color-text-primary)" }}
          >
            支持政党を教えてください
          </h2>
          <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
            （任意です）
          </span>
        </div>
        <div className="flex flex-wrap gap-2">
          {PARTY_OPTIONS.map((party) => (
            <button
              key={party.id}
              type="button"
              onClick={() => setSupportedPartyId(party.id)}
              className="px-4 py-2 rounded-full text-sm border transition-colors duration-150"
              style={{
                borderColor:
                  supportedPartyId === party.id
                    ? "var(--color-brand-primary)"
                    : "var(--color-border)",
                backgroundColor:
                  supportedPartyId === party.id
                    ? "var(--color-brand-primary)"
                    : "transparent",
                color:
                  supportedPartyId === party.id ? "#ffffff" : "var(--color-text-primary)",
              }}
            >
              {party.name}
            </button>
          ))}
        </div>
      </section>

      {/* ③ 関心テーマ */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <NumberBadge n={3} />
          <h2
            className="text-base font-semibold"
            style={{ color: "var(--color-text-primary)" }}
          >
            関心のあるテーマを教えてください
          </h2>
          <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
            （複数可）
          </span>
        </div>
        <div className="flex flex-wrap gap-2">
          {CATEGORY_OPTIONS.map((category) => {
            const isSelected = interestedCategoryIds.includes(category.id);
            return (
              <button
                key={category.id}
                type="button"
                onClick={() => toggleCategory(category.id)}
                className="px-4 py-2 rounded-full text-sm border transition-colors duration-150"
                style={{
                  borderColor: isSelected
                    ? "var(--color-brand-primary)"
                    : "var(--color-border)",
                  backgroundColor: isSelected
                    ? "var(--color-brand-primary)"
                    : "transparent",
                  color: isSelected ? "#ffffff" : "var(--color-text-primary)",
                }}
              >
                {category.name}
              </button>
            );
          })}
        </div>
      </section>

      {/* プライバシー注意書き（🔒 アイコン付き） */}
      <div
        className="flex gap-3 rounded-xl p-4"
        style={{ backgroundColor: "var(--color-bg-surface)" }}
      >
        <span className="flex-shrink-0 text-sm leading-5" aria-hidden="true">
          🔒
        </span>
        <p className="text-xs leading-relaxed" style={{ color: "var(--color-text-secondary)" }}>
          回答は端末内に保存され、表示内容の調整に使われます。また、サービス改善のため、個人を特定できない匿名の集計データとして利用する場合があります。
          <Link
            href="/about"
            className="ml-1 underline transition-opacity duration-150 hover:opacity-70"
            style={{ color: "var(--color-brand-primary)" }}
          >
            このアプリの考え方を見る
          </Link>
        </p>
      </div>

      {/* 操作ボタン */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={handleSkip}
          className="text-sm transition-opacity duration-150 hover:opacity-70"
          style={{ color: "var(--color-text-secondary)" }}
        >
          今はスキップする
        </button>
        <Button variant="primary" size="md" onClick={handleComplete}>
          はじめる
        </Button>
      </div>
    </div>
  );
}
