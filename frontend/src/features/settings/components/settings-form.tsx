"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import {
  LockKeyhole,
} from "lucide-react";
import {
  getPreferences,
  resetPreferences,
  savePreferences,
} from "@/lib/storage/preferences-storage";
import {
  AGE_GROUP_OPTIONS,
  PARTY_OPTIONS,
} from "@/lib/constants/parties";
import { getPartyColor } from "@/lib/constants/party-colors";
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

function NumberBadge({ n }: { n: number }) {
  return (
    <span className="onboarding-step__number" aria-hidden="true">
      {n}
    </span>
  );
}

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
    colorHex: getPartyColor(party.id),
  }));
}

// 設定フォームコンポーネント（Client Component）
// 現在の設定値が選択済み状態で表示され、変更は即時 localStorage に保存される
export function SettingsForm() {
  const router = useRouter();
  const [ageGroup, setAgeGroup] = useState<string | null>(null);
  const [supportedPartyId, setSupportedPartyId] = useState<string | null>(null);
  const [partyOptions, setPartyOptions] = useState<PartySelectOption[]>(fallbackPartyOptions);

  // 1. 初期値を localStorage から読み込む
  useEffect(() => {
    const prefs = getPreferences();
    setAgeGroup(prefs.ageGroup);
    setSupportedPartyId(prefs.supportedPartyId);
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

  // 4. オンボーディングをやり直す
  const handleRestartOnboarding = () => {
    savePreferences({ onboardingCompleted: false });
    router.push("/onboarding");
  };

  // 5. 設定をリセットする
  const handleReset = () => {
    resetPreferences();
    setAgeGroup(null);
    setSupportedPartyId(null);
  };

  return (
    <div className="onboarding-form settings-form">
      {/* 年代を変更 */}
      <section className="onboarding-step onboarding-step--age">
        <div className="onboarding-step__head">
          <NumberBadge n={1} />
          <h2>年代を変更</h2>
          <span>（任意です）</span>
        </div>
        <div className="chip-grid">
          {AGE_GROUP_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleAgeGroupChange(option.value)}
              className="chip-button onboarding-chip"
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
        <Image
          src="/assets/mascot/mascot-think.png"
          alt=""
          width={86}
          height={86}
          className="onboarding-step__mascot"
          aria-hidden="true"
        />
      </section>

      {/* 支持政党を変更 */}
      <section className="onboarding-step onboarding-step--party">
        <div className="onboarding-step__head">
          <NumberBadge n={2} />
          <h2>支持政党を変更</h2>
          <span>（任意です）</span>
        </div>
        <div className="chip-grid">
          {partyOptions.map((party) => {
            const isSelected = supportedPartyId === party.id;
            const dotColor = party.colorHex ?? "#999999";
            const hasDot = party.id !== "none" && party.id !== "unknown";
            return (
              <button
                key={party.id}
                type="button"
                onClick={() => handlePartyChange(party.id)}
                className={`chip-button onboarding-chip ${
                  party.name.length >= 12 ? "onboarding-chip--compact" : ""
                }`}
                style={{
                  borderColor: isSelected ? dotColor : "var(--color-border)",
                  backgroundColor: isSelected ? `${dotColor}14` : "#ffffff",
                  color: isSelected
                    ? "var(--color-text-primary)"
                    : "var(--color-text-secondary)",
                }}
              >
                {hasDot && (
                  <span
                    className="dot"
                    style={{ backgroundColor: dotColor }}
                  />
                )}
                {party.name}
              </button>
            );
          })}
        </div>
        <Image
          src="/assets/mascot/mascot-question.png"
          alt=""
          width={88}
          height={88}
          className="onboarding-step__mascot"
          aria-hidden="true"
        />
      </section>

      {/*
      関心テーマを変更
      <section className="onboarding-step onboarding-step--category">
        <div className="onboarding-step__head">
          <NumberBadge n={3} />
          <h2>関心テーマを変更</h2>
          <span>（複数可）</span>
        </div>
        <div className="chip-grid chip-grid--categories">
          {CATEGORY_OPTIONS.map((category, index) => {
            const isSelected = interestedCategoryIds.includes(category.id);
            const Icon = CATEGORY_ICONS[index % CATEGORY_ICONS.length];
            return (
              <button
                key={category.id}
                type="button"
                onClick={() => toggleCategory(category.id)}
                className="chip-button onboarding-chip"
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
                <Icon size={14} />
                {category.name}
              </button>
            );
          })}
        </div>
        <Image
          src="/assets/mascot/mascot-idea.png"
          alt=""
          width={86}
          height={86}
          className="onboarding-step__mascot"
          aria-hidden="true"
        />
      </section>
      */}

      <div className="privacy-note">
        <LockKeyhole size={20} />
        <p>
          回答は端末内に保存され、表示内容の調整に使われます。サーバーには送信されません。
          <Link
            href="/about"
            className="privacy-note__link"
          >
            このアプリの考え方を見る
          </Link>
        </p>
      </div>

      {/* その他の操作 */}
      <section className="settings-actions">
        <button
          type="button"
          onClick={handleRestartOnboarding}
          className="settings-actions__restart"
        >
          オンボーディングをやり直す
        </button>
        <button
          type="button"
          onClick={handleReset}
          className="settings-actions__reset"
        >
          設定をリセットする
        </button>
      </section>
    </div>
  );
}
