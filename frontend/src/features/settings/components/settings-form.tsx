"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  getPreferences,
  savePreferences,
  resetPreferences,
} from "@/lib/storage/preferences-storage";
import {
  AGE_GROUP_OPTIONS,
  PARTY_OPTIONS,
  CATEGORY_OPTIONS,
} from "@/lib/constants/parties";
import { listParties, type PartyResponse } from "@/lib/api/parties-api";

type PartySelectOption = {
  id: string;
  name: string;
  shortName: string;
  colorHex: string | null;
};

const DEFAULT_PARTY_OPTIONS: PartySelectOption[] = [
  { id: "none", name: "特になし", shortName: "なし", colorHex: "#999999" },
  { id: "unknown", name: "わからない", shortName: "?", colorHex: "#999999" },
];

function toPartyOptions(parties: PartyResponse[]): PartySelectOption[] {
  return [
    ...DEFAULT_PARTY_OPTIONS,
    ...parties.map((party) => ({
      id: party.id,
      name: party.name,
      shortName: party.short_name,
      colorHex: party.color_hex,
    })),
  ];
}

function fallbackPartyOptions(): PartySelectOption[] {
  return PARTY_OPTIONS.map((party) => ({
    id: party.id,
    name: party.name,
    shortName: party.shortName,
    colorHex: null,
  }));
}

// 設定フォームコンポーネント（Client Component）
// 現在の設定値が選択済み状態で表示され、変更は即時 localStorage に保存される
export function SettingsForm() {
  const router = useRouter();
  const [ageGroup, setAgeGroup] = useState<string | null>(null);
  const [supportedPartyId, setSupportedPartyId] = useState<string | null>(null);
  const [interestedCategoryIds, setInterestedCategoryIds] = useState<string[]>([]);
  const [partyOptions, setPartyOptions] = useState<PartySelectOption[]>(fallbackPartyOptions);

  // 1. 初期値を localStorage から読み込む
  useEffect(() => {
    const prefs = getPreferences();
    setAgeGroup(prefs.ageGroup);
    setSupportedPartyId(prefs.supportedPartyId);
    setInterestedCategoryIds(prefs.interestedCategoryIds);
  }, []);

  useEffect(() => {
    let cancelled = false;
    void listParties()
      .then((parties) => {
        if (!cancelled) setPartyOptions(toPartyOptions(parties));
      })
      .catch(() => {
        if (!cancelled) setPartyOptions(fallbackPartyOptions());
      });

    return () => {
      cancelled = true;
    };
  }, []);

  // 2. 年代を変更する（即時保存）
  const handleAgeGroupChange = (value: string) => {
    setAgeGroup(value);
    savePreferences({ ageGroup: value });
  };

  // 3. 支持政党を変更する（即時保存）
  const handlePartyChange = (value: string) => {
    setSupportedPartyId(value);
    savePreferences({ supportedPartyId: value });
  };

  // 4. 関心テーマをトグルする（即時保存）
  const toggleCategory = (id: string) => {
    const updated = interestedCategoryIds.includes(id)
      ? interestedCategoryIds.filter((c) => c !== id)
      : [...interestedCategoryIds, id];
    setInterestedCategoryIds(updated);
    savePreferences({ interestedCategoryIds: updated });
  };

  // 5. オンボーディングをやり直す
  const handleRestartOnboarding = () => {
    savePreferences({ onboardingCompleted: false });
    router.push("/onboarding");
  };

  // 6. 設定をリセットする
  const handleReset = () => {
    resetPreferences();
    setAgeGroup(null);
    setSupportedPartyId(null);
    setInterestedCategoryIds([]);
  };

  return (
    <div className="flex flex-col gap-8">
      {/* 年代を変更 */}
      <section>
        <h2
          className="text-base font-medium mb-0.5"
          style={{ color: "var(--color-text-primary)" }}
        >
          年代を変更
        </h2>
        <p
          className="text-xs mb-3"
          style={{ color: "var(--color-text-secondary)" }}
        >
          表示内容のカスタマイズに使われます（任意）
        </p>
        <div className="flex flex-wrap gap-2">
          {AGE_GROUP_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleAgeGroupChange(option.value)}
              className="px-4 py-2 rounded-full text-sm border transition-colors duration-150"
              style={{
                borderColor:
                  ageGroup === option.value
                    ? "var(--color-brand-primary)"
                    : "var(--color-border)",
                backgroundColor:
                  ageGroup === option.value
                    ? "var(--color-brand-primary)"
                    : "transparent",
                color:
                  ageGroup === option.value
                    ? "#ffffff"
                    : "var(--color-text-primary)",
              }}
            >
              {option.label}
            </button>
          ))}
        </div>
      </section>

      {/* 支持政党を変更 */}
      <section>
        <h2
          className="text-base font-medium mb-0.5"
          style={{ color: "var(--color-text-primary)" }}
        >
          支持政党を変更
        </h2>
        <p
          className="text-xs mb-3"
          style={{ color: "var(--color-text-secondary)" }}
        >
          支持政党の Good News がホームに表示されます（任意）
        </p>
        <div className="flex flex-wrap gap-2">
          {partyOptions.map((party) => {
            const isSelected = supportedPartyId === party.id;
            const dotColor = party.colorHex ?? "#999999";
            const hasDot = party.id !== "none" && party.id !== "unknown";
            return (
              <button
                key={party.id}
                type="button"
                onClick={() => handlePartyChange(party.id)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-full text-sm border transition-colors duration-150"
                style={{
                  borderColor: isSelected ? "var(--color-brand-primary)" : "var(--color-border)",
                  backgroundColor: isSelected ? "var(--color-brand-primary)" : "transparent",
                  color: isSelected ? "#ffffff" : "var(--color-text-primary)",
                }}
              >
                {hasDot && (
                  <span
                    className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: isSelected ? "rgba(255,255,255,0.8)" : dotColor }}
                  />
                )}
                {party.name}
              </button>
            );
          })}
        </div>
      </section>

      {/* 関心テーマを変更 */}
      <section>
        <h2
          className="text-base font-medium mb-0.5"
          style={{ color: "var(--color-text-primary)" }}
        >
          関心テーマを変更
        </h2>
        <p
          className="text-xs mb-3"
          style={{ color: "var(--color-text-secondary)" }}
        >
          複数選択できます（任意）
        </p>
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

      {/* プライバシー注意書き（🔒 アイコン付きボックス） */}
      <div
        className="flex gap-3 rounded-xl p-4"
        style={{ backgroundColor: "var(--color-bg-surface)" }}
      >
        <span className="flex-shrink-0 text-sm leading-5" aria-hidden="true">
          🔒
        </span>
        <p
          className="text-xs leading-relaxed"
          style={{ color: "var(--color-text-secondary)" }}
        >
          回答は端末内に保存され、表示内容の調整に使われます。サーバーには送信されません。
          <Link
            href="/about"
            className="ml-1 underline transition-opacity duration-150 hover:opacity-70"
            style={{ color: "var(--color-brand-primary)" }}
          >
            このアプリの考え方を見る
          </Link>
        </p>
      </div>

      {/* その他の操作 */}
      <section
        className="border-t pt-6 flex flex-col gap-3"
        style={{ borderColor: "var(--color-border)" }}
      >
        <button
          type="button"
          onClick={handleRestartOnboarding}
          className="text-sm text-left transition-opacity duration-150 hover:opacity-70"
          style={{ color: "var(--color-brand-primary)" }}
        >
          オンボーディングをやり直す
        </button>
        <button
          type="button"
          onClick={handleReset}
          className="text-sm text-left transition-opacity duration-150 hover:opacity-70"
          style={{ color: "var(--color-text-secondary)" }}
        >
          設定をリセットする
        </button>
      </section>
    </div>
  );
}
